# Analytical Findings & Risk Factor Insights

This report details the primary findings derived from analyzing the cleaned dataset of 68,636 patient records. Every finding follows a structured, neutral analytical format.

---

### Finding 1: Blood Pressure Classification & CVD Risk
- **Question**: How does cardiovascular disease (CVD) prevalence vary across AHA Blood Pressure categories?
- **Observation**: CVD prevalence increases dramatically with higher blood pressure stages, rising from normal blood pressure up to hypertensive crisis.
- **Metric**: Patients with Normal BP exhibit a **22.14%** CVD rate, whereas patients with Hypertension Stage 2 exhibit a **77.64%** CVD rate, and Hypertensive Crisis reaches **86.49%**.
- **Interpretation**: Systolic and diastolic blood pressures demonstrate the strongest statistical association with CVD presence among all features analyzed (Cramér's V = 0.4265, p < 0.0001).
- **Limitation**: Observational dataset; blood pressure readings represent point-in-time measurements rather than longitudinal clinical monitoring.

---

### Finding 2: Age Progression & CVD Risk
- **Question**: How does CVD prevalence vary across age groups?
- **Observation**: CVD prevalence displays a strict positive monotonic trend across age decades.
- **Metric**: CVD rate is **24.18%** for patients aged 30–39, **37.36%** for 40–49, **51.05%** for 50–59, and **66.70%** for patients aged 60+.
- **Interpretation**: Age is a fundamental demographic risk factor (Chi2 = 3119.53, Cramér's V = 0.2132, p < 0.0001), with CVD prevalence nearly tripling from the 30s to 60+.
- **Limitation**: Cross-sectional data snapshot; cannot track individual patient disease progression over time.

---

### Finding 3: Cholesterol Level Association
- **Question**: How does cholesterol level impact CVD prevalence?
- **Observation**: Elevated cholesterol levels are associated with significantly higher CVD occurrence.
- **Metric**: Patients with Normal cholesterol have a **43.54%** CVD rate, Above Normal reaches **59.63%**, and Well Above Normal reaches **76.26%** (a 32.72% absolute rate increase).
- **Interpretation**: Serum cholesterol exhibits a strong positive relationship with CVD (Cramér's V = 0.2214, p < 0.0001), serving as a crucial secondary risk indicator.
- **Limitation**: Categorical representation (1, 2, 3) in original dataset without explicit mg/dL laboratory values.

---

### Finding 4: Body Mass Index (BMI) & Obesity Gradient
- **Question**: How does CVD prevalence change across BMI classification categories?
- **Observation**: CVD prevalence increases consistently from Normal Weight to severe Obesity bands.
- **Metric**: CVD rate is **39.73%** in Normal Weight patients, **50.54%** in Overweight patients, **59.86%** in Obese Class I, and **67.63%** in Obese Class II/III.
- **Interpretation**: Adiposity as measured by BMI shows a statistically significant positive relationship with CVD (Cramér's V = 0.1873, p < 0.0001).
- **Limitation**: BMI does not distinguish between visceral fat mass and skeletal muscle mass.

---

### Finding 5: Gender Comparison Baseline
- **Question**: Is there a significant baseline difference in CVD prevalence between female and male cohorts?
- **Observation**: CVD prevalence is nearly identical between female and male cohorts across the overall dataset.
- **Metric**: Female CVD prevalence is **49.21%** (22,000 / 44,708), while Male CVD prevalence is **49.96%** (11,955 / 23,928).
- **Interpretation**: Gender alone shows minimal bivariate association with CVD baseline presence (Chi2 = 3.52, p = 0.0608, Cramér's V = 0.0072).
- **Limitation**: Does not account for potential differences in age distribution between genders within specific age sub-cohorts.

---

### Finding 6: Physical Activity Protective Observed Pattern
- **Question**: How does physical activity status correlate with observed CVD rates?
- **Observation**: Physically active patients show a lower observed CVD prevalence compared to inactive patients.
- **Metric**: Inactive patients exhibit a **53.27%** CVD rate, whereas Active patients exhibit a **48.54%** CVD rate (a 4.73% absolute reduction).
- **Interpretation**: Physical activity shows a statistically significant inverse association with CVD (Chi2 = 96.68, p < 0.0001, Cramér's V = 0.0375).
- **Limitation**: Self-reported binary activity flag without quantitative duration or intensity tracking.
