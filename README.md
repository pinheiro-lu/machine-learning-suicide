# Machine Learning Suicide Rate Modeling

A comprehensive data science pipeline for predicting suicide rates using World Bank and WHO data, with a focus on interpretable machine learning models and gender-specific analysis.

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

- Python 3.8+
- pandas, numpy, scikit-learn
- matplotlib, seaborn
- requests (for API data fetching)

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

## 📝 License

This project is developed for academic research purposes. Please cite appropriately if using components of this work.

## 👥 Author

Developed as part of machine learning research in epidemiological modeling.

---

*This research contributes to the understanding of socioeconomic factors in suicide prevention through interpretable machine learning approaches.*
