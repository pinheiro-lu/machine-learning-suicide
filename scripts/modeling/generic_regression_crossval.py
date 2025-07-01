import os
import argparse
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import make_scorer, mean_squared_error, r2_score
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import json
from src.feature_selection import build_code_to_name

def parse_args():
    parser = argparse.ArgumentParser(description="Generic Regression Model Runner.")
    parser.add_argument('--model', choices=['decision_tree', 'lasso'], required=True, help='Which model to run')
    parser.add_argument('--mode', choices=['default', 'interpretable', 'top_features'], default='default', help='Which feature set to use')
    parser.add_argument('--gender', choices=['all', 'female', 'male'], default='all', help='Which gender dataset to use')
    parser.add_argument('--classification_col', type=str, default=None, help='Column for classification-based modeling (e.g., income_group)')
    parser.add_argument('--results_dir', type=str, default=None, help='Base directory for results')
    parser.add_argument('--target_col', type=str, default='SuicideRatesPer100k', help='Target column name')
    parser.add_argument('--k', type=int, default=5, help='Number of folds for cross-validation')
    parser.add_argument('--random_state', type=int, default=42, help='Random state for reproducibility')
    args = parser.parse_args()
    if args.results_dir is None:
        args.results_dir = f"results/{args.model}"
    return args

def get_data_and_dir(mode, gender, results_dir):
    gender_suffix = '' if gender == 'all' else f'_{gender}'
    if mode == 'interpretable':
        data_path = f'data/processed/merged_data_interpretable{gender_suffix}.csv'
        out_dir = os.path.join(results_dir + gender_suffix, 'interpretable')
    elif mode == 'top_features':
        data_path = f'data/processed/merged_data_top20_decisiontree{gender_suffix}.csv'
        out_dir = os.path.join(results_dir + gender_suffix, 'top_features')
    else:
        data_path = f'data/processed/merged_data_independent_filled{gender_suffix}.csv'
        out_dir = results_dir if gender == 'all' else results_dir + gender_suffix
    return data_path, out_dir

def save_metrics(metrics, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"[INFO] Saved metrics to {os.path.join(out_dir, 'metrics.json')}")

def save_feature_importances(importances, code_to_name, out_dir):
    importances_named = importances.rename(lambda code: code_to_name.get(code, code))
    out_path = os.path.join(out_dir, 'feature_importances.csv')
    importances_named.sort_values(ascending=False).to_csv(out_path, header=['importance'])
    print(f"[INFO] Saved feature importances to {out_path}")

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

def save_coefficients(coefs, code_to_name, out_dir):
    coefs_named = coefs.rename(lambda code: code_to_name.get(code, code))
    out_path = os.path.join(out_dir, 'nonzero_coefficients.csv')
    coefs_sorted = coefs_named[coefs_named != 0].reindex(coefs_named[coefs_named != 0].abs().sort_values(ascending=False).index)
    coefs_sorted.to_csv(out_path, header=['coefficient'])
    print(f"[INFO] Saved nonzero coefficients to {out_path}")

def save_feature_importances_with_split_direction(model, X, code_to_name, out_dir):
    """
    For each feature, at each split:
    - If right_value > parent_value, count as a positive split for that feature
    - Else, count as a negative split for that feature
    Output the proportion of positive/negative splits and the proportion of samples classified as positive/negative for each feature.
    """
    importances = pd.Series(model.feature_importances_, index=X.columns)
    tree = model.tree_
    feature_names = X.columns
    pos_splits = {name: 0 for name in feature_names}
    neg_splits = {name: 0 for name in feature_names}
    pos_samples = {name: 0 for name in feature_names}
    neg_samples = {name: 0 for name in feature_names}
    for node in range(tree.node_count):
        feature_idx = tree.feature[node]
        if feature_idx >= 0:
            right = tree.children_right[node]
            right_value = tree.value[right][0][0]
            parent_value = tree.value[node][0][0]
            n_parent = tree.n_node_samples[node]
            if right_value > parent_value:
                pos_splits[feature_names[feature_idx]] += 1
                pos_samples[feature_names[feature_idx]] += n_parent
            else:
                neg_splits[feature_names[feature_idx]] += 1
                neg_samples[feature_names[feature_idx]] += n_parent
    summary = []
    for feat in feature_names:
        total_splits = pos_splits[feat] + neg_splits[feat]
        total_samples = pos_samples[feat] + neg_samples[feat]
        if total_splits > 0:
            prop_pos_splits = pos_splits[feat] / total_splits
            prop_neg_splits = neg_splits[feat] / total_splits
        else:
            prop_pos_splits = prop_neg_splits = 0.0
        if total_samples > 0:
            prop_pos_samples = pos_samples[feat] / total_samples
            prop_neg_samples = neg_samples[feat] / total_samples
        else:
            prop_pos_samples = prop_neg_samples = 0.0
        summary.append({
            'feature': code_to_name.get(feat, feat),
            'importance': importances[feat],
            'prop_positive_splits': round(prop_pos_splits, 3),
            'prop_negative_splits': round(prop_neg_splits, 3),
            'prop_positive_samples': round(prop_pos_samples, 3),
            'prop_negative_samples': round(prop_neg_samples, 3)
        })
    df = pd.DataFrame(summary).sort_values('importance', ascending=False)
    out_path = os.path.join(out_dir, 'feature_importances_with_direction.csv')
    df.to_csv(out_path, index=False)
    print(f"[INFO] Saved feature importances with split direction to {out_path}")

def run_decision_tree(X, y, k, random_state, code_to_name, out_dir):
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

def run_lasso(X, y, k, random_state, code_to_name, out_dir):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kf = KFold(n_splits=k, shuffle=True, random_state=random_state)
    model = LassoCV(cv=kf, random_state=random_state, max_iter=10000)
    model.fit(X_scaled, y)
    mse_scores = cross_val_score(model, X_scaled, y, cv=kf, scoring=make_scorer(mean_squared_error))
    r2_scores = cross_val_score(model, X_scaled, y, cv=kf, scoring=make_scorer(r2_score))
    metrics = {
        'k_fold': k,
        'mean_mse': float(np.mean(mse_scores)),
        'std_mse': float(np.std(mse_scores)),
        'mean_r2': float(np.mean(r2_scores)),
        'std_r2': float(np.std(r2_scores)),
        'n_samples': int(len(y)),
        'best_alpha': float(model.alpha_)
    }
    print(f"[INFO] {k}-fold CV: Mean MSE={metrics['mean_mse']:.4f} ± {metrics['std_mse']:.4f}, Mean R2={metrics['mean_r2']:.4f} ± {metrics['std_r2']:.4f}, N={metrics['n_samples']}, Best alpha={metrics['best_alpha']:.6f}")
    save_metrics(metrics, out_dir)
    coefs = pd.Series(model.coef_, index=X.columns)
    save_coefficients(coefs, code_to_name, out_dir)

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
            if args.model == 'decision_tree':
                run_decision_tree(X, y, args.k, args.random_state, code_to_name, out_dir)
            elif args.model == 'lasso':
                run_lasso(X, y, args.k, args.random_state, code_to_name, out_dir)
    else:
        X = df.drop(columns=[target_col] + [col for col in key_columns if col in df.columns])
        X = X.select_dtypes(include=[np.number])
        y = df[target_col]
        if args.model == 'decision_tree':
            run_decision_tree(X, y, args.k, args.random_state, code_to_name, base_out_dir)
        elif args.model == 'lasso':
            run_lasso(X, y, args.k, args.random_state, code_to_name, base_out_dir)

if __name__ == "__main__":
    main()
