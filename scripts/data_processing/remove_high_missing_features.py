import pandas as pd

# Load the deduplicated data
df = pd.read_csv('data/processed/merged_data.csv')

# Load high-missing features from file
with open('data/interim/high_missing_features.txt') as f:
    high_missing_cols = [line.split(':')[0].strip() for line in f if ':' in line and 'missing' in line]

# Drop high-missing features
cleaned_df = df.drop(columns=[col for col in high_missing_cols if col in df.columns])

# Save the cleaned dataframe
cleaned_df.to_csv('data/processed/merged_data_nohighmissing.csv', index=False)
print(f"Removed {len(high_missing_cols)} high-missing features. Saved to data/processed/merged_data_nohighmissing.csv with {len(cleaned_df.columns)} columns.")
