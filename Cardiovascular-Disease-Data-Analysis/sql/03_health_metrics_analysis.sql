-- 03_health_metrics_analysis.sql
-- Health Metrics Analysis: BMI Categories and Blood Pressure Classification

-- 1. CVD Prevalence by BMI Category
SELECT 
    BMI_Category,
    COUNT(*) AS patient_count,
    SUM(cardio) AS cvd_cases,
    ROUND(AVG(cardio) * 100.0, 2) AS cvd_prevalence_pct,
    ROUND(AVG(weight), 1) AS avg_weight_kg,
    ROUND(AVG(BMI), 2) AS avg_bmi
FROM cardio_cleaned
GROUP BY BMI_Category
ORDER BY cvd_prevalence_pct DESC;

-- 2. CVD Prevalence by AHA Blood Pressure Category
SELECT 
    Blood_Pressure_Category,
    COUNT(*) AS patient_count,
    SUM(cardio) AS cvd_cases,
    ROUND(AVG(cardio) * 100.0, 2) AS cvd_prevalence_pct,
    ROUND(AVG(ap_hi), 1) AS avg_systolic_bp,
    ROUND(AVG(ap_lo), 1) AS avg_diastolic_bp
FROM cardio_cleaned
GROUP BY Blood_Pressure_Category
ORDER BY cvd_prevalence_pct DESC;

-- 3. Cross-Tabulation: BMI Category vs Blood Pressure Category
SELECT 
    BMI_Category,
    Blood_Pressure_Category,
    COUNT(*) AS patient_count,
    SUM(cardio) AS cvd_cases,
    ROUND(AVG(cardio) * 100.0, 2) AS cvd_prevalence_pct
FROM cardio_cleaned
GROUP BY BMI_Category, Blood_Pressure_Category
HAVING COUNT(*) >= 100
ORDER BY cvd_prevalence_pct DESC;
