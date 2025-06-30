import pandas as pd

# Load the deduplicated data
df = pd.read_csv('data/processed/merged_data_nohighmissing.csv')

# Calculate the fraction of missing values for each row
missing_fraction = df.isnull().mean(axis=1)

# Set a threshold for maximum allowed missing fraction per row (e.g., 0.3 = 30%)
threshold = 0.5

# Identify rows with too many missing values
high_missing_rows = missing_fraction[missing_fraction > threshold]

print(f"Rows with more than {threshold*100:.0f}% missing data: {len(high_missing_rows)} out of {len(df)}")

# Optionally, save the indices and missing fraction to a file
with open('data/interim/high_missing_rows.txt', 'w') as f:
    for idx, frac in high_missing_rows.items():
        f.write(f"Row {idx}: {frac*100:.2f}% missing\n")
    f.write(f"\nTotal: {len(high_missing_rows)} rows with >{threshold*100:.0f}% missing data out of {len(df)} total rows\n")
