import pandas as pd
from src.feature_selection import build_code_to_name, find_highly_correlated, write_correlated_pairs

# Load merged data
df = pd.read_csv('data/processed/merged_data.csv')

# Load code-to-name mapping
code_to_name = build_code_to_name('data/raw/wdi_metadata.csv')

# Find highly correlated pairs
pairs = find_highly_correlated(df, threshold=0.9)

# Write all highly correlated pairs to file
write_correlated_pairs(
    [(col1, col2) for col1, col2, _ in pairs],
    code_to_name,
    'data/interim/correlated.txt',
    header="Highly correlated variable pairs (|corr| > 0.9):"
)

if pairs:
    print("Highly correlated variable pairs (|corr| > 0.9):")
    for col1, col2, corr in pairs:
        name1 = code_to_name.get(col1, col1)
        name2 = code_to_name.get(col2, col2)
        print(f"{col1} ({name1}) and {col2} ({name2}): correlation = {corr:.2f}")
else:
    print("No variable pairs with |correlation| > 0.9 found.")
