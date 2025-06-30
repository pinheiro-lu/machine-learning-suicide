import pandas as pd

input_file = 'data/processed/merged_data_independent.csv'
output_file = 'data/processed/merged_data_independent_filled.csv'

df = pd.read_csv(input_file)
# Fill missing values with the median of each column (numeric only)
df_filled = df.copy()
for col in df_filled.select_dtypes(include='number').columns:
    median = df_filled[col].median()
    df_filled[col] = df_filled[col].fillna(median)

df_filled.to_csv(output_file, index=False)
print(f"Missing values filled with median. Output saved to {output_file}.")
