import pandas as pd
from src.feature_selection import build_code_to_name

# Load top features from decision tree importances (all groups)
imp = pd.read_csv('results/decision_tree/feature_importances.csv')
top_feats_names = imp.iloc[:20, 0].tolist()

# Build code-to-name and name-to-code mapping
code_to_name = build_code_to_name('data/raw/wdi_metadata.csv')
name_to_code = {v: k for k, v in code_to_name.items()}

# Always keep these columns
base_cols = ['iso3', 'Year', 'SuicideRatesPer100k']

# Load the main dataset
df = pd.read_csv('data/processed/merged_data_independent_filled.csv')

# Map top feature names to codes, only keep those present in the dataset
present_codes = [name_to_code[name] for name in top_feats_names if name in name_to_code and name_to_code[name] in df.columns]
selected_cols = [col for col in base_cols if col in df.columns] + present_codes
filtered_df = df[selected_cols]

# Save the new dataset
filtered_df.to_csv('data/processed/merged_data_top20_decisiontree.csv', index=False)
print('Created data/processed/merged_data_top20_decisiontree.csv with columns:', filtered_df.columns.tolist())

# Move 'SuicideRatesPer100k' to the end if present
cols = [col for col in filtered_df.columns if col != 'SuicideRatesPer100k']
if 'SuicideRatesPer100k' in filtered_df.columns:
    cols.append('SuicideRatesPer100k')
filtered_df = filtered_df[cols]

filtered_df.to_csv('data/processed/merged_data_top20_decisiontree.csv', index=False)
print(f"Moved 'SuicideRatesPer100k' to the end in data/processed/merged_data_top20_decisiontree.csv.")
