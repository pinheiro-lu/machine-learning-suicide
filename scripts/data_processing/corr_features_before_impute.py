import pandas as pd
from src.feature_selection import build_code_to_name

# Load the pre-imputation data
df = pd.read_csv('data/processed/merged_data_independent.csv')

# Get code for the indicator names
code_to_name = build_code_to_name('data/raw/wdi_metadata.csv')
name_to_code = {v: k for k, v in code_to_name.items()}

def get_feature_code(name_or_code):
    # Try to resolve as name, else assume it's a code
    return name_to_code.get(name_or_code, name_or_code)

# User input: change these to any two feature names or codes
target1 = input("Enter first feature (name or code): ").strip()
target2 = input("Enter second feature (name or code): ").strip()

col1 = get_feature_code(target1)
col2 = get_feature_code(target2)

if col1 in df.columns and col2 in df.columns:
    corr = df[[col1, col2]].corr().iloc[0, 1]
    print(f"Correlation between '{target1}' [{col1}] and '{target2}' [{col2}] (before imputation): {corr:.4f}")
else:
    print(f"Columns not found: {col1} ({target1}), {col2} ({target2})")
