import pandas as pd
from scripts.utils_remove_features import remove_features_from_list

input_file = 'data/processed/merged_data_after_to_remove.csv'
remove_file = 'data/interim/to_remove_low_variance.txt'
output_file = 'data/processed/merged_data_after_to_remove_low_variance.csv'

remove_features_from_list(input_file, remove_file, output_file)
print(f"Removed features from {remove_file} and saved to {output_file}.")
