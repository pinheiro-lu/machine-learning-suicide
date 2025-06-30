import pandas as pd
from sklearn.model_selection import cross_val_score, KFold
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import make_scorer, mean_squared_error, r2_score
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree
from src.feature_selection import build_code_to_name

# Load your processed, filled data
df = pd.read_csv('data/processed/merged_data_independent_filled.csv')

# Set your target column
target_col = 'SuicideRatesPer100k'
# List of key columns to drop from features
key_columns = ['iso3', 'Year']

# Drop target and key columns from features
X = df.drop(columns=[target_col] + [col for col in key_columns if col in df.columns])
y = df[target_col]

# Load code-to-name mapping
code_to_name = build_code_to_name('data/raw/wdi_metadata.csv')

# Set up k-fold cross-validation (e.g., 5 folds)
k = 5
kf = KFold(n_splits=k, shuffle=True, random_state=42)

# Decision Tree model
model = DecisionTreeRegressor(random_state=42)

# Cross-validate with MSE and R2
mse_scores = cross_val_score(model, X, y, cv=kf, scoring=make_scorer(mean_squared_error))
r2_scores = cross_val_score(model, X, y, cv=kf, scoring=make_scorer(r2_score))

print(f"{k}-fold cross-validation results:")
print(f"Mean MSE: {np.mean(mse_scores):.4f} ± {np.std(mse_scores):.4f}")
print(f"Mean R2: {np.mean(r2_scores):.4f} ± {np.std(r2_scores):.4f}")

# Fit on the whole dataset for interpretability
model.fit(X, y)

# Print feature importances with actual names and accumulated importance
importances = pd.Series(model.feature_importances_, index=X.columns)
importances_named = importances.rename(lambda code: code_to_name.get(code, code))
importances_sorted = importances_named.sort_values(ascending=False)
accumulated = importances_sorted.cumsum()
N_TOP_FEATURES = 20  # Number of top features to print and analyze
print(f"\nFeature importances (top {N_TOP_FEATURES}):")
for name, imp, acc in zip(importances_sorted.index[:N_TOP_FEATURES], importances_sorted.values[:N_TOP_FEATURES], accumulated.values[:N_TOP_FEATURES]):
    print(f"{name:50s} Importance: {imp:.4f}  Accumulated: {acc:.4f}")

# Save feature importances to file (with names)
importances_named.sort_values(ascending=False).to_csv('data/interim/decision_tree_feature_importances.csv', header=['importance'])

# Optional: visualize the tree (for small trees)
plt.figure(figsize=(30, 16))  # Larger figure for readability
plot_tree(
    model,
    feature_names=[code_to_name.get(col, col) for col in X.columns],
    filled=True,
    max_depth=2,
    fontsize=10  # Smaller font size for clarity
)
plt.title("Decision Tree (first 2 levels)")
plt.show()
