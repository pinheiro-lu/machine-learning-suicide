import pandas as pd
from sklearn.model_selection import cross_val_score, KFold
from sklearn.linear_model import RidgeCV
from sklearn.metrics import make_scorer, mean_squared_error, r2_score
import numpy as np
from sklearn.preprocessing import StandardScaler
from src.feature_selection import build_code_to_name

# Load your processed, filled data
df = pd.read_csv('data/processed/merged_data_independent_filled.csv')

target_col = 'SuicideRatesPer100k'
key_columns = ['iso3', 'Year']
X = df.drop(columns=[target_col] + [col for col in key_columns if col in df.columns])
y = df[target_col]

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Load code-to-name mapping
code_to_name = build_code_to_name('data/raw/wdi_metadata.csv')

# Set up k-fold cross-validation
k = 5
kf = KFold(n_splits=k, shuffle=True, random_state=42)

# Ridge regression with cross-validated alpha
alphas = np.logspace(-2, 8, 100)
model = RidgeCV(alphas=alphas, cv=kf)
model.fit(X_scaled, y)

# Cross-validate with MSE and R2
mse_scores = cross_val_score(model, X_scaled, y, cv=kf, scoring=make_scorer(mean_squared_error))
r2_scores = cross_val_score(model, X_scaled, y, cv=kf, scoring=make_scorer(r2_score))

print(f"Ridge Regression ({k}-fold cross-validation, standardized features):")
print(f"Mean MSE: {np.mean(mse_scores):.4f} ± {np.std(mse_scores):.4f}")
print(f"Mean R2: {np.mean(r2_scores):.4f} ± {np.std(r2_scores):.4f}")
print(f"Best alpha (regularization): {model.alpha_}")

# Print coefficients with feature names
coefs = pd.Series(model.coef_, index=X.columns)
coefs_named = coefs.rename(lambda code: code_to_name.get(code, code))
print("\nCoefficients (sorted by absolute value):")
print(coefs_named.reindex(coefs_named.abs().sort_values(ascending=False).index).head(20))

# Save coefficients to file
coefs_named.reindex(coefs_named.abs().sort_values(ascending=False).index).to_csv('data/interim/ridge_coefficients.csv', header=['coefficient'])
