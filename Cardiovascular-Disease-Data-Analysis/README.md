# Cardiovascular Disease Data Analysis & Risk Factor Insights

A production-grade, end-to-end **Data Analytics & Machine Learning Portfolio Project** evaluating cardiovascular disease (CVD) risk factors across **70,000 real patient records**.

---

## Executive Summary & Analytical Objective

The primary objective of this project is to perform rigorous observational data analytics, statistical hypothesis testing, SQL query analytics, publication-quality visualizations, and interpretable machine learning support analysis on Kaggle's Cardiovascular Disease Dataset.

Unlike generic classification projects that treat predictive modeling as a black box, this repository focuses on **Data Analyst best practices**: explicit quality control auditing, separation of physiological validation failures from statistical outliers, non-parametric hypothesis testing, complex SQL window functions, and business interpretation.

```
RAW DATA (70,000) -> DATA CLEANING (68,636) -> FEATURE ENGINEERING -> STATISTICAL ANALYSIS -> SQL SUITE -> ML SUPPORT -> INSIGHTS
```

---

## Dataset Attribution & Source

- **Dataset**: Cardiovascular Disease Dataset
- **Author / Credit**: Svetlana Ulianova (Kaggle)
- **Kaggle Source**: [https://www.kaggle.com/datasets/sulianova/cardiovascular-disease-dataset](https://www.kaggle.com/datasets/sulianova/cardiovascular-disease-dataset)
- **License**: Open Data Commons Attribution License (ODC-By)

---

## Dataset Description & Data Dictionary

The raw dataset contains **70,000 records** and **13 features**:

| Feature | Data Type | Unit / Range | Description / Kaggle Definition |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Identifier | Patient unique identifier key |
| `age` | Integer | Days | Age of patient in days (converted to `age_years`) |
| `gender` | Integer | 1: Female, 2: Male | Biological gender (Gender 1 mean height 161.4 cm; Gender 2 mean height 169.9 cm) |
| `height` | Integer | cm | Height in centimeters |
| `weight` | Float | kg | Weight in kilograms |
| `ap_hi` | Integer | mmHg | Systolic blood pressure |
| `ap_lo` | Integer | mmHg | Diastolic blood pressure |
| `cholesterol` | Integer | 1: Normal, 2: Above Normal, 3: Well Above Normal | Serum cholesterol level |
| `gluc` | Integer | 1: Normal, 2: Above Normal, 3: Well Above Normal | Glucose level |
| `smoke` | Integer | 0: Non-Smoker, 1: Smoker | Binary smoking status flag |
| `alco` | Integer | 0: Non-Drinker, 1: Drinker | Binary alcohol consumption flag |
| `active` | Integer | 0: Inactive, 1: Active | Binary physical activity flag |
| `cardio` | Integer | 0: Absence, 1: Presence of CVD | Target binary outcome variable |

---

## Data Cleaning & Validation Audit

We applied 5 strict domain boundary validation rules to screen out impossible data entry errors:
1. `height`: `100 <= height <= 220` cm
2. `weight`: `30 <= weight <= 200` kg
3. `ap_hi` (Systolic BP): `60 <= ap_hi <= 240` mmHg
4. `ap_lo` (Diastolic BP): `40 <= ap_lo <= 160` mmHg
5. `ap_hi > ap_lo` (Systolic BP strictly greater than Diastolic BP)

### Data Quality Audit Breakdown

| Cleaning Metric | Record Count / Value | Percentage (%) |
| :--- | :--- | :--- |
| **Total Raw Records** | **70,000** | **100.00%** |
| **Missing Values** | 0 | 0.00% |
| **Exact Duplicate Rows** | 0 | 0.00% |
| **Invalid Height Records** (<100 or >220 cm) | 30 | 0.04% |
| **Invalid Weight Records** (<30 or >200 kg) | 7 | 0.01% |
| **Invalid Systolic BP Records** (<60 or >240 mmHg) | 228 | 0.33% |
| **Invalid Diastolic BP Records** (<40 or >160 mmHg) | 1,025 | 1.46% |
| **Invalid BP Relationship Records** (`ap_hi <= ap_lo`) | 1,236 | 1.77% |
| **Multiple-Rule Violations** | 1,155 | 1.65% |
| **Total Excluded Records (Validation Failures)** | **1,364** | **1.95%** |
| **Final Retained Clean Records** | **68,636** | **98.05%** |

> [!IMPORTANT]
> The excluded 1,364 records represent physiological data entry errors (e.g. Systolic BP = 16,000 mmHg), NOT statistical outliers. Statistical outliers were analyzed separately using IQR boundaries.

---

## Feature Engineering

We engineered 11 analytical features without altering original raw fields:
- `age_years`: `(age / 365.25).round(1)`
- `age_group`: Decades (`30-39`, `40-49`, `50-59`, `60+`)
- `gender_label`: `Female` (1), `Male` (2)
- `BMI`: `weight / (height / 100)^2`
- `BMI_Category`: WHO bands (`Underweight`, `Normal Weight`, `Overweight`, `Obese Class I`, `Obese Class II/III`)
- `Blood_Pressure_Category`: AHA/ACC Guidelines (`Normal`, `Elevated`, `Hypertension Stage 1`, `Hypertension Stage 2`, `Hypertensive Crisis`)
- Categorical mappings for `Cholesterol_Level`, `Glucose_Level`, `Smoking_Status`, `Alcohol_Status`, `Physical_Activity_Status`.

---

## Exploratory Data Analysis & Visualizations

| Chart File | Visualization Description | Key Finding |
| :--- | :--- | :--- |
| `visualizations/01_age_distribution.png` | Age distribution by CVD status | CVD cases shift significantly towards older age brackets. |
| `visualizations/03_cvd_prevalence.png` | CVD baseline target prevalence | 50.53% No CVD vs 49.47% CVD Present (clean baseline). |
| `visualizations/05_bmi_vs_cvd.png` | CVD rate across BMI Categories | Monotonic increase: Normal Weight (39.73%) -> Obese Class II/III (67.63%). |
| `visualizations/07_bp_vs_cvd.png` | CVD rate by AHA BP Category | Sharp risk jump: Normal BP (22.14%) -> Stage 2 Hypertension (77.64%). |
| `visualizations/08_cholesterol_vs_cvd.png` | CVD rate by Cholesterol Level | Normal (43.54%) -> Well Above Normal (76.26%). |
| `visualizations/12_correlation_heatmap.png` | Spearman Rank Correlation Heatmap | `ap_hi`, `ap_lo`, `age_years`, and `cholesterol` display strongest rank correlation. |
| `visualizations/14_model_comparison.png` | Machine Learning Model Performance | Gradient Boosting achieves 73.25% accuracy and 0.8031 ROC-AUC. |

---

## Statistical Analysis & Hypothesis Testing

| Categorical Factor | Chi-Square ($\chi^2$) | p-value | Degrees of Freedom | Cramér's V Effect Size | Statistical Significance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Blood Pressure Category** | **12,486.85** | **< 0.0001** | 4 | **0.4265** | Significant |
| **Cholesterol Level** | **3,365.53** | **< 0.0001** | 2 | **0.2214** | Significant |
| **Age Group** | **3,119.53** | **< 0.0001** | 3 | **0.2132** | Significant |
| **BMI Category** | **2,407.27** | **< 0.0001** | 4 | **0.1873** | Significant |
| **Glucose Level** | **578.93** | **< 0.0001** | 2 | **0.0918** | Significant |
| **Physical Activity** | **96.68** | **< 0.0001** | 1 | **0.0375** | Significant |
| **Smoking Status** | **18.15** | **< 0.0001** | 1 | **0.0163** | Significant |
| **Gender Label** | **3.52** | **0.0608** | 1 | **0.0072** | Not Significant |

---

## Machine Learning Support Analysis

Models were evaluated on a 20% holdout test set (13,728 records):

| Model Name | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression** | 72.70% | 75.27% | 66.74% | 70.75% | 0.7923 |
| **Decision Tree (depth=6)** | 72.93% | 75.59% | 66.88% | 70.97% | 0.7943 |
| **Random Forest (depth=10)** | **73.28%** | **75.70%** | 67.72% | 71.49% | 0.8017 |
| **Gradient Boosting** | 73.25% | 74.96% | **68.96%** | **71.84%** | **0.8031** |

---

## Project Structure

```
Cardiovascular-Disease-Data-Analysis/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── data/
│   ├── raw/
│   │   └── cardio_train.csv
│   ├── processed/
│   │   ├── cardio_cleaned.csv
│   │   └── cardio_db.sqlite
│   └── data_dictionary.csv
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_exploratory_data_analysis.ipynb
│   ├── 04_statistical_analysis.ipynb
│   └── 05_machine_learning.ipynb
├── src/
│   ├── data_loader.py
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   ├── analysis.py
│   └── visualization.py
├── sql/
│   ├── 01_data_quality.sql
│   ├── 02_demographic_analysis.sql
│   ├── 03_health_metrics_analysis.sql
│   ├── 04_risk_factor_analysis.sql
│   └── 05_advanced_analysis.sql
├── visualizations/
├── models/
├── powerbi/
│   ├── data_model.md
│   ├── dax_measures.md
│   └── dashboard_specification.md
└── reports/
    ├── methodology.md
    ├── insights.md
    ├── limitations.md
    ├── interview_questions.md
    └── project_explanation.md
```

---

## Installation & Reproducibility

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/username/Cardiovascular-Disease-Data-Analysis.git
cd Cardiovascular-Disease-Data-Analysis
pip install -r requirements.txt
```

### 2. Execute Data Pipeline & Visualizations
```bash
python -c "
from src.data_loader import load_raw_data, save_to_sqlite
from src.data_cleaning import perform_cleaning
from src.feature_engineering import add_engineered_features
from src.visualization import create_all_visualizations

df_raw = load_raw_data()
df_clean, audit = perform_cleaning(df_raw)
df_feat = add_engineered_features(df_clean)
df_feat.to_csv('data/processed/cardio_cleaned.csv', index=False)
save_to_sqlite(df_feat)
create_all_visualizations(df_feat)
"
```

### 3. Run Notebooks
```bash
python -m nbconvert --to notebook --execute notebooks/*.ipynb --inplace
```

---

## Ethical & Medical Disclaimer

> [!CAUTION]
> This repository is an educational data-analysis and machine-learning portfolio project built on observational data. It is **not a medical diagnostic tool** and should not be used to guide individual healthcare treatment decisions.

---

## Author & License

- **Author**: Senior Data Analyst / Data Scientist
- **License**: MIT License
