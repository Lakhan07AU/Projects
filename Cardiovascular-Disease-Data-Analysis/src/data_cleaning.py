"""
Data Cleaning Module for Cardiovascular Disease Data Analysis
"""

import pandas as pd
from typing import Tuple, Dict, Any


def validate_schema(df: pd.DataFrame) -> bool:
    """
    Verify expected columns and types exist in raw dataframe.
    """
    expected_cols = [
        "id", "age", "gender", "height", "weight", 
        "ap_hi", "ap_lo", "cholesterol", "gluc", 
        "smoke", "alco", "active", "cardio"
    ]
    missing = [col for col in expected_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in dataset: {missing}")
    return True


def perform_cleaning(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Applies data quality and validation rules to the raw cardiovascular dataset.
    Returns cleaned DataFrame and detailed audit dictionary.
    """
    validate_schema(df)
    
    total_raw = len(df)
    missing_records = int(df.isnull().any(axis=1).sum())
    duplicate_records = int(df.duplicated().sum())

    # Validation condition masks
    invalid_height = ((df['height'] < 100) | (df['height'] > 220))
    invalid_weight = ((df['weight'] < 30) | (df['weight'] > 200))
    invalid_ap_hi = ((df['ap_hi'] < 60) | (df['ap_hi'] > 240))
    invalid_ap_lo = ((df['ap_lo'] < 40) | (df['ap_lo'] > 160))
    invalid_bp_relation = (df['ap_hi'] <= df['ap_lo'])

    all_invalid_mask = invalid_height | invalid_weight | invalid_ap_hi | invalid_ap_lo | invalid_bp_relation
    violations_count = (
        invalid_height.astype(int) + 
        invalid_weight.astype(int) + 
        invalid_ap_hi.astype(int) + 
        invalid_ap_lo.astype(int) + 
        invalid_bp_relation.astype(int)
    )

    multiple_violations = int((violations_count > 1).sum())
    total_excluded = int(all_invalid_mask.sum())
    total_retained = total_raw - total_excluded

    cleaned_df = df[~all_invalid_mask].copy()

    audit_report = {
        "total_raw_records": total_raw,
        "missing_records": missing_records,
        "duplicate_records": duplicate_records,
        "invalid_height_records": int(invalid_height.sum()),
        "invalid_weight_records": int(invalid_weight.sum()),
        "invalid_systolic_bp_records": int(invalid_ap_hi.sum()),
        "invalid_diastolic_bp_records": int(invalid_ap_lo.sum()),
        "invalid_bp_relationship_records": int(invalid_bp_relation.sum()),
        "multiple_rule_violations": multiple_violations,
        "final_excluded_records": total_excluded,
        "final_retained_records": total_retained,
        "retention_rate_pct": round((total_retained / total_raw) * 100, 2),
        "exclusion_rate_pct": round((total_excluded / total_raw) * 100, 2)
    }

    return cleaned_df, audit_report
