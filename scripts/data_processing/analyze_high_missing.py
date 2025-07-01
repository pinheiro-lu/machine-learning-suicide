import pandas as pd

# Load the deduplicated data
df = pd.read_csv('data/processed/merged_data_independent.csv')

# Set a threshold for maximum allowed missing fraction (e.g., 0.3 = 30%)
threshold = 0.5

# Calculate fraction of missing values for each column
missing_fraction = df.isnull().mean()

# Identify columns with too many missing values
high_missing_cols = missing_fraction[missing_fraction > threshold].index.tolist()

print(f"Features with more than {threshold*100:.0f}% missing data:")
for col in high_missing_cols:
    print(f"{col}: {missing_fraction[col]*100:.2f}% missing")

print(f"\nTotal features with >{threshold*100:.0f}% missing: {len(high_missing_cols)}")

# Optionally, save the list to a file
with open('data/interim/high_missing_features.txt', 'w') as f:
    for col in high_missing_cols:
        f.write(f"{col}: {missing_fraction[col]*100:.2f}% missing\n")
    f.write(f"\nTotal: {len(high_missing_cols)} features with >{threshold*100:.0f}% missing data\n")
