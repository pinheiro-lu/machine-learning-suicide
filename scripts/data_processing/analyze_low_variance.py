import pandas as pd

# Load the deduplicated data
df = pd.read_csv('data/processed/merged_data_dedup.csv')

# Select only numeric columns
numeric_df = df.select_dtypes(include='number')

# Compute variance for each column
variances = numeric_df.var()

# Set a threshold for "low" variance (adjust as needed)
threshold = 0.01

# Identify columns with variance below the threshold
low_variance_cols = variances[variances < threshold].index.tolist()

print("Variables with low variance:")
for col in low_variance_cols:
    print(f"{col}: variance={variances[col]}")

# Optionally, save the list to a file
with open('data/interim/low_variance_features.txt', 'w') as f:
    for col in low_variance_cols:
        f.write(f"{col}: variance={variances[col]}\n")
