import pandas as pd
import requests
from datetime import datetime
import time
import logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import re  # for normalization

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load filtered series names
try:
    with open('data/raw/filtered_series_names.txt', 'r') as file:
        filtered_series_names = [line.strip() for line in file.readlines()]
    print(f"Loaded {len(filtered_series_names)} filtered series names.")
except FileNotFoundError:
    print("Error: filtered_series_names.txt not found.")
    filtered_series_names = []

# Load and process metadata
try:
    metadata_df = pd.read_csv('data/raw/wdi_metadata.csv', encoding='latin1', on_bad_lines='skip')
    metadata_df = metadata_df.dropna(subset=['Code'])
    # Normalize Indicator Name: lowercase, strip, remove punctuation
    metadata_df['Name Norm'] = (
        metadata_df['Indicator Name'].astype(str)
        .str.strip().str.lower()
        .apply(lambda x: re.sub(r"[^\w\s]", "", x))
    )
    # Build normalized mapping
    norm_mapping = dict(zip(metadata_df['Name Norm'], metadata_df['Code']))
    # Normalize filtered names
    filtered_norm = [re.sub(r"[^\w\s]", "", name.strip().lower()) for name in filtered_series_names]
    # Map normalized names to codes
    desired_series_codes = [norm_mapping[n] for n in filtered_norm if n in norm_mapping]
    # Determine unmatched
    final_unmatched = [orig for orig, n in zip(filtered_series_names, filtered_norm) if n not in norm_mapping]
    if final_unmatched:
        print(f"Final unmatched entries after normalization: {final_unmatched}")
    desired_series_codes = list(set(desired_series_codes))
    print(f"Mapped {len(desired_series_codes)} series names to codes.")
except FileNotFoundError:
    print("Error: wdi_metadata.csv not found.")
    desired_series_codes = []
except Exception as e:
    print(f"Error processing metadata: {e}")
    desired_series_codes = []

# Validate series codes
valid_series_codes = [code for code in desired_series_codes if isinstance(code, str) and code.strip() and len(code) <= 20]
if not valid_series_codes:
    print("Error: No valid series codes found.")
    exit()

def load_partial_data(temp_file):
    try:
        with open(temp_file, 'r') as temp:
            partial_data = json.load(temp)
            logging.info(f"Loaded {len(partial_data)} records from {temp_file}.")
            return partial_data
    except FileNotFoundError:
        logging.info(f"No partial data found in {temp_file}. Starting fresh.")
        return []
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {temp_file}. Starting fresh.")
        return []

def fetch_data_with_session(indicators, countries, date_range, temp_file, batch_size=20):
    base_url = "http://api.worldbank.org/v2/country/{}/indicator/{}?date={}:{}&format=json"
    all_data = load_partial_data(temp_file)
    processed_indicators = set(record['indicator'] for record in all_data if 'indicator' in record)
    remaining_indicators = [indicator for indicator in indicators if indicator not in processed_indicators]
    batches = [remaining_indicators[i:i + batch_size] for i in range(0, len(remaining_indicators), batch_size)]
    def fetch_indicator_data(indicator, country):
        url = base_url.format(country, indicator, date_range[0].year, date_range[1].year)
        logging.info(f"Fetching data for indicator '{indicator}' in country '{country}'. URL: {url}")
        for attempt in range(3):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                logging.debug(f"Raw response content: {response.content}")
                data = response.json()
                logging.debug(f"Parsed data: {data}")
                if len(data) > 1 and isinstance(data[1], list):
                    valid_entries = []
                    for entry in data[1]:
                        if 'value' in entry and entry['value'] is not None:
                            entry['indicator'] = indicator
                            valid_entries.append(entry)
                        else:
                            logging.warning(f"Missing 'value' for indicator '{indicator}' in country '{country}' on date '{entry.get('date', 'unknown')}'.")
                    return valid_entries
                else:
                    logging.warning(f"No valid data found for indicator '{indicator}' in country '{country}'.")
                    return []
            except requests.exceptions.RequestException as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)
        logging.error(f"Failed to fetch data for indicator '{indicator}' in country '{country}' after 3 attempts.")
        return []
    for batch_index, batch in enumerate(batches):
        logging.info(f"Processing batch {batch_index + 1}/{len(batches)} with {len(batch)} indicators.")
        batch_data = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_indicator = {
                executor.submit(fetch_indicator_data, indicator, country): (indicator, country)
                for indicator in batch for country in countries
            }
            for future in as_completed(future_to_indicator):
                indicator, country = future_to_indicator[future]
                try:
                    result = future.result()
                    batch_data.extend(result)
                except Exception as e:
                    logging.error(f"Error processing indicator '{indicator}' for country '{country}': {e}")
        if batch_data:
            all_data.extend(batch_data)
            with open(temp_file, 'w') as temp:
                json.dump(all_data, temp)
            logging.info(f"Saved partial data after processing batch {batch_index + 1} to {temp_file}.")
    logging.info("Finished processing all batches.")
    return all_data

if __name__ == "__main__":
    temp_file = 'data/raw/temp_data.json'
    countries = [
        'AFG', 'ALB', 'DZA', 'AGO', 'ATG', 'ARG', 'ARM', 'AUS', 'AUT', 'AZE', 'BHS', 'BHR', 'BGD', 'BRB', 'BLR', 'BEL', 'BLZ', 'BEN', 'BTN', 'BOL', 'BIH', 'BWA', 'BRA', 'BRN', 'BGR', 'BFA', 'BDI', 'CPV', 'KHM', 'CMR', 'CAN', 'CAF', 'TCD', 'CHL', 'CHN', 'COL', 'COM', 'COG', 'COD', 'CRI', 'HRV', 'CUB', 'CYP', 'CZE', 'DNK', 'DJI', 'DOM', 'ECU', 'EGY', 'SLV', 'GNQ', 'ERI', 'EST', 'SWZ', 'ETH', 'FJI', 'FIN', 'FRA', 'GAB', 'GMB', 'GEO', 'DEU', 'GHA', 'GRC', 'GRD', 'GTM', 'GIN', 'GNB', 'GUY', 'HTI', 'HND', 'HUN', 'ISL', 'IND', 'IDN', 'IRN', 'IRQ', 'IRL', 'ISR', 'ITA', 'JAM', 'JPN', 'JOR', 'KAZ', 'KEN', 'KIR', 'KOR', 'KWT', 'KGZ', 'LAO', 'LVA', 'LBN', 'LSO', 'LBR', 'LBY', 'LTU', 'LUX', 'MDG', 'MWI', 'MYS', 'MDV', 'MLI', 'MLT', 'MRT', 'MUS', 'MEX', 'FSM', 'MDA', 'MNG', 'MNE', 'MAR', 'MOZ', 'MMR', 'NAM', 'NPL', 'NLD', 'NZL', 'NIC', 'NER', 'NGA', 'MKD', 'NOR', 'OMN', 'PAK', 'PAN', 'PNG', 'PRY', 'PER', 'PHL', 'POL', 'PRT', 'PRI', 'QAT', 'ROU', 'RUS', 'RWA', 'VCT', 'LCA', 'STP', 'SAU', 'SEN', 'SRB', 'SYC', 'SLE', 'SGP', 'SVK', 'SVN', 'SLB', 'SOM', 'ZAF', 'SSD', 'ESP', 'LKA', 'SDN', 'SUR', 'SWE', 'CHE', 'SYR', 'TJK', 'TZA', 'THA', 'TLS', 'TGO', 'TON', 'TTO', 'TUN', 'TUR', 'TKM', 'UGA', 'UKR', 'ARE', 'GBR', 'USA', 'URY', 'UZB', 'VUT', 'VEN', 'VNM', 'PSE', 'WSM', 'YEM', 'ZMB', 'ZWE'
    ]
    date_range = (datetime(2000, 1, 1), datetime(2021, 12, 31))
    combined_data = fetch_data_with_session(valid_series_codes, countries, date_range, temp_file)
    if combined_data:
        df_wdi = pd.DataFrame(combined_data)
        df_wdi['country_id'] = df_wdi['country'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
        df_wdi['country_name'] = df_wdi['country'].apply(lambda x: x.get('value') if isinstance(x, dict) else None)
        df_wdi.drop(columns=['country'], inplace=True)
        df_wdi.drop(columns=['unit', 'obs_status', 'decimal'], inplace=True)
        df_wdi = df_wdi.dropna(subset=['value'])
        df_wdi.to_csv('data/raw/wdi_data.csv', index=False)
        logging.info("Download successful! All data saved to CSV.")
    else:
        logging.warning("No data downloaded.")
    # Force fetching data for specific countries by bypassing processed indicators
    additional_countries = ['CIV', 'PRK']
    logging.info(f"Forcing data fetch for countries: {additional_countries}")
    combined_data = fetch_data_with_session(valid_series_codes, additional_countries, date_range, 'data/raw/temp_civ_prk_data.json')
    if combined_data:
        df_wdi = pd.DataFrame(combined_data)
        df_wdi['country_id'] = df_wdi['country'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
        df_wdi['country_name'] = df_wdi['country'].apply(lambda x: x.get('value') if isinstance(x, dict) else None)
        df_wdi.drop(columns=['country'], inplace=True)
        df_wdi.drop(columns=['unit', 'obs_status', 'decimal'], inplace=True)
        df_wdi = df_wdi.dropna(subset=['value'])
        df_wdi.to_csv('data/raw/wdi_civ_prk_data.csv', index=False)
        logging.info("Saved CIV/PRK data to CSV.")
    else:
        logging.warning("No additional data downloaded for forced countries.")
