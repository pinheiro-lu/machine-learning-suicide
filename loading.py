import pandas as pd

def load_data(file_path: str) -> pd.DataFrame:
    """
    Load data from a CSV file into a pandas DataFrame.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The loaded data as a DataFrame.
    """
    try:
        data = pd.read_csv(file_path)
        return data
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        print("Error: The file is empty.")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        return pd.DataFrame()

wdi_data = load_data('datasets/wdi_data.csv')
who_data = load_data('datasets/who_data.csv')

# Normalize WDI data
wdi_data.rename(columns={'date': 'Year', 'value': 'wdi_value'}, inplace=True)
if 'countryiso3code' in wdi_data.columns:
    wdi_data.rename(columns={'countryiso3code': 'iso3'}, inplace=True)

# Remove CIV and PRK from main WDI data (to avoid duplicates)
if 'iso3' in wdi_data.columns:
    wdi_data = wdi_data[~wdi_data['iso3'].isin(['CIV', 'PRK'])]

# Normalize WHO data: filter to both sexes and rename columns
if 'Dim1' in who_data.columns:
    who_data = who_data[who_data['Dim1'] == 'Both sexes']
if 'SpatialDimValueCode' in who_data.columns:
    who_data.rename(columns={'SpatialDimValueCode': 'iso3', 'Period': 'Year', 'FactValueNumeric': 'SuicideRatesPer100k'}, inplace=True)
# Pivot WDI data to make indicators columns
wdi_data = wdi_data.pivot_table(index=['iso3', 'Year'], columns='indicator', values='wdi_value').reset_index()
# Merge normalized WDI and WHO data
merged = pd.merge(wdi_data, who_data[['iso3', 'Year', 'SuicideRatesPer100k']], on=['iso3', 'Year'], how='inner')

# Load CIV and PRK data
civ_prk_data = load_data('datasets/wdi_civ_prk_data.csv')

# Normalize CIV and PRK data
civ_prk_data.rename(columns={'date': 'Year', 'value': 'wdi_value'}, inplace=True)
if 'countryiso3code' in civ_prk_data.columns:
    civ_prk_data.rename(columns={'countryiso3code': 'iso3'}, inplace=True)

# Pivot CIV and PRK data to make indicators columns
civ_prk_data = civ_prk_data.pivot_table(index=['iso3', 'Year'], columns='indicator', values='wdi_value').reset_index()

# Append CIV and PRK data to merged dataset
merged = pd.concat([merged, civ_prk_data], ignore_index=True)

# Save updated merged data
merged.to_csv('datasets/merged_data.csv', index=False)
print(f"Merged dataset saved with {len(merged)} records.")