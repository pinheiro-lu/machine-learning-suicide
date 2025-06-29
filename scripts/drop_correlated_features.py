import pandas as pd
from src.feature_selection import build_code_to_name, find_highly_correlated, drop_correlated_features

# Load merged data
df = pd.read_csv('data/processed/merged_data.csv')

# Load code-to-name mapping
code_to_name = build_code_to_name('data/raw/wdi_metadata.csv')

# Find highly correlated pairs
pairs = find_highly_correlated(df, threshold=0.9)

# Drop features based on completeness
reduced_df, dropped = drop_correlated_features(df, pairs, strategy='completeness')

print(f"Dropped features: {dropped}")
reduced_df.to_csv('data/processed/merged_data_dedup.csv', index=False)
