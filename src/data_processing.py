import pandas as pd

def load_data(file_path: str) -> pd.DataFrame:
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

def merge_wdi_who_data(wdi_path, who_path, civ_prk_path, output_path):
    wdi_data = load_data(wdi_path)
    who_data = load_data(who_path)

    # Normalize WDI data
    wdi_data.rename(columns={'date': 'Year', 'value': 'wdi_value'}, inplace=True)
    if 'countryiso3code' in wdi_data.columns:
        wdi_data.rename(columns={'countryiso3code': 'iso3'}, inplace=True)
    if 'iso3' in wdi_data.columns:
        wdi_data = wdi_data[~wdi_data['iso3'].isin(['CIV', 'PRK'])]

    # Normalize WHO data
    if 'Dim1' in who_data.columns:
        who_data = who_data[who_data['Dim1'] == 'Both sexes']
    if 'SpatialDimValueCode' in who_data.columns:
        who_data.rename(columns={'SpatialDimValueCode': 'iso3', 'Period': 'Year', 'FactValueNumeric': 'SuicideRatesPer100k'}, inplace=True)

    # Pivot WDI data
    wdi_data = wdi_data.pivot_table(index=['iso3', 'Year'], columns='indicator', values='wdi_value').reset_index()
    merged = pd.merge(wdi_data, who_data[['iso3', 'Year', 'SuicideRatesPer100k']], on=['iso3', 'Year'], how='inner')

    # Load and process CIV/PRK data
    civ_prk_data = load_data(civ_prk_path)
    civ_prk_data.rename(columns={'date': 'Year', 'value': 'wdi_value'}, inplace=True)
    if 'countryiso3code' in civ_prk_data.columns:
        civ_prk_data.rename(columns={'countryiso3code': 'iso3'}, inplace=True)
    civ_prk_data = civ_prk_data.pivot_table(index=['iso3', 'Year'], columns='indicator', values='wdi_value').reset_index()
    merged = pd.concat([merged, civ_prk_data], ignore_index=True)

    # Move SuicideRatesPer100k to the last column
    if 'SuicideRatesPer100k' in merged.columns:
        cols = [col for col in merged.columns if col != 'SuicideRatesPer100k'] + ['SuicideRatesPer100k']
        merged = merged[cols]

    merged.to_csv(output_path, index=False)
    print(f"Merged dataset saved with {len(merged)} records.")
