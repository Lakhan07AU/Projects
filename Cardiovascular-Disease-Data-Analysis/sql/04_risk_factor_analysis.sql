-- 04_risk_factor_analysis.sql
-- Clinical & Lifestyle Risk Factor Analysis: Cholesterol, Glucose, Smoking, Alcohol, Activity

-- 1. CVD Prevalence by Cholesterol Level
SELECT 
    Cholesterol_Level,
    COUNT(*) AS total_patients,
    SUM(cardio) AS cvd_cases,
    ROUND(AVG(cardio) * 100.0, 2) AS cvd_prevalence_pct
FROM cardio_cleaned
GROUP BY Cholesterol_Level
ORDER BY cvd_prevalence_pct DESC;

-- 2. CVD Prevalence by Glucose Level
SELECT 
    Glucose_Level,
    COUNT(*) AS total_patients,
    SUM(cardio) AS cvd_cases,
    ROUND(AVG(cardio) * 100.0, 2) AS cvd_prevalence_pct
FROM cardio_cleaned
GROUP BY Glucose_Level
ORDER BY cvd_prevalence_pct DESC;

-- 3. CVD Prevalence by Smoking Status
SELECT 
    Smoking_Status,
    COUNT(*) AS total_patients,
    SUM(cardio) AS cvd_cases,
    ROUND(AVG(cardio) * 100.0, 2) AS cvd_prevalence_pct
FROM cardio_cleaned
GROUP BY Smoking_Status;

-- 4. CVD Prevalence by Alcohol Consumption Status
SELECT 
    Alcohol_Status,
    COUNT(*) AS total_patients,
    SUM(cardio) AS cvd_cases,
    ROUND(AVG(cardio) * 100.0, 2) AS cvd_prevalence_pct
FROM cardio_cleaned
GROUP BY Alcohol_Status;

-- 5. CVD Prevalence by Physical Activity Status
SELECT 
    Physical_Activity_Status,
    COUNT(*) AS total_patients,
    SUM(cardio) AS cvd_cases,
    ROUND(AVG(cardio) * 100.0, 2) AS cvd_prevalence_pct
FROM cardio_cleaned
GROUP BY Physical_Activity_Status;

-- 6. Multi-Factor Risk Burden Combination Analysis
SELECT 
    Cholesterol_Level,
    Glucose_Level,
    Smoking_Status,
    COUNT(*) AS patient_count,
    SUM(cardio) AS cvd_cases,
    ROUND(AVG(cardio) * 100.0, 2) AS cvd_prevalence_pct
FROM cardio_cleaned
GROUP BY Cholesterol_Level, Glucose_Level, Smoking_Status
ORDER BY cvd_prevalence_pct DESC;
