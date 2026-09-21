# Project Methodology & Technical Documentation

## 1. Data Collection & Baseline Verification
The raw dataset was sourced directly from Kaggle (`sulianova/cardiovascular-disease-dataset`). It contains **70,000 raw patient records** across 13 clinical and demographic features.

### Raw Data Integrity Check
- **Row Count**: 70,000
- **Missing Values**: 0 across all features
- **Duplicate Records**: 0
- **Target Distribution**: 35,021 No CVD (50.03%), 34,979 CVD Present (49.97%)

---

## 2. Data Cleaning & Validation Rules
Data entry errors and unphysiological records were filtered using strict domain logic:
1. `height`: `100 <= height <= 220` cm
2. `weight`: `30 <= weight <= 200` kg
3. `ap_hi` (Systolic BP): `60 <= ap_hi <= 240` mmHg
4. `ap_lo` (Diastolic BP): `40 <= ap_lo <= 160` mmHg
5. `ap_hi > ap_lo` (Systolic BP strictly greater than Diastolic BP)

### Cleaning Audit Results
- **Raw Records**: 70,000
- **Excluded Records**: 1,364 (1.95%)
- **Cleaned Retained Records**: 68,636 (98.05%)
- **Cleaned Target Breakdown**: 34,681 No CVD (50.53%), 33,955 CVD Present (49.47%)

---

## 3. Statistical Analysis Methodology
1. **IQR Statistical Outlier Analysis**: Quantified extreme values for height, weight, BMI, systolic BP, and diastolic BP without automatic deletion.
2. **Chi-Square Test of Independence**: Tested categorical variable independence against `cardio`. Effect size measured using **Cramér's V**.
3. **Mann-Whitney U Non-Parametric Test**: Evaluated continuous feature differences between CVD and non-CVD cohorts. Effect size measured using **Rank-Biserial Correlation**.
4. **Correlation Heatmap**: Constructed using **Spearman Rank Correlation** to accommodate ordinal and non-normally distributed features.

---

## 4. Machine Learning Modeling Framework
Four classification algorithms were trained using stratified 80/20 train/test splitting:
1. **Logistic Regression** (Standardized inputs)
2. **Decision Tree Classifier** (`max_depth = 6`)
3. **Random Forest Classifier** (`n_estimators = 100`, `max_depth = 10`)
4. **Gradient Boosting Classifier** (`n_estimators = 100`, `learning_rate = 0.1`)

Models were evaluated across Accuracy, Precision, Recall, F1-Score, ROC-AUC, and Confusion Matrix metrics.
