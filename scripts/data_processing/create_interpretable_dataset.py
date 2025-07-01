import pandas as pd
from src.feature_selection import build_code_to_name

# Paths
base_path = 'data/processed/merged_data_independent_filled.csv'
noninterp_path = 'data/interim/non_interpretable.txt'
out_path = 'data/processed/merged_data_interpretable.csv'

# Load base dataset
base_df = pd.read_csv(base_path)

# Build code-to-name and name-to-code mapping
code_to_name = build_code_to_name('data/raw/wdi_metadata.csv')
name_to_code = {v: k for k, v in code_to_name.items()}

# Load non-interpretable feature names (one per line, possibly quoted)
with open(noninterp_path, 'r', encoding='utf-8') as f:
    noninterp_names = [line.strip().strip('"') for line in f if line.strip()]

# Map names to codes, only keep those present in the dataset
noninterp_codes = [name_to_code[name] for name in noninterp_names if name in name_to_code and name_to_code[name] in base_df.columns]

# Remove columns by code (if present)
filtered_df = base_df.drop(columns=noninterp_codes)

# Save new dataset
filtered_df.to_csv(out_path, index=False)
print(f"Created {out_path} without columns: {noninterp_codes}")
