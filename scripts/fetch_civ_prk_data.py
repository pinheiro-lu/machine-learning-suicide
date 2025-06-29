import pandas as pd
import requests
from datetime import datetime
import time
import logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import unicodedata
import string
import re  # for normalization

# Configure logging to show warnings and errors only
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_data_for_countries(indicators, countries, date_range, temp_file):
    base_url = "http://api.worldbank.org/v2/country/{}/indicator/{}?date={}:{}&format=json"
    all_data = []

    def fetch_indicator_data(indicator, country):
        url = base_url.format(country, indicator, date_range[0].year, date_range[1].year)
        logging.info(f"Fetching data for indicator '{indicator}' in country '{country}'. URL: {url}")
        for attempt in range(3):  # Retry up to 3 times
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                if len(data) > 1 and isinstance(data[1], list):
                    valid_entries = []
                    for entry in data[1]:
                        if 'value' in entry and entry['value'] is not None:
                            entry['indicator'] = indicator
                            valid_entries.append(entry)
                    return valid_entries
                else:
                    logging.warning(f"No valid data found for indicator '{indicator}' in country '{country}'.")
                    return []
            except requests.exceptions.RequestException as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
        logging.error(f"Failed to fetch data for indicator '{indicator}' in country '{country}' after 3 attempts.")
        return []

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_indicator = {
            executor.submit(fetch_indicator_data, indicator, country): (indicator, country)
            for indicator in indicators for country in countries
        }
        for future in as_completed(future_to_indicator):
            indicator, country = future_to_indicator[future]
            try:
                result = future.result()
                all_data.extend(result)
            except Exception as e:
                logging.error(f"Error processing indicator '{indicator}' for country '{country}': {e}")

    # Save data to temporary file
    if all_data:
        with open(temp_file, 'w') as temp:
            json.dump(all_data, temp)
        logging.info(f"Saved data for countries {countries} to {temp_file}.")
    return all_data

# Main function
try:
    temp_file = 'datasets/temp_civ_prk_data.json'
    countries = ['CIV', 'PRK']
    date_range = (datetime(2000, 1, 1), datetime(2021, 12, 31))

    # Load filtered series names
    try:
        with open('filtered_series_names.txt', 'r') as file:
            filtered_series_names = [line.strip() for line in file.readlines()]
        logging.info(f"Loaded {len(filtered_series_names)} filtered series names.")
    except FileNotFoundError:
        logging.error("Error: filtered_series_names.txt not found.")
        filtered_series_names = []

    # Load and process metadata
    try:
        metadata_df = pd.read_csv('datasets/wdi_metadata.csv', encoding='latin1', on_bad_lines='skip')
        metadata_df = metadata_df.dropna(subset=['Code'])
        # Normalize Indicator Name by removing punctuation and case
        metadata_df['Indicator Norm'] = (
            metadata_df['Indicator Name'].astype(str)
            .str.strip()
            .str.lower()
            .apply(lambda x: re.sub(r"[^\w\s]", "", x))
        )
        # Prepare normalized filtered series names
        filtered_norm = [re.sub(r"[^\w\s]", "", name.strip().lower())
                         for name in filtered_series_names]
        # Map normalized names to codes
        metadata_mapping = dict(zip(metadata_df['Indicator Norm'], metadata_df['Code']))
        # Filter and collect valid codes
        valid_series_codes = []
        matched_norms = set()
        for orig, norm in zip(filtered_series_names, filtered_norm):
            if norm in metadata_mapping:
                valid_series_codes.append(metadata_mapping[norm])
                matched_norms.add(norm)
        logging.info(f"Mapped {len(valid_series_codes)} series names to codes.")
    except FileNotFoundError:
        logging.error("Error: wdi_metadata.csv not found.")
        valid_series_codes = []
    except Exception as e:
        logging.error(f"Error processing metadata: {e}")
        valid_series_codes = []

    # Prepare unmatched entries based on normalization
    unmatched_entries = [name for name, norm in zip(filtered_series_names, filtered_norm)
                         if norm not in metadata_mapping]

    # DEBUG: Print the first 10 valid_series_codes and filtered_series_names
    print('DEBUG: First 10 valid_series_codes:', valid_series_codes[:10])
    print('DEBUG: First 10 filtered_series_names:', filtered_series_names[:10])
    # DEBUG: Print any entries in valid_series_codes that are not short codes (i.e., are long descriptions)
    for code in valid_series_codes:
        if len(code) > 30:
            print('DEBUG: Suspiciously long code:', code)

    # Check if all series names were successfully mapped to codes
    if len(valid_series_codes) == len(filtered_series_names):
        logging.info("All series names were successfully mapped to codes.")
    else:
        logging.warning(f"Only {len(valid_series_codes)} out of {len(filtered_series_names)} series names were mapped to codes.")
        if unmatched_entries:
            logging.warning(f"Unmatched entries: {unmatched_entries}")

    # Verify if filtered_series_names has more series names than valid_series_codes has codes
    unmatched_entries = [name for name in filtered_series_names if name not in metadata_mapping]
    if len(filtered_series_names) > len(valid_series_codes):
        logging.warning(f"Filtered series names ({len(filtered_series_names)}) exceed valid series codes ({len(valid_series_codes)}). Unmatched entries: {unmatched_entries}")
    else:
        logging.info("Filtered series names and valid series codes are consistent.")

    combined_data = fetch_data_for_countries(valid_series_codes, countries, date_range, temp_file)

    if combined_data:
        df_wdi = pd.DataFrame(combined_data)
        # Parse country field into separate columns
        df_wdi['country_id'] = df_wdi['country'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
        df_wdi['country_name'] = df_wdi['country'].apply(lambda x: x.get('value') if isinstance(x, dict) else None)
        df_wdi.drop(columns=['country'], inplace=True)
        # Remove unnecessary columns
        df_wdi.drop(columns=['unit', 'obs_status', 'decimal'], inplace=True)
        # Drop rows with missing values
        df_wdi = df_wdi.dropna(subset=['value'])
        df_wdi.to_csv('datasets/wdi_civ_prk_data.csv', index=False)
        logging.info("Download successful! Data saved to CSV.")
    else:
        logging.warning("No data downloaded.")
except Exception as e:
    logging.error(f"Error during data download: {e}")
