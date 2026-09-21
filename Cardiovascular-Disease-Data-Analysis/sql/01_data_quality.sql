-- 01_data_quality.sql
-- Data Quality Auditing and Integrity Verification Queries

-- 1. Total record count and target distribution
SELECT 
    COUNT(*) AS total_records,
    SUM(CASE WHEN cardio = 0 THEN 1 ELSE 0 END) AS no_cvd_count,
    SUM(CASE WHEN cardio = 1 THEN 1 ELSE 0 END) AS cvd_count,
    ROUND(AVG(cardio) * 100.0, 2) AS overall_cvd_prevalence_pct
FROM cardio_cleaned;

-- 2. Null value and boundary validation check
SELECT
    SUM(CASE WHEN id IS NULL THEN 1 ELSE 0 END) AS missing_ids,
    SUM(CASE WHEN age_years IS NULL THEN 1 ELSE 0 END) AS missing_age,
    SUM(CASE WHEN height IS NULL THEN 1 ELSE 0 END) AS missing_height,
    SUM(CASE WHEN weight IS NULL THEN 1 ELSE 0 END) AS missing_weight,
    SUM(CASE WHEN ap_hi IS NULL THEN 1 ELSE 0 END) AS missing_ap_hi,
    SUM(CASE WHEN ap_lo IS NULL THEN 1 ELSE 0 END) AS missing_ap_lo
FROM cardio_cleaned;

-- 3. Minimum, Maximum, and Average physical/clinical metrics
SELECT
    ROUND(MIN(age_years), 1) AS min_age_years,
    ROUND(AVG(age_years), 1) AS avg_age_years,
    ROUND(MAX(age_years), 1) AS max_age_years,
    MIN(height) AS min_height_cm,
    ROUND(AVG(height), 1) AS avg_height_cm,
    MAX(height) AS max_height_cm,
    MIN(weight) AS min_weight_kg,
    ROUND(AVG(weight), 1) AS avg_weight_kg,
    MAX(weight) AS max_weight_kg,
    ROUND(AVG(BMI), 2) AS avg_bmi,
    ROUND(AVG(ap_hi), 1) AS avg_systolic_bp,
    ROUND(AVG(ap_lo), 1) AS avg_diastolic_bp
FROM cardio_cleaned;
