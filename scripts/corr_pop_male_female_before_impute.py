import pandas as pd
from src.feature_selection import build_code_to_name

# Load the pre-imputation data
# Assuming the file before imputation is 'merged_data_independent.csv'
df = pd.read_csv('data/processed/merged_data_nohighmissing_rows.csv')

# Get code for the indicator names
code_to_name = build_code_to_name('data/raw/wdi_metadata.csv')
name_to_code = {v: k for k, v in code_to_name.items()}

col_male_name = 'Population, male (% of total population)'
col_female_name = 'Population, female (% of total population)'
col_male = name_to_code.get(col_male_name)
col_female = name_to_code.get(col_female_name)

if col_male in df.columns and col_female in df.columns:
    corr = df[[col_male, col_female]].corr().iloc[0, 1]
    print(f"Correlation between '{col_male_name}' and '{col_female_name}' (before imputation): {corr:.4f}")
else:
    print(f"Columns not found: {col_male} ({col_male_name}), {col_female} ({col_female_name})")
