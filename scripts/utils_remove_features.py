import pandas as pd

def remove_features_from_list(input_file, remove_file, output_file):
    df = pd.read_csv(input_file)
    print(f"Number of features before removal: {df.shape[1]}")
    # Normalize DataFrame columns
    col_map = {str(col).strip(): col for col in df.columns}
    normalized_columns = set(col_map.keys())
    # Remove features listed in remove_file (normalize for matching)
    with open(remove_file) as f:
        to_remove_raw = [line.strip() for line in f if line.strip()]
        to_remove = [str(col).strip() for col in to_remove_raw]
    # Find which features are present and which are missing
    present = [col_map[col] for col in to_remove if col in normalized_columns]
    missing = [col for col in to_remove if col not in normalized_columns]
    if missing:
        print(f"Warning: {len(missing)} features from {remove_file} not found in DataFrame: {missing}")
    # Remove present features
    df = df.drop(columns=present)
    df.to_csv(output_file, index=False)
    print(f"Removed {len(present)} features from {remove_file}. Saved to {output_file}.")
