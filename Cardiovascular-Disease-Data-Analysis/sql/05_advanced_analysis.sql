-- 05_advanced_analysis.sql
-- Advanced Analytical SQL Queries using CTEs, Window Functions, Ranking, NTILE, and Conditional Aggregation

-- 1. CTE & Window Functions: Age Group Prevalence & Ranking
WITH AgeGroupStats AS (
    SELECT 
        age_group,
        COUNT(*) AS patient_count,
        SUM(cardio) AS cvd_cases,
        ROUND(AVG(cardio) * 100.0, 2) AS cvd_prevalence_pct,
        ROUND(AVG(ap_hi), 1) AS avg_systolic_bp
    FROM cardio_cleaned
    GROUP BY age_group
)
SELECT 
    age_group,
    patient_count,
    cvd_cases,
    cvd_prevalence_pct,
    avg_systolic_bp,
    RANK() OVER (ORDER BY cvd_prevalence_pct DESC) AS prevalence_rank,
    DENSE_RANK() OVER (ORDER BY avg_systolic_bp DESC) AS systolic_bp_rank
FROM AgeGroupStats;

-- 2. NTILE Window Function: Partitioning Patients into 5 Systolic BP Quartiles
WITH BpQuartiles AS (
    SELECT 
        id,
        age_years,
        ap_hi,
        cardio,
        NTILE(5) OVER (ORDER BY ap_hi ASC) AS systolic_bp_quintile
    FROM cardio_cleaned
)
SELECT 
    systolic_bp_quintile,
    COUNT(*) AS patient_count,
    MIN(ap_hi) AS min_systolic_bp,
    MAX(ap_hi) AS max_systolic_bp,
    SUM(cardio) AS cvd_cases,
    ROUND(AVG(cardio) * 100.0, 2) AS cvd_prevalence_pct
FROM BpQuartiles
GROUP BY systolic_bp_quintile
ORDER BY systolic_bp_quintile ASC;

-- 3. Complex Conditional Aggregation: Risk Profile Cohort Comparison
WITH CohortRisk AS (
    SELECT 
        gender_label,
        age_group,
        COUNT(*) AS total_patients,
        SUM(CASE WHEN Blood_Pressure_Category IN ('Hypertension Stage 2', 'Hypertensive Crisis') THEN 1 ELSE 0 END) AS high_bp_patients,
        SUM(CASE WHEN Cholesterol_Level = 'Well Above Normal' THEN 1 ELSE 0 END) AS high_cholesterol_patients,
        SUM(CASE WHEN cardio = 1 THEN 1 ELSE 0 END) AS cvd_cases
    FROM cardio_cleaned
    GROUP BY gender_label, age_group
)
SELECT 
    gender_label,
    age_group,
    total_patients,
    high_bp_patients,
    ROUND(high_bp_patients * 100.0 / total_patients, 1) AS high_bp_pct,
    high_cholesterol_patients,
    ROUND(high_cholesterol_patients * 100.0 / total_patients, 1) AS high_cholesterol_pct,
    cvd_cases,
    ROUND(cvd_cases * 100.0 / total_patients, 2) AS cvd_prevalence_pct
FROM CohortRisk
ORDER BY cvd_prevalence_pct DESC;
