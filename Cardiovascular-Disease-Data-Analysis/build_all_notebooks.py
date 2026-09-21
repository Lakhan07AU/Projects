"""
Script to programmatically generate all 5 production Jupyter Notebooks.
"""

import os
import nbformat as nbf


def build_notebook_01():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("""# 01. Data Understanding & Baseline Inspection

**Project**: Cardiovascular Disease Data Analysis & Risk Factor Insights  
**Dataset Source**: Kaggle (`sulianova/cardiovascular-disease-dataset`)  
**Author**: Senior Data Analyst / Portfolio Engineer  

---

## 1. Executive Summary & Objective
This notebook performs the initial data understanding phase on the raw Kaggle dataset. We inspect the dataset structure, shape, schema, missing values, duplicates, variable data types, and target distribution before applying any validation rules or cleaning operations.
"""),
        nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import os
import sys

# Ensure project root is in python path
sys.path.append('..')
from src.data_loader import load_raw_data

# Load raw dataset
df_raw = load_raw_data('../data/raw/cardio_train.csv')
print(f"Raw Dataset Shape: {df_raw.shape[0]:,} rows x {df_raw.shape[1]} columns")
df_raw.head()"""),
        nbf.v4.new_markdown_cell("## 2. Dataset Schema & Data Types"),
        nbf.v4.new_code_cell("""df_raw.info()"""),
        nbf.v4.new_markdown_cell("## 3. Numerical Summary Statistics"),
        nbf.v4.new_code_cell("""df_raw.describe().T"""),
        nbf.v4.new_markdown_cell("## 4. Missing Value & Duplicate Inspection"),
        nbf.v4.new_code_cell("""print("Missing Values per Feature:")
print(df_raw.isnull().sum())

print(f"\\nExact Duplicate Rows: {df_raw.duplicated().sum()}")
print(f"Duplicate Patient IDs: {df_raw['id'].duplicated().sum()}")"""),
        nbf.v4.new_markdown_cell("## 5. Categorical & Target Distributions"),
        nbf.v4.new_code_cell("""print("Target Breakdown (cardio):")
print(df_raw['cardio'].value_counts())
print("\\nPercentage breakdown (%):")
print((df_raw['cardio'].value_counts(normalize=True) * 100).round(2))"""),
        nbf.v4.new_code_cell("""print("Gender Breakdown (1 = Female, 2 = Male):")
print(df_raw['gender'].value_counts())
print((df_raw['gender'].value_counts(normalize=True) * 100).round(2))""")
    ]

    os.makedirs("notebooks", exist_ok=True)
    with open("notebooks/01_data_understanding.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Generated notebooks/01_data_understanding.ipynb")


def build_notebook_02():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("""# 02. Data Cleaning & Validation Pipeline

**Project**: Cardiovascular Disease Data Analysis  
**Goal**: Audit data quality, enforce physiological validation rules, perform feature engineering, and export `cardio_cleaned.csv`.

---

## 1. Overview & Validation Rules
We enforce five strict physiological domain boundaries:
1. `height`: `100 <= height <= 220` cm
2. `weight`: `30 <= weight <= 200` kg
3. `ap_hi` (Systolic BP): `60 <= ap_hi <= 240` mmHg
4. `ap_lo` (Diastolic BP): `40 <= ap_lo <= 160` mmHg
5. `ap_hi > ap_lo` (Systolic BP must strictly exceed Diastolic BP)

> [!IMPORTANT]
> The records failing these rules represent data entry errors / invalid records (e.g. 16000 mmHg BP), NOT statistical outliers.
"""),
        nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import sys
sys.path.append('..')

from src.data_loader import load_raw_data, save_to_sqlite
from src.data_cleaning import perform_cleaning
from src.feature_engineering import add_engineered_features

df_raw = load_raw_data('../data/raw/cardio_train.csv')
df_clean, audit = perform_cleaning(df_raw)

audit_df = pd.DataFrame([audit]).T.reset_index()
audit_df.columns = ['Metric', 'Value']
audit_df"""),
        nbf.v4.new_markdown_cell("## 2. Feature Engineering"),
        nbf.v4.new_code_cell("""df_feat = add_engineered_features(df_clean)
print("Engineered DataFrame Shape:", df_feat.shape)
df_feat[['age_years', 'age_group', 'gender_label', 'BMI', 'BMI_Category', 'Blood_Pressure_Category']].head()"""),
        nbf.v4.new_markdown_cell("## 3. Export Cleaned Dataset"),
        nbf.v4.new_code_cell("""df_feat.to_csv('../data/processed/cardio_cleaned.csv', index=False)
save_to_sqlite(df_feat, '../data/processed/cardio_db.sqlite')
print("Successfully exported cleaned CSV and SQLite database.")""")
    ]

    with open("notebooks/02_data_cleaning.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Generated notebooks/02_data_cleaning.ipynb")


def build_notebook_03():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("""# 03. Exploratory Data Analysis (EDA)

**Project**: Cardiovascular Disease Data Analysis  
**Goal**: Investigate demographic, physical, clinical, lifestyle factor distributions and their relationship with Cardiovascular Disease (`cardio`).

---
"""),
        nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys

sys.path.append('..')
from src.data_loader import load_cleaned_data
from src.analysis import compute_prevalence_by_factor

df = load_cleaned_data('../data/processed/cardio_cleaned.csv')
print(f"Loaded Cleaned Dataset: {len(df):,} records")"""),
        nbf.v4.new_markdown_cell("## 1. Age & Demographic Analysis"),
        nbf.v4.new_code_cell("""age_prev = compute_prevalence_by_factor(df, 'age_group')
age_prev"""),
        nbf.v4.new_markdown_cell("## 2. Gender vs CVD Analysis"),
        nbf.v4.new_code_cell("""gender_prev = compute_prevalence_by_factor(df, 'gender_label')
gender_prev"""),
        nbf.v4.new_markdown_cell("## 3. BMI Category vs CVD Analysis"),
        nbf.v4.new_code_cell("""bmi_prev = compute_prevalence_by_factor(df, 'BMI_Category')
bmi_prev"""),
        nbf.v4.new_markdown_cell("## 4. Blood Pressure Category vs CVD Analysis"),
        nbf.v4.new_code_cell("""bp_prev = compute_prevalence_by_factor(df, 'Blood_Pressure_Category')
bp_prev"""),
        nbf.v4.new_markdown_cell("## 5. Clinical & Lifestyle Risk Factors"),
        nbf.v4.new_code_cell("""for factor in ['Cholesterol_Level', 'Glucose_Level', 'Smoking_Status', 'Alcohol_Status', 'Physical_Activity_Status']:
    print(f"=== {factor} ===")
    display(compute_prevalence_by_factor(df, factor))""")
    ]

    with open("notebooks/03_exploratory_data_analysis.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Generated notebooks/03_exploratory_data_analysis.ipynb")


def build_notebook_04():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("""# 04. Statistical Hypothesis Testing & Outlier Analysis

**Project**: Cardiovascular Disease Data Analysis  
**Goal**: Perform formal statistical hypothesis testing (Chi-Square, Mann-Whitney U, Spearman correlations) and independent IQR outlier analysis.

---
"""),
        nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import sys
sys.path.append('..')

from src.data_loader import load_cleaned_data
from src.analysis import calculate_iqr_outliers, run_chi_square_tests, run_mann_whitney_tests

df = load_cleaned_data('../data/processed/cardio_cleaned.csv')"""),
        nbf.v4.new_markdown_cell("## 1. IQR Outlier Analysis"),
        nbf.v4.new_code_cell("""iqr_df = calculate_iqr_outliers(df)
iqr_df"""),
        nbf.v4.new_markdown_cell("## 2. Categorical Chi-Square Tests of Independence"),
        nbf.v4.new_code_cell("""chi2_df = run_chi_square_tests(df)
chi2_df"""),
        nbf.v4.new_markdown_cell("## 3. Continuous Mann-Whitney U Non-Parametric Tests"),
        nbf.v4.new_code_cell("""mwu_df = run_mann_whitney_tests(df)
mwu_df""")
    ]

    with open("notebooks/04_statistical_analysis.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Generated notebooks/04_statistical_analysis.ipynb")


def build_notebook_05():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("""# 05. Machine Learning Support Analysis

**Project**: Cardiovascular Disease Data Analysis  
**Goal**: Build interpretable classification models (Logistic Regression, Decision Tree, Random Forest, Gradient Boosting) to evaluate predictive signal and feature importance.

> [!CAUTION]
> This machine learning model is an educational supporting analysis on observational data, NOT a medical diagnostic tool.
"""),
        nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import sys
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

sys.path.append('..')
from src.data_loader import load_cleaned_data

df = load_cleaned_data('../data/processed/cardio_cleaned.csv')

feature_cols = ['age_years', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 'cholesterol', 'gluc', 'smoke', 'alco', 'active', 'BMI']
X = df[feature_cols]
y = df['cardio']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

models = {
    'Logistic Regression': (LogisticRegression(max_iter=1000, random_state=42), X_train_scaled, X_test_scaled),
    'Decision Tree': (DecisionTreeClassifier(max_depth=6, random_state=42), X_train, X_test),
    'Random Forest': (RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1), X_train, X_test),
    'Gradient Boosting': (GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42), X_train, X_test)
}

results = []
for name, (model, X_tr, X_te) in models.items():
    model.fit(X_tr, y_train)
    y_pred = model.predict(X_te)
    y_proba = model.predict_proba(X_te)[:, 1]

    results.append({
        'Model': name,
        'Accuracy': round(accuracy_score(y_test, y_pred), 4),
        'Precision': round(precision_score(y_test, y_pred), 4),
        'Recall': round(recall_score(y_test, y_pred), 4),
        'F1_Score': round(f1_score(y_test, y_pred), 4),
        'ROC_AUC': round(roc_auc_score(y_test, y_proba), 4)
    })

results_df = pd.DataFrame(results)
results_df""")
    ]

    with open("notebooks/05_machine_learning.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Generated notebooks/05_machine_learning.ipynb")


if __name__ == "__main__":
    build_notebook_01()
    build_notebook_02()
    build_notebook_03()
    build_notebook_04()
    build_notebook_05()
