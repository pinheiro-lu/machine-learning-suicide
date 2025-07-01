import sys
import os
import pandas as pd

from src.data_processing import merge_wdi_who_data

# Load the final both sexes dataset
final_both_path = 'data/processed/merged_data_independent_filled.csv'
df_both = pd.read_csv(final_both_path)

# Helper to replace target with sex-specific rates
def inject_sex_rates(df_both, sex):
    from src.data_processing import load_data
    who = load_data('data/raw/who_data.csv')
    # Filter for the right sex
    who_sex = who[who['Dim1'] == sex]
    who_sex = who_sex.rename(columns={'SpatialDimValueCode': 'iso3', 'Period': 'Year', 'FactValueNumeric': 'SuicideRatesPer100k'})
    who_sex = who_sex[['iso3', 'Year', 'SuicideRatesPer100k']]
    # Merge, replacing only the target column
    merged = df_both.copy()
    merged = merged.merge(who_sex, on=['iso3', 'Year'], how='left', suffixes=('', '_sex'))
    merged['SuicideRatesPer100k'] = merged['SuicideRatesPer100k_sex']
    merged = merged.drop(columns=['SuicideRatesPer100k_sex'])
    return merged

if __name__ == "__main__":
    male = inject_sex_rates(df_both, 'Male')
    male.to_csv('data/processed/merged_data_independent_filled_male.csv', index=False)
    female = inject_sex_rates(df_both, 'Female')
    female.to_csv('data/processed/merged_data_independent_filled_female.csv', index=False)
