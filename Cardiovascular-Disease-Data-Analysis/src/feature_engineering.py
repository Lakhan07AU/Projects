"""
Feature Engineering Module for Cardiovascular Disease Data Analysis
"""

import pandas as pd
import numpy as np


def compute_bmi(weight_kg: pd.Series, height_cm: pd.Series) -> pd.Series:
    """
    Computes Body Mass Index (BMI): weight (kg) / height (m)^2
    """
    height_m = height_cm / 100.0
    return (weight_kg / (height_m ** 2)).round(2)


def categorize_bmi(bmi: float) -> str:
    """
    Categorize BMI into standard WHO analytical bands.
    """
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25.0:
        return "Normal Weight"
    elif bmi < 30.0:
        return "Overweight"
    elif bmi < 35.0:
        return "Obese Class I"
    else:
        return "Obese Class II/III"


def categorize_blood_pressure(row: pd.Series) -> str:
    """
    Categorize blood pressure based on AHA/ACC guidelines for analytics.
    Note: Evaluated strictly as an analytical proxy on observational data.
    """
    hi = row["ap_hi"]
    lo = row["ap_lo"]

    if hi >= 180 or lo >= 120:
        return "Hypertensive Crisis"
    elif hi >= 140 or lo >= 90:
        return "Hypertension Stage 2"
    elif (130 <= hi < 140) or (80 <= lo < 90):
        return "Hypertension Stage 1"
    elif (120 <= hi < 130) and lo < 80:
        return "Elevated"
    else:
        return "Normal"


def categorize_age(age_years: float) -> str:
    """
    Categorize age into analytical decade groups.
    Dataset age range is ~29.7 to 64.9 years.
    """
    if age_years < 40:
        return "30-39"
    elif age_years < 50:
        return "40-49"
    elif age_years < 60:
        return "50-59"
    else:
        return "60+"


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds all analytical features without modifying original raw features.
    """
    df_feat = df.copy()

    # Age conversions & grouping
    df_feat["age_years"] = (df_feat["age"] / 365.25).round(1)
    df_feat["age_group"] = df_feat["age_years"].apply(categorize_age)

    # Demographics
    df_feat["gender_label"] = df_feat["gender"].map({1: "Female", 2: "Male"})

    # Physical metrics & BMI
    df_feat["BMI"] = compute_bmi(df_feat["weight"], df_feat["height"])
    df_feat["BMI_Category"] = df_feat["BMI"].apply(categorize_bmi)

    # Blood Pressure Category
    df_feat["Blood_Pressure_Category"] = df_feat.apply(categorize_blood_pressure, axis=1)

    # Categorical Descriptions for reporting
    df_feat["Cholesterol_Level"] = df_feat["cholesterol"].map({
        1: "Normal",
        2: "Above Normal",
        3: "Well Above Normal"
    })

    df_feat["Glucose_Level"] = df_feat["gluc"].map({
        1: "Normal",
        2: "Above Normal",
        3: "Well Above Normal"
    })

    df_feat["Smoking_Status"] = df_feat["smoke"].map({0: "Non-Smoker", 1: "Smoker"})
    df_feat["Alcohol_Status"] = df_feat["alco"].map({0: "Non-Drinker", 1: "Alcohol Consumer"})
    df_feat["Physical_Activity_Status"] = df_feat["active"].map({0: "Inactive", 1: "Active"})
    df_feat["CVD_Status"] = df_feat["cardio"].map({0: "No CVD", 1: "CVD Present"})

    return df_feat
