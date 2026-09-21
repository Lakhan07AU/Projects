-- 02_demographic_analysis.sql
-- Demographic Breakdown & CVD Prevalence across Age and Gender

-- 1. CVD Prevalence by Gender
SELECT 
    gender_label,
    COUNT(*) AS total_patients,
    SUM(cardio) AS cvd_cases,
    COUNT(*) - SUM(cardio) AS non_cvd_cases,
    ROUND(AVG(cardio) * 100.0, 2) AS cvd_prevalence_pct,
    ROUND(AVG(age_years), 1) AS avg_age_years,
    ROUND(AVG(BMI), 2) AS avg_bmi
FROM cardio_cleaned
GROUP BY gender_label
ORDER BY cvd_prevalence_pct DESC;

-- 2. CVD Prevalence by Age Group
SELECT 
    age_group,
    COUNT(*) AS total_patients,
    SUM(cardio) AS cvd_cases,
    ROUND(AVG(cardio) * 100.0, 2) AS cvd_prevalence_pct,
    ROUND(AVG(ap_hi), 1) AS avg_systolic_bp,
    ROUND(AVG(ap_lo), 1) AS avg_diastolic_bp
FROM cardio_cleaned
GROUP BY age_group
ORDER BY age_group ASC;

-- 3. Cross-demographic Analysis: Age Group and Gender Matrix
SELECT 
    age_group,
    gender_label,
    COUNT(*) AS total_patients,
    SUM(cardio) AS cvd_cases,
    ROUND(AVG(cardio) * 100.0, 2) AS cvd_prevalence_pct
FROM cardio_cleaned
GROUP BY age_group, gender_label
ORDER BY age_group ASC, gender_label ASC;
