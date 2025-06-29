import pandas as pd
import csv

def build_code_to_name(metadata_path):
    code_to_name = {}
    with open(metadata_path, encoding='latin1') as f:
        reader = csv.reader(f)
        header = next(reader)
        code_idx = header.index('Code')
        name_idx = header.index('Indicator Name')
        for row in reader:
            if len(row) > max(code_idx, name_idx):
                code = row[code_idx].strip()
                name = row[name_idx].strip()
                if code and name:
                    code_to_name[code] = name
    return code_to_name

def find_highly_correlated(df, threshold=0.9):
    numeric_df = df.select_dtypes(include='number')
    corr_matrix = numeric_df.corr()
    high_corr = (corr_matrix.abs() > threshold) & (corr_matrix.abs() < 1.0)
    pairs = [
        (col1, col2, corr_matrix.loc[col1, col2])
        for col1 in corr_matrix.columns
        for col2 in corr_matrix.columns
        if high_corr.loc[col1, col2] and col1 < col2
    ]
    return pairs

def feature_completeness(df, feature):
    return df[feature].notna().sum()

def drop_correlated_features(df, pairs, strategy='completeness'):
    to_drop = set()
    for col1, col2, _ in pairs:
        if strategy == 'completeness':
            n1 = feature_completeness(df, col1)
            n2 = feature_completeness(df, col2)
            if n1 < n2:
                to_drop.add(col1)
            else:
                to_drop.add(col2)
    return df.drop(columns=list(to_drop)), to_drop
