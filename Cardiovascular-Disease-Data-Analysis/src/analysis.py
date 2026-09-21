"""
Statistical Analysis and Risk Factor Aggregation Module
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, List


def calculate_iqr_outliers(df: pd.DataFrame, continuous_cols: List[str] = None) -> pd.DataFrame:
    """
    Computes IQR, Q1, Q3, Lower Bound, Upper Bound, Outlier Count, and % Affected
    for specified continuous variables.
    """
    if continuous_cols is None:
        continuous_cols = ['age_years', 'height', 'weight', 'BMI', 'ap_hi', 'ap_lo']

    records = []
    total_len = len(df)

    for col in continuous_cols:
        q1 = float(df[col].quantile(0.25))
        q3 = float(df[col].quantile(0.75))
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers_count = int(((df[col] < lower_bound) | (df[col] > upper_bound)).sum())
        pct_affected = round((outliers_count / total_len) * 100, 2)

        records.append({
            "variable": col,
            "q1": round(q1, 2),
            "q3": round(q3, 2),
            "iqr": round(iqr, 2),
            "lower_bound": round(lower_bound, 2),
            "upper_bound": round(upper_bound, 2),
            "outliers_count": outliers_count,
            "pct_affected": pct_affected
        })

    return pd.DataFrame(records)


def compute_prevalence_by_factor(df: pd.DataFrame, factor_col: str) -> pd.DataFrame:
    """
    Computes total records, CVD cases, non-CVD cases, and CVD prevalence rate (%) for a factor.
    """
    grouped = df.groupby(factor_col).agg(
        total_count=('cardio', 'count'),
        cvd_cases=('cardio', 'sum')
    ).reset_index()

    grouped['non_cvd_cases'] = grouped['total_count'] - grouped['cvd_cases']
    grouped['cvd_prevalence_pct'] = ((grouped['cvd_cases'] / grouped['total_count']) * 100).round(2)
    overall_prev = (df['cardio'].sum() / len(df)) * 100
    grouped['difference_from_baseline_pct'] = (grouped['cvd_prevalence_pct'] - overall_prev).round(2)
    return grouped.sort_values(by='cvd_prevalence_pct', ascending=False)


def run_chi_square_tests(df: pd.DataFrame, cat_cols: List[str] = None) -> pd.DataFrame:
    """
    Runs Chi-Square Test of Independence for categorical variables against cardio.
    Calculates Chi2, p-value, Degrees of Freedom, and Cramér's V effect size.
    """
    if cat_cols is None:
        cat_cols = [
            'Blood_Pressure_Category', 'Cholesterol_Level', 'age_group', 
            'BMI_Category', 'Glucose_Level', 'Physical_Activity_Status', 
            'Smoking_Status', 'Alcohol_Status', 'gender_label'
        ]

    results = []
    n = len(df)

    for col in cat_cols:
        contingency = pd.crosstab(df[col], df['cardio'])
        chi2, p_val, dof, _ = stats.chi2_contingency(contingency)
        min_dim = min(contingency.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0.0

        results.append({
            "factor": col,
            "chi2_statistic": round(chi2, 2),
            "p_value": p_val,
            "p_value_formatted": "< 0.0001" if p_val < 0.0001 else f"{p_val:.4f}",
            "degrees_of_freedom": dof,
            "cramers_v": round(cramers_v, 4),
            "statistical_significance": "Significant (p < 0.05)" if p_val < 0.05 else "Not Significant"
        })

    res_df = pd.DataFrame(results).sort_values(by='cramers_v', ascending=False)
    return res_df


def run_mann_whitney_tests(df: pd.DataFrame, cont_cols: List[str] = None) -> pd.DataFrame:
    """
    Runs Mann-Whitney U test comparing feature values between CVD (1) and non-CVD (0) groups.
    Calculates U statistic, p-value, group medians, and Rank-Biserial Correlation effect size.
    """
    if cont_cols is None:
        cont_cols = ['age_years', 'ap_hi', 'ap_lo', 'BMI', 'weight', 'height']

    results = []
    no_cvd = df[df['cardio'] == 0]
    cvd = df[df['cardio'] == 1]
    n1, n2 = len(no_cvd), len(cvd)

    for col in cont_cols:
        stat, p_val = stats.mannwhitneyu(cvd[col], no_cvd[col], alternative='two-sided')
        # Rank-biserial correlation = 1 - (2*U)/(n1*n2)
        rank_biserial = 1.0 - (2.0 * stat) / (n1 * n2)

        results.append({
            "variable": col,
            "no_cvd_median": round(float(no_cvd[col].median()), 2),
            "cvd_median": round(float(cvd[col].median()), 2),
            "u_statistic": round(float(stat), 1),
            "p_value": p_val,
            "p_value_formatted": "< 0.0001" if p_val < 0.0001 else f"{p_val:.4f}",
            "rank_biserial_effect_size": round(float(rank_biserial), 4)
        })

    return pd.DataFrame(results).sort_values(by='rank_biserial_effect_size', ascending=False)
