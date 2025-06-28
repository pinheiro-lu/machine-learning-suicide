import pandas as pd
import wbdata
from datetime import datetime
import time

# Load filtered series names
try:
    with open('filtered_series_names.txt', 'r') as file:
        filtered_series_names = [line.strip() for line in file.readlines()]
    print(f"Loaded {len(filtered_series_names)} filtered series names.")
except FileNotFoundError:
    print("Error: filtered_series_names.txt not found.")
    filtered_series_names = []

# Load and process metadata
try:
    metadata_df = pd.read_csv('datasets/wdi_metadata.csv', encoding='latin1', on_bad_lines='skip')
    metadata_df = metadata_df.dropna(subset=['Series Code'])
    metadata_df['Normalized Series Name'] = metadata_df['Series Name'].str.strip().str.lower()

    metadata_mapping = dict(zip(metadata_df['Series Name'], metadata_df['Series Code']))
    normalized_mapping = dict(zip(metadata_df['Normalized Series Name'], metadata_df['Series Code']))

    desired_series_codes = [metadata_mapping[name] for name in filtered_series_names if name in metadata_mapping]
    unmatched_entries = [name for name in filtered_series_names if name not in metadata_mapping]

    normalized_unmatched = [name.strip().lower() for name in unmatched_entries]
    normalized_codes = [normalized_mapping[name] for name in normalized_unmatched if name in normalized_mapping]
    desired_series_codes.extend(normalized_codes)

    final_unmatched = [name for name in normalized_unmatched if name not in normalized_mapping]
    if final_unmatched:
        print(f"Final unmatched entries: {final_unmatched}")

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

# Prepare indicators dictionary
indicators = {code: code for code in valid_series_codes}

# Define date range
date_range = (datetime(2000, 1, 1), datetime(2021, 12, 31))

# Define a function for batch queries
def batch_query(indicators, countries, date_range, batch_size=20):
    batches = [list(indicators.items())[i:i + batch_size] for i in range(0, len(indicators), batch_size)]
    all_data = []

    for batch in batches:
        try:
            batch_indicators = dict(batch)
            print(f"Querying batch with {len(batch_indicators)} indicators...")
            df_batch = wbdata.get_dataframe(indicators=batch_indicators, country=countries, date=date_range)
            all_data.append(df_batch)
            # Introduce a delay between batch queries
            time.sleep(2)  # Delay for 2 seconds
        except Exception as e:
            print(f"Error during batch query: {e}")

    if all_data:
        return pd.concat(all_data, axis=0)
    else:
        return pd.DataFrame()

# Download data in batches
try:
    countries = ['AFG', 'ALB', 'DZA', 'AGO', 'ATG', 'ARG', 'ARM', 'AUS', 'AUT', 'AZE', 'BHS', 'BHR', 'BGD', 'BRB', 'BLR', 'BEL', 'BLZ', 'BEN', 'BTN', 'BOL', 'BIH', 'BWA', 'BRA', 'BRN', 'BGR', 'BFA', 'BDI', 'CPV', 'KHM', 'CMR', 'CAN', 'CAF', 'TCD', 'CHL', 'CHN', 'COL', 'COM', 'COG', 'COD', 'CRI', 'HRV', 'CUB', 'CYP', 'CZE', 'DNK', 'DJI', 'DOM', 'ECU', 'EGY', 'SLV', 'GNQ', 'ERI', 'EST', 'SWZ', 'ETH', 'FJI', 'FIN', 'FRA', 'GAB', 'GMB', 'GEO', 'DEU', 'GHA', 'GRC', 'GRD', 'GTM', 'GIN', 'GNB', 'GUY', 'HTI', 'HND', 'HUN', 'ISL', 'IND', 'IDN', 'IRN', 'IRQ', 'IRL', 'ISR', 'ITA', 'JAM', 'JPN', 'JOR', 'KAZ', 'KEN', 'KIR', 'KOR', 'KWT', 'KGZ', 'LAO', 'LVA', 'LBN', 'LSO', 'LBR', 'LBY', 'LTU', 'LUX', 'MDG', 'MWI', 'MYS', 'MDV', 'MLI', 'MLT', 'MRT', 'MUS', 'MEX', 'FSM', 'MDA', 'MNG', 'MNE', 'MAR', 'MOZ', 'MMR', 'NAM', 'NPL', 'NLD', 'NZL', 'NIC', 'NER', 'NGA', 'MKD', 'NOR', 'OMN', 'PAK', 'PAN', 'PNG', 'PRY', 'PER', 'PHL', 'POL', 'PRT', 'PRI', 'QAT', 'ROU', 'RUS', 'RWA', 'VCT', 'LCA', 'STP', 'SAU', 'SEN', 'SRB', 'SYC', 'SLE', 'SGP', 'SVK', 'SVN', 'SLB', 'SOM', 'ZAF', 'SSD', 'ESP', 'LKA', 'SDN', 'SUR', 'SWE', 'CHE', 'SYR', 'TJK', 'TZA', 'THA', 'TLS', 'TGO', 'TON', 'TTO', 'TUN', 'TUR', 'TKM', 'UGA', 'UKR', 'ARE', 'GBR', 'USA', 'URY', 'UZB', 'VUT', 'VEN', 'VNM', 'PSE', 'WSM', 'YEM', 'ZMB', 'ZWE']
    df_wdi = batch_query(indicators, countries, date_range)
    if not df_wdi.empty:
        df_wdi.to_csv('datasets/wdi_data.csv')
        print("Download successful!")
    else:
        print("No data downloaded.")
except Exception as e:
    print(f"Error during data download: {e}")