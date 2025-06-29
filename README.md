# Suicide Rates ML Project

## Structure

- `data/raw/`: Original downloaded data
- `data/interim/`: Intermediate files (partially cleaned)
- `data/processed/`: Final, ready-for-ML datasets
- `src/`: Reusable code modules
- `scripts/`: Pipeline scripts (run steps, not reusable code)
- `notebooks/`: Jupyter notebooks for exploration

## How to Run

1. Use scripts in `scripts/` to run each step of the pipeline.
2. Use functions in `src/` for reusable logic.
3. Store all data in the appropriate `data/` subfolders.

## Example Pipeline

- Fetch data: `python scripts/fetch_data.py`
- Process data: `python scripts/process_data.py`
- Analyze completeness: `python scripts/analyze_completeness.py`
- Analyze high correlation: `python scripts/analyze_high_correlation.py`
- Drop correlated features: `python scripts/drop_correlated_features.py`
