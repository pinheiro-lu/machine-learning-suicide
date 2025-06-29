import pandas as pd

merged = pd.read_csv('datasets/merged_data.csv')
complete_cases = merged.dropna()
print(f"Records with no missing values (list-wise deletion): {len(complete_cases)} out of {len(merged)} total records.")
