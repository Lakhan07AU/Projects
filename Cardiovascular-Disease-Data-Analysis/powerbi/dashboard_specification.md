# Power BI Interactive Dashboard Layout & Page Specification

This document details the exact layout, page structure, slicers, visual configurations, and interactive features designed for the Power BI dashboard solution.

> [!NOTE]
> This specification reflects the design architecture for Power BI. The underlying dataset and calculated DAX values are derived from `data/processed/cardio_cleaned.csv`.

---

## Dashboard Architecture

```
+---------------------------------------------------------------------------------+
|                              POWER BI DASHBOARD                                 |
+-------------------+--------------------+-------------------+--------------------+
|  PAGE 1: OVERVIEW | PAGE 2: DEMOGRAPHICS| PAGE 3: HEALTH    | PAGE 4: INSIGHTS   |
|  - Executive KPIs |  - Age Pyramids    |    RISK FACTORS   |  - Risk Matrix     |
|  - Baseline Stats |  - Gender Split    |  - BP Categories  |  - Correlations    |
|  - Quick Filter   |  - BMI Categories  |  - Lifestyle Factors| - Model Ranking  |
+-------------------+--------------------+-------------------+--------------------+
```

---

## Page 1: Cardiovascular Executive Overview

### Top Header KPI Cards
1. **Total Records**: `68,636`
2. **CVD Cases**: `33,955`
3. **CVD Prevalence**: `49.47%`
4. **Average Age**: `53.3 Years`
5. **Average BMI**: `27.52 kg/m²`
6. **Average Systolic BP**: `126.6 mmHg`

### Visualizations
- **Visual 1 (Donut Chart)**: Target Balance — `No CVD (50.53%)` vs `CVD Present (49.47%)`
- **Visual 2 (Clustered Bar Chart)**: CVD Prevalence Rate by Age Group (`30-39`: 24.78%, `40-49`: 35.84%, `50-59`: 49.38%, `60+`: 64.91%)
- **Visual 3 (Stacked Column Chart)**: CVD Cases by AHA Blood Pressure Category

### Global Page Slicers
- **Gender** (`Female`, `Male`)
- **Age Group** (`30-39`, `40-49`, `50-59`, `60+`)
- **BMI Category** (`Underweight`, `Normal Weight`, `Overweight`, `Obese Class I`, `Obese Class II/III`)

---

## Page 2: Demographic Analysis

### Key Focus Areas
- **Visual 1 (Histogram & KDE)**: Age distribution by CVD status.
- **Visual 2 (Grouped Bar Chart)**: Male vs Female CVD Prevalence by Age Group.
- **Visual 3 (Treemap)**: Patient Breakdown across BMI Categories and Gender.

---

## Page 3: Health Risk Factors

### Key Focus Areas
- **Visual 1 (Column Chart)**: CVD Prevalence by AHA Blood Pressure Category (Normal 13.43% -> Hypertensive Crisis 83.33%).
- **Visual 2 (Bar Chart)**: CVD Prevalence by Cholesterol Level (Normal 43.53% -> Well Above Normal 76.54%).
- **Visual 3 (Side-by-side Bar)**: Impact of Smoking and Alcohol on CVD Prevalence.
- **Visual 4 (Bar Chart)**: Physical Activity Status vs CVD Prevalence (Active 48.73% vs Inactive 52.53%).

---

## Page 4: Correlation & Risk Insights

### Key Focus Areas
- **Visual 1 (Matrix Table)**: Multi-Factor CVD Prevalence Matrix (Age Group x BP Category x Cholesterol).
- **Visual 2 (Bar Chart)**: Feature Importance Ranking derived from Random Forest machine learning support analysis.
- **Visual 3 (Scatter Plot)**: Systolic vs Diastolic Blood Pressure colored by CVD presence.
