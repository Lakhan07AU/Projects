"""
Visualization Module for Cardiovascular Disease Data Analysis
Generates publication-quality charts saved to visualizations/
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set consistent matplotlib style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 16,
    'figure.autolayout': True,
    'figure.dpi': 300
})

PRIMARY_BLUE = "#2b5c8f"
ALERT_RED = "#d9534f"
COLOR_PALETTE = ["#2b5c8f", "#d9534f", "#41b6c4", "#225ea8", "#a6bddb"]


def create_all_visualizations(df_feat: pd.DataFrame, model_results_df: pd.DataFrame = None, feature_imp_df: pd.DataFrame = None, output_dir: str = "visualizations") -> None:
    """
    Generates all 14 required publication-quality PNG charts.
    """
    os.makedirs(output_dir, exist_ok=True)

    # 01. Age Distribution
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(data=df_feat, x="age_years", hue="CVD_Status", kde=True, bins=35, palette={"No CVD": "#2b5c8f", "CVD Present": "#d9534f"}, alpha=0.6, ax=ax)
    ax.set_title("Age Distribution by Cardiovascular Disease Status")
    ax.set_xlabel("Age (Years)")
    ax.set_ylabel("Patient Count")
    plt.savefig(os.path.join(output_dir, "01_age_distribution.png"), dpi=300)
    plt.close()

    # 02. Gender Distribution
    fig, ax = plt.subplots(figsize=(7, 5))
    gender_counts = df_feat["gender_label"].value_counts()
    bars = ax.bar(gender_counts.index, gender_counts.values, color=["#2b5c8f", "#41b6c4"], width=0.5)
    for bar in bars:
        yval = bar.get_height()
        pct = (yval / len(df_feat)) * 100
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 500, f"{yval:,}\n({pct:.1f}%)", ha='center', va='bottom', fontsize=10)
    ax.set_title("Demographic Gender Distribution")
    ax.set_ylabel("Patient Count")
    ax.set_ylim(0, max(gender_counts.values) * 1.15)
    plt.savefig(os.path.join(output_dir, "02_gender_distribution.png"), dpi=300)
    plt.close()

    # 03. CVD Prevalence Baseline
    fig, ax = plt.subplots(figsize=(7, 5))
    cvd_counts = df_feat["CVD_Status"].value_counts()
    bars = ax.bar(cvd_counts.index, cvd_counts.values, color=["#2b5c8f", "#d9534f"], width=0.5)
    for bar in bars:
        yval = bar.get_height()
        pct = (yval / len(df_feat)) * 100
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 500, f"{yval:,}\n({pct:.2f}%)", ha='center', va='bottom', fontsize=10)
    ax.set_title("Cardiovascular Disease Baseline Prevalence")
    ax.set_ylabel("Patient Count")
    ax.set_ylim(0, max(cvd_counts.values) * 1.15)
    plt.savefig(os.path.join(output_dir, "03_cvd_prevalence.png"), dpi=300)
    plt.close()

    # 04. BMI Distribution
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(data=df_feat, x="BMI", hue="CVD_Status", kde=True, bins=40, palette={"No CVD": "#2b5c8f", "CVD Present": "#d9534f"}, alpha=0.6, ax=ax)
    ax.axvline(25.0, color='gray', linestyle='--', label='Overweight Threshold (25.0)')
    ax.axvline(30.0, color='black', linestyle=':', label='Obesity Threshold (30.0)')
    ax.set_title("Body Mass Index (BMI) Distribution & CVD Breakdown")
    ax.set_xlabel("BMI (kg/m²)")
    ax.set_ylabel("Patient Count")
    ax.set_xlim(12, 50)
    ax.legend()
    plt.savefig(os.path.join(output_dir, "04_bmi_distribution.png"), dpi=300)
    plt.close()

    # 05. BMI Category vs CVD
    fig, ax = plt.subplots(figsize=(9, 5))
    bmi_order = ["Underweight", "Normal Weight", "Overweight", "Obese Class I", "Obese Class II/III"]
    bmi_prev = df_feat.groupby("BMI_Category")["cardio"].mean().reindex(bmi_order) * 100
    bars = ax.bar(bmi_prev.index, bmi_prev.values, color="#2b5c8f", width=0.5)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f"{yval:.1f}%", ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_title("CVD Prevalence Rate by BMI Category")
    ax.set_ylabel("CVD Prevalence (%)")
    ax.set_ylim(0, 80)
    plt.savefig(os.path.join(output_dir, "05_bmi_vs_cvd.png"), dpi=300)
    plt.close()

    # 06. BP Distribution
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.scatterplot(data=df_feat.sample(5000, random_state=42), x="ap_lo", y="ap_hi", hue="CVD_Status", palette={"No CVD": "#2b5c8f", "CVD Present": "#d9534f"}, alpha=0.5, s=25, ax=ax)
    ax.set_title("Blood Pressure Scatter Plot (Systolic vs Diastolic BP)")
    ax.set_xlabel("Diastolic Blood Pressure (ap_lo mmHg)")
    ax.set_ylabel("Systolic Blood Pressure (ap_hi mmHg)")
    ax.set_xlim(40, 140)
    ax.set_ylim(70, 210)
    plt.savefig(os.path.join(output_dir, "06_bp_distribution.png"), dpi=300)
    plt.close()

    # 07. BP Category vs CVD
    fig, ax = plt.subplots(figsize=(10, 5))
    bp_order = ["Normal", "Elevated", "Hypertension Stage 1", "Hypertension Stage 2", "Hypertensive Crisis"]
    bp_prev = df_feat.groupby("Blood_Pressure_Category")["cardio"].mean().reindex(bp_order) * 100
    bars = ax.bar(bp_prev.index, bp_prev.values, color="#d9534f", width=0.55)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f"{yval:.1f}%", ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_title("CVD Prevalence Rate by AHA Blood Pressure Category")
    ax.set_ylabel("CVD Prevalence (%)")
    ax.set_ylim(0, 100)
    plt.xticks(rotation=15)
    plt.savefig(os.path.join(output_dir, "07_bp_vs_cvd.png"), dpi=300)
    plt.close()

    # 08. Cholesterol vs CVD
    fig, ax = plt.subplots(figsize=(8, 5))
    chol_order = ["Normal", "Above Normal", "Well Above Normal"]
    chol_prev = df_feat.groupby("Cholesterol_Level")["cardio"].mean().reindex(chol_order) * 100
    bars = ax.bar(chol_prev.index, chol_prev.values, color="#2b5c8f", width=0.5)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f"{yval:.1f}%", ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_title("CVD Prevalence Rate by Cholesterol Level")
    ax.set_ylabel("CVD Prevalence (%)")
    ax.set_ylim(0, 90)
    plt.savefig(os.path.join(output_dir, "08_cholesterol_vs_cvd.png"), dpi=300)
    plt.close()

    # 09. Glucose vs CVD
    fig, ax = plt.subplots(figsize=(8, 5))
    gluc_order = ["Normal", "Above Normal", "Well Above Normal"]
    gluc_prev = df_feat.groupby("Glucose_Level")["cardio"].mean().reindex(gluc_order) * 100
    bars = ax.bar(gluc_prev.index, gluc_prev.values, color="#41b6c4", width=0.5)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f"{yval:.1f}%", ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_title("CVD Prevalence Rate by Glucose Level")
    ax.set_ylabel("CVD Prevalence (%)")
    ax.set_ylim(0, 80)
    plt.savefig(os.path.join(output_dir, "09_glucose_vs_cvd.png"), dpi=300)
    plt.close()

    # 10. Smoking vs CVD
    fig, ax = plt.subplots(figsize=(7, 5))
    smoke_prev = df_feat.groupby("Smoking_Status")["cardio"].mean() * 100
    bars = ax.bar(smoke_prev.index, smoke_prev.values, color=["#2b5c8f", "#d9534f"], width=0.45)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f"{yval:.1f}%", ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_title("CVD Prevalence Rate by Smoking Status")
    ax.set_ylabel("CVD Prevalence (%)")
    ax.set_ylim(0, 70)
    plt.savefig(os.path.join(output_dir, "10_smoking_vs_cvd.png"), dpi=300)
    plt.close()

    # 11. Activity vs CVD
    fig, ax = plt.subplots(figsize=(7, 5))
    act_prev = df_feat.groupby("Physical_Activity_Status")["cardio"].mean().reindex(["Inactive", "Active"]) * 100
    bars = ax.bar(act_prev.index, act_prev.values, color=["#d9534f", "#2b5c8f"], width=0.45)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f"{yval:.1f}%", ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_title("CVD Prevalence Rate by Physical Activity Status")
    ax.set_ylabel("CVD Prevalence (%)")
    ax.set_ylim(0, 70)
    plt.savefig(os.path.join(output_dir, "11_activity_vs_cvd.png"), dpi=300)
    plt.close()

    # 12. Correlation Heatmap
    num_cols = ["age_years", "height", "weight", "BMI", "ap_hi", "ap_lo", "cholesterol", "gluc", "smoke", "alco", "active", "cardio"]
    corr_matrix = df_feat[num_cols].corr(method='spearman')
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="Blues", cbar=True, ax=ax, linewidths=0.5)
    ax.set_title("Spearman Rank Correlation Heatmap")
    plt.savefig(os.path.join(output_dir, "12_correlation_heatmap.png"), dpi=300)
    plt.close()

    # 13. Feature Importance Chart (if provided)
    if feature_imp_df is not None:
        fig, ax = plt.subplots(figsize=(9, 6))
        sns.barplot(data=feature_imp_df, x="importance", y="feature", color="#2b5c8f", ax=ax)
        ax.set_title("Random Forest Model Feature Importance")
        ax.set_xlabel("Relative Gini Importance Score")
        ax.set_ylabel("Feature")
        plt.savefig(os.path.join(output_dir, "13_feature_importance.png"), dpi=300)
        plt.close()

    # 14. Model Comparison Chart (if provided)
    if model_results_df is not None:
        fig, ax = plt.subplots(figsize=(10, 6))
        melted_df = model_results_df.melt(id_vars=["Model"], value_vars=["Accuracy", "Precision", "Recall", "F1_Score", "ROC_AUC"], var_name="Metric", value_name="Score")
        sns.barplot(data=melted_df, x="Model", y="Score", hue="Metric", palette="Blues_r", ax=ax)
        ax.set_title("Machine Learning Models Evaluation Metrics Comparison")
        ax.set_ylabel("Metric Score (0.0 to 1.0)")
        ax.set_ylim(0.5, 0.85)
        plt.xticks(rotation=15)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.savefig(os.path.join(output_dir, "14_model_comparison.png"), dpi=300)
        plt.close()

    print(f"All 14 visualizations successfully generated and saved to {output_dir}/")
