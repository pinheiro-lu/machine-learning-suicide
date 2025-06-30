import pandas as pd
from src.feature_selection import find_highly_correlated

# Load the data after removal
input_file = 'data/processed/merged_data_after_to_remove.csv'
df = pd.read_csv(input_file)

# Find highly correlated pairs (after removal)
pairs = find_highly_correlated(df, threshold=0.9)

# Output all remaining pairs with their correlation
output_file = 'data/interim/variance_of_remaining_pairs.txt'
with open(output_file, 'w') as f:
    f.write('Feature1\tFeature2\tCorrelation\tVariance1\tVariance2\n')
    for a, b, corr in sorted(pairs):
        var_a = df[a].var()
        var_b = df[b].var()
        f.write(f'{a}\t{b}\t{corr:.6g}\t{var_a:.6g}\t{var_b:.6g}\n')

print(f"Detailed info for all remaining correlated pairs written to {output_file}.")
