# Data Analytics & Methodological Limitations

This document outlines key limitations, assumptions, and analytical constraints inherent to this study.

---

## 1. Observational Study Design & Causation
> [!WARNING]
> This analysis is strictly observational. No findings, statistical significance tests, or correlation metrics establish direct clinical causation. All relationships must be interpreted as observational associations.

---

## 2. Dataset Constraints & Measurement Granularity

### Point-in-Time Cross-Sectional Data
- The dataset represents a single static snapshot per patient. Longitudinal data tracking individual disease progression over time is unavailable.

### Self-Reported Behavioral Variables
- Features such as `smoke` (smoking status), `alco` (alcohol intake), and `active` (physical activity) are binary self-reported flags without dosage, frequency, or duration metrics.

### Ordinal Categorical Clinical Indicators
- `cholesterol` and `gluc` (glucose) are coded as 1 (Normal), 2 (Above Normal), 3 (Well Above Normal) rather than quantitative continuous mg/dL blood concentration measurements.

---

## 3. Scope of Machine Learning Models
- ML models (Logistic Regression, Decision Tree, Random Forest, Gradient Boosting) achieved test accuracy between **72.7% and 73.3%** and ROC-AUC between **0.792 and 0.803**.
- Models serve strictly as an analytical supporting component to identify feature predictive importance and pattern recognition within this dataset.
- **Not for Clinical Diagnosis**: These models must not be used as medical diagnostic tools or for healthcare treatment decision-making.
