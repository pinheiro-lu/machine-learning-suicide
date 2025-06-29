import pandas as pd

# Load unmatched series names
unmatched_file = 'datasets/unmatched_series_names.txt'
try:
    with open(unmatched_file, 'r') as file:
        unmatched_series_names = [line.strip() for line in file.readlines()]
    print(f"Loaded {len(unmatched_series_names)} unmatched series names.")
except FileNotFoundError:
    print("Error: unmatched_series_names.txt not found.")
    unmatched_series_names = []

# Load metadata
metadata_file = 'datasets/wdi_metadata.csv'
try:
    metadata_df = pd.read_csv(metadata_file, encoding='latin1', on_bad_lines='skip')
    print(f"Loaded metadata with {len(metadata_df)} entries.")
except FileNotFoundError:
    print("Error: wdi_metadata.csv not found.")
    metadata_df = pd.DataFrame()

# Search for unmatched series names in metadata
if not metadata_df.empty and unmatched_series_names:
    for name in unmatched_series_names:
        matches = metadata_df[metadata_df['Series Name'].str.contains(name, na=False, case=False)]
        if not matches.empty:
            print(f"Matches for '{name}':")
            print(matches[['Series Name', 'Series Code']])
        else:
            print(f"No matches found for '{name}'.")
else:
    print("No unmatched series names or metadata available for search.")
