# Machine Learning Suicide Rate Modeling

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.0%2B-orange)](https://scikit-learn.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive data science pipeline for predicting suicide rates using World Bank and WHO data, with a focus on interpretable machine learning models and gender-specific analysis.

## 🎯 Quick Results Summary

| Model | R² Score | MSE |
|-------|----------|-----|
| **Decision Tree** | 0.76 ± 0.02 | 12.4 ± 1.1 |
| **Lasso Regression** | 0.24 ± 0.01 | 36.8 ± 1.1 |
| **Ridge Regression** | 0.28 ± 0.03 | 34.2 ± 2.1 |

**Top Predictors**: Female labor force participation (+), Population density (-), Industrial employment (+), Electricity access (-)

![Model Comparison](comparacao_r2_modelos.png)
*Sample comparison of model performance across cross-validation folds*

## 📊 Project Overview

This project develops and evaluates machine learning models to predict suicide rates per 100,000 inhabitants using socioeconomic, demographic, and health indicators from the World Bank and WHO databases. The research emphasizes model interpretability and explores gender-specific patterns in suicide risk factors.

### Key Features

- **Multi-model approach**: Decision Trees, Lasso, Ridge, ElasticNet, and OLS regression
- **Gender-specific analysis**: Separate models for male, female, and combined populations
- **Feature interpretability**: Analysis of feature importance and split directions in decision trees
- **Country classification modeling**: Analysis by income group, region, and other classifications
- **Robust evaluation**: K-fold cross-validation with comprehensive metrics

## 🗂️ Data Sources

- **World Bank Open Data**: Socioeconomic indicators, population statistics, health expenditure
- **WHO Global Health Observatory**: Health indicators and mortality data
- **Coverage**: Multiple countries and years with extensive feature engineering

## 🔬 Methodology

### Pipeline Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   Preprocessing  │    │ Feature Eng.    │
│                 │    │                  │    │                 │
│ • World Bank    │───▶│ • Missing data   │───▶│ • Correlation   │
│ • WHO Data      │    │ • Validation     │    │ • Variance      │
│ • Country Meta  │    │ • Standardization│    │ • Selection     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Evaluation    │    │   ML Models      │    │   Dataset       │
│                 │    │                  │    │   Creation      │
│ • Cross-val     │◀───│ • Decision Tree  │◀───│                 │
│ • Metrics       │    │ • Lasso/Ridge    │    │ • Gender split  │
│ • Comparison    │    │ • ElasticNet     │    │ • Interpretable │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Data Processing Pipeline

1. **Data Extraction**: Automated fetching from World Bank and WHO APIs
2. **Feature Engineering**: Creation of interpretable features and handling missing data
3. **Feature Selection**: 
   - Correlation analysis and variance filtering
   - Selection of top 20 features for focused modeling
   - Interpretable feature subset creation
4. **Data Splitting**: Gender-specific and combined datasets

### Machine Learning Models

#### Decision Trees
- **Interpretability focus**: Feature importance with split direction analysis
- **Output**: Proportion of positive/negative splits for each feature
- **Visualization**: Tree plots and feature importance rankings

#### Regression Models
- **Lasso**: L1 regularization for feature selection
- **Ridge**: L2 regularization for coefficient shrinkage
- **ElasticNet**: Combined L1/L2 regularization
- **OLS**: Baseline linear regression

### Model Evaluation

- **Cross-validation**: 5-fold stratified cross-validation
- **Metrics**: R² score, Mean Squared Error (MSE)
- **Comparison**: Statistical comparison across models and gender groups
- **Interpretability**: Feature coefficients and importance analysis

## 📈 Key Findings

### Most Important Predictors (Interpretable Features)

| Rank | Feature | Decision Tree Importance | Lasso Coefficient | Association |
|------|---------|-------------------------|-------------------|-------------|
| 1 | Female labor force participation | 0.296 | +3.05 | Positive ⬆️ |
| 2 | Population density | 0.284 | -0.25 | Negative ⬇️ |
| 3 | Industrial employment | 0.169 | +2.65 | Positive ⬆️ |
| 4 | Electricity access | 0.137 | -2.24 | Negative ⬇️ |
| 5 | Private health expenditure | 0.115 | -0.26 | Negative ⬇️ |

### Most Important Predictors (Interpretable Features)

1. **Labor force, female (% of total labor force)**: Positive association with suicide rates
2. **Population density**: Negative association with suicide rates
3. **Employment in industry**: Positive association with suicide rates
4. **Access to electricity**: Negative association with suicide rates
5. **Domestic private health expenditure**: Mixed association

### Model Performance

- **Decision Trees**: Better interpretability, moderate predictive performance
- **Lasso Regression**: Good balance between prediction and feature selection
- **Gender differences**: Distinct patterns observed between male and female populations

### Decision Tree Split Analysis

The project introduces a novel approach to interpret decision tree splits by analyzing:
- **Proportion of positive splits**: How often a feature leads to higher predicted values
- **Proportion of negative splits**: How often a feature leads to lower predicted values
- **Sample weighting**: Consideration of sample sizes in split analysis

## 🚀 Usage

### Running Models

```bash
# Decision Tree with interpretable features
python scripts/modeling/generic_regression_crossval.py --model decision_tree --mode interpretable

# Lasso regression for all features
python scripts/modeling/generic_regression_crossval.py --model lasso --mode default

# Gender-specific modeling
python scripts/modeling/generic_regression_crossval.py --model decision_tree --gender female --mode interpretable

# Country classification analysis
python scripts/modeling/generic_regression_crossval.py --model lasso --classification_col income_group
```

### Generating Comparison Plots

```bash
python scripts/plot_comparacao_modelos.py
```

## 📁 Project Structure

```
├── data/
│   ├── raw/                    # Original data from APIs
│   ├── interim/                # Intermediate processing results
│   └── processed/              # Final datasets for modeling
├── scripts/
│   ├── data_processing/        # Data extraction and processing
│   ├── modeling/               # Machine learning models
│   └── plot_comparacao_modelos.py  # Model comparison plots
├── results/                    # Model outputs and evaluations
│   ├── decision_tree/          # Decision tree results
│   ├── lasso/                  # Lasso regression results
│   └── [other models]/
└── src/                        # Core utilities and feature selection
```

## 🔧 Requirements

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.21%2B-blue?logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-1.3%2B-green?logo=pandas&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/scikit--learn-1.0%2B-orange?logo=scikit-learn&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.5%2B-red?logo=matplotlib&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-0.11%2B-purple)

### Core Dependencies
- **Python 3.8+**
- **Data Processing**: pandas, numpy
- **Machine Learning**: scikit-learn
- **Visualization**: matplotlib, seaborn
- **API Access**: requests
- **Statistical Analysis**: scipy

Install dependencies:
```bash
pip install -r requirements.txt
```

## 📊 Outputs

### Model Results
- **Metrics**: Cross-validation R² and MSE scores
- **Feature importance**: Ranked by model-specific importance measures
- **Coefficients**: For linear models, with significance indicators
- **Visualizations**: Tree plots, feature importance charts, model comparisons

### Interpretability Analysis
- **Decision tree splits**: Detailed analysis of split directions and sample proportions
- **Feature coefficients**: Sign and magnitude analysis for linear models
- **Gender comparisons**: Differences in feature importance across populations

### Generated Files
```
results/
├── decision_tree/
│   ├── metrics.json                    # Performance metrics
│   ├── feature_importances_with_direction.csv  # Novel split analysis
│   ├── tree_plot.png                  # Decision tree visualization
│   └── fold_metrics.csv               # Per-fold performance
├── lasso/
│   ├── metrics.json
│   ├── nonzero_coefficients.csv       # Selected features
│   └── fold_metrics.csv
└── comparacao_r2_modelos.png          # Model comparison plots
```

## 🎯 Research Contributions

1. **Novel interpretability approach**: Split direction analysis for decision trees
2. **Comprehensive gender analysis**: Systematic comparison across male/female populations
3. **Multi-model evaluation**: Thorough comparison of interpretable vs. black-box approaches
4. **Scalable pipeline**: Flexible framework for similar epidemiological studies

## 🔮 Future Work

- Integration of time-series analysis for temporal patterns
- Extension to other health outcomes
- Deep learning approaches for complex pattern recognition
- Real-time prediction system development

## 👥 Author

Developed as part of machine learning research in epidemiological modeling.

---

*This research contributes to the understanding of socioeconomic factors in suicide prevention through interpretable machine learning approaches.*
