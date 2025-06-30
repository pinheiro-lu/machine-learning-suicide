import pandas as pd
from src.feature_selection import find_highly_correlated, build_code_to_name

# Load the cleaned data (after all other removals)
df = pd.read_csv('data/processed/merged_data_dedup.csv')
print(f"Number of features before removal: {df.shape[1]}")

# Normalize DataFrame columns
col_map = {str(col).strip(): col for col in df.columns}
normalized_columns = set(col_map.keys())

# Remove features listed in to_remove.txt (normalize for matching)
with open('data/interim/to_remove.txt') as f:
    to_remove_raw = [line.strip() for line in f if line.strip()]
    to_remove = [str(col).strip() for col in to_remove_raw]

# Find which features are present and which are missing
present = [col_map[col] for col in to_remove if col in normalized_columns]
missing = [col for col in to_remove if col not in normalized_columns]

if missing:
    print(f"Warning: {len(missing)} features from to_remove.txt not found in DataFrame: {missing}")

# Remove present features
df = df.drop(columns=present)

# Save the new cleaned file
output_file = 'data/processed/merged_data_after_to_remove.csv'
df.to_csv(output_file, index=False)
print(f"Removed {len(present)} features from to_remove.txt. Saved to {output_file}.")

# Find highly correlated pairs (after removal)
pairs = find_highly_correlated(df, threshold=0.9)

# Load code-to-name mapping for better output
code_to_name = build_code_to_name('data/raw/wdi_metadata.csv')

# Write correlated pairs to correlated.txt
with open('data/interim/correlated.txt', 'w') as f:
    if pairs:
        f.write("Highly correlated pairs (|correlation| > 0.9):\n")
        for a, b, corr in pairs:
            f.write(f"{a} ({code_to_name.get(a, a)}) <-> {b} ({code_to_name.get(b, b)}): {corr:.4f}\n")
    else:
        f.write("No highly correlated pairs found.\n")
print("Wrote highly correlated pairs to data/interim/correlated.txt.")
