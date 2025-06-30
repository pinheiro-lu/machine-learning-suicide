# Data Cleaning and Feature Selection Pipeline

This directory contains scripts for cleaning, filtering, and preparing the dataset for modeling. Follow the steps below in order for best results.

## Recommended Script Order

1. **fetch_data.py**
   - Downloads and prepares the raw data from the World Bank and WHO APIs.

2. **remove_high_missing_features.py**
   - Removes features (columns) with more than a set threshold of missing data.
   - Output: `data/processed/merged_data_nohighmissing.csv`

3. **remove_high_missing_rows.py**
   - Removes rows (tuples) with more than a set threshold of missing data.
   - Output: `data/processed/merged_data_nohighmissing_rows.csv`

4. **analyze_low_variance.py**
   - Identifies features with low variance (optionally remove them).

5. **drop_correlated_features.py**
   - Removes highly correlated features based on completeness and decorrelation strategies.
   - Outputs: `merged_data_dedup.csv`, `merged_data_independent.csv`, and supporting files.

6. **analyze_completeness.py**
   - Reports the number of complete cases (rows with no missing data).

## Notes
- Adjust thresholds in each script as needed for your analysis.
- Each script can be run independently, but following the order above ensures a clean and robust dataset for modeling.
- See comments at the top of each script for more details on its function and usage.

---

For questions or improvements, please contact the project maintainer.
