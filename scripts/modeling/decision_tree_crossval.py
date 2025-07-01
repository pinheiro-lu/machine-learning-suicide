import os
import argparse
import pandas as pd
from sklearn.model_selection import cross_val_score, KFold
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.metrics import make_scorer, mean_squared_error, r2_score
import numpy as np
import matplotlib.pyplot as plt
import json
from src.feature_selection import build_code_to_name

def parse_args():
    parser = argparse.ArgumentParser(description="Decision Tree Regression with flexible output structure.")
    parser.add_argument('--mode', choices=['default', 'interpretable', 'top_features'], default='default', help='Which feature set to use')
    parser.add_argument('--gender', choices=['all', 'female', 'male'], default='all', help='Which gender dataset to use')
    parser.add_argument('--classification_col', type=str, default=None, help='Column for classification-based modeling (e.g., income_group)')
    parser.add_argument('--results_dir', type=str, default='results/decision_tree', help='Base directory for results')
    parser.add_argument('--target_col', type=str, default='SuicideRatesPer100k', help='Target column name')
    parser.add_argument('--k', type=int, default=5, help='Number of folds for cross-validation')
    parser.add_argument('--random_state', type=int, default=42, help='Random state for reproducibility')
    return parser.parse_args()

def get_data_and_dir(mode, gender, results_dir):
    gender_suffix = '' if gender == 'all' else f'_{gender}'
    if mode == 'interpretable':
        data_path = f'data/processed/merged_data_interpretable{gender_suffix}.csv'
        out_dir = os.path.join(results_dir, f'interpretable{gender_suffix}')
    elif mode == 'top_features':
        data_path = f'data/processed/merged_data_top20_decisiontree{gender_suffix}.csv'
        out_dir = os.path.join(results_dir, f'top_features{gender_suffix}')
    else:
        data_path = f'data/processed/merged_data_independent_filled{gender_suffix}.csv'
        out_dir = results_dir if gender == 'all' else results_dir + f'_{gender}'
    return data_path, out_dir

def save_metrics(metrics, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"[INFO] Saved metrics to {os.path.join(out_dir, 'metrics.json')}")

def save_feature_importances_with_split_direction(model, X, code_to_name, out_dir):
    importances = pd.Series(model.feature_importances_, index=X.columns)
    tree = model.tree_
    feature_names = X.columns
    split_directions = {name: [] for name in feature_names}
    # Traverse all nodes
    for node in range(tree.node_count):
        feature_idx = tree.feature[node]
        if feature_idx >= 0:
            left = tree.children_left[node]
            right = tree.children_right[node]
            left_value = tree.value[left][0][0]
            right_value = tree.value[right][0][0]
            # If going right (feature > threshold) increases prediction, direction is positive
            if right_value > left_value:
                split_directions[feature_names[feature_idx]].append('positive')
            elif right_value < left_value:
                split_directions[feature_names[feature_idx]].append('negative')
            else:
                split_directions[feature_names[feature_idx]].append('neutral')
    # Aggregate direction for each feature
    summary = []
    for feat in feature_names:
        dirs = split_directions[feat]
        pos = dirs.count('positive')
        neg = dirs.count('negative')
        if pos > neg:
            direction = 'mostly positive'
        elif neg > pos:
            direction = 'mostly negative'
        elif pos == 0 and neg == 0:
            direction = 'not used'
        else:
            direction = 'mixed'
        summary.append({
            'feature': code_to_name.get(feat, feat),
            'importance': importances[feat],
            'split_direction': direction
        })
    df = pd.DataFrame(summary).sort_values('importance', ascending=False)
    out_path = os.path.join(out_dir, 'feature_importances_with_direction.csv')
    df.to_csv(out_path, index=False)
    print(f"[INFO] Saved feature importances with split direction to {out_path}")

def save_tree_plot(model, X, code_to_name, out_dir):
    plt.figure(figsize=(30, 16))
    plot_tree(
        model,
        feature_names=[code_to_name.get(col, col) for col in X.columns],
        filled=True,
        max_depth=2,
        fontsize=10
    )
    plt.title("Decision Tree (first 2 levels)")
    out_path = os.path.join(out_dir, 'tree_plot.png')
    plt.savefig(out_path)
    plt.close()
    print(f"[INFO] Saved tree plot to {out_path}")

def run_tree(X, y, k, random_state, code_to_name, out_dir):
    kf = KFold(n_splits=k, shuffle=True, random_state=random_state)
    model = DecisionTreeRegressor(random_state=random_state)
    mse_scores = cross_val_score(model, X, y, cv=kf, scoring=make_scorer(mean_squared_error))
    r2_scores = cross_val_score(model, X, y, cv=kf, scoring=make_scorer(r2_score))
    metrics = {
        'k_fold': k,
        'mean_mse': float(np.mean(mse_scores)),
        'std_mse': float(np.std(mse_scores)),
        'mean_r2': float(np.mean(r2_scores)),
        'std_r2': float(np.std(r2_scores)),
        'n_samples': int(len(y))
    }
    print(f"[INFO] {k}-fold CV: Mean MSE={metrics['mean_mse']:.4f} ± {metrics['std_mse']:.4f}, Mean R2={metrics['mean_r2']:.4f} ± {metrics['std_r2']:.4f}, N={metrics['n_samples']}")
    save_metrics(metrics, out_dir)
    model.fit(X, y)
    save_feature_importances_with_split_direction(model, X, code_to_name, out_dir)
    save_tree_plot(model, X, code_to_name, out_dir)

def main():
    args = parse_args()
    data_path, base_out_dir = get_data_and_dir(args.mode, args.gender, args.results_dir)
    df = pd.read_csv(data_path)
    code_to_name = build_code_to_name('data/raw/wdi_metadata.csv')
    target_col = args.target_col
    key_columns = ['iso3', 'Year']

    # If classification_col is set, only bring in the classification columns for the countries
    if args.classification_col:
        class_df = pd.read_csv('data/raw/wdi_country_classifications.csv')
        if 'iso3' in df.columns and 'iso3' in class_df.columns and args.classification_col in class_df.columns:
            df = df.merge(class_df[['iso3', args.classification_col]], on='iso3', how='left')
        else:
            print('[WARN] iso3 or classification column missing in data or classification file; skipping merge.')

    if args.classification_col:
        groups = df[args.classification_col].unique()
        for group in groups:
            group_df = df[df[args.classification_col] == group]
            if group_df.shape[0] < args.k:
                print(f"Skipping group {group} (not enough samples)")
                continue
            out_dir = os.path.join(base_out_dir, args.classification_col, str(group))
            X = group_df.drop(columns=[target_col] + [col for col in key_columns if col in group_df.columns])
            X = X.select_dtypes(include=[np.number])
            y = group_df[target_col]
            run_tree(X, y, args.k, args.random_state, code_to_name, out_dir)
    else:
        X = df.drop(columns=[target_col] + [col for col in key_columns if col in df.columns])
        X = X.select_dtypes(include=[np.number])
        y = df[target_col]
        run_tree(X, y, args.k, args.random_state, code_to_name, base_out_dir)

if __name__ == "__main__":
    main()
