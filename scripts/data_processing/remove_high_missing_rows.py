import pandas as pd

# Load the data after high-missing features have been removed
df = pd.read_csv('data/processed/merged_data_nohighmissing.csv')

# Set a threshold for maximum allowed missing fraction per row (e.g., 0.5 = 50%)
threshold = 0.5

# Calculate the fraction of missing values for each row
missing_fraction = df.isnull().mean(axis=1)

# Keep only rows with missing fraction <= threshold
cleaned_df = df[missing_fraction <= threshold]

print(f"Removed {len(df) - len(cleaned_df)} rows with more than {threshold*100:.0f}% missing data.")
print(f"Remaining rows: {len(cleaned_df)} out of {len(df)}.")

# Save the cleaned dataframe
cleaned_df.to_csv('data/processed/merged_data_nohighmissing_rows.csv', index=False)
