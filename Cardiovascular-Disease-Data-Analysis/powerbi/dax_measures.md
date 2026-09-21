# Power BI DAX Measures Reference Library

All DAX measures are organized within a dedicated `_Measures` table for clean maintenance and governance.

---

## 1. Executive Key Performance Indicators (KPIs)

### Total Patient Records
```dax
Total_Patients = 
COUNTROWS(Fact_Patient_Cardio)
```

### CVD Cases Count
```dax
CVD_Cases = 
CALCULATE(
    COUNTROWS(Fact_Patient_Cardio),
    Fact_Patient_Cardio[cardio] = 1
)
```

### Non-CVD Cases Count
```dax
Non_CVD_Cases = 
CALCULATE(
    COUNTROWS(Fact_Patient_Cardio),
    Fact_Patient_Cardio[cardio] = 0
)
```

### Cardiovascular Disease Prevalence Rate (%)
```dax
CVD_Prevalence_Pct = 
DIVIDE([CVD_Cases], [Total_Patients], 0) * 100
```

---

## 2. Demographic & Physical Health Averages

### Average Age (Years)
```dax
Average_Age = 
AVERAGE(Fact_Patient_Cardio[age_years])
```

### Average BMI (kg/m²)
```dax
Average_BMI = 
AVERAGE(Fact_Patient_Cardio[BMI])
```

### Average Systolic Blood Pressure (mmHg)
```dax
Average_Systolic_BP = 
AVERAGE(Fact_Patient_Cardio[ap_hi])
```

### Average Diastolic Blood Pressure (mmHg)
```dax
Average_Diastolic_BP = 
AVERAGE(Fact_Patient_Cardio[ap_lo])
```

---

## 3. Advanced Analytical Risk Measures

### High Blood Pressure Prevalence (%)
```dax
High_BP_Prevalence_Pct = 
DIVIDE(
    CALCULATE(
        COUNTROWS(Fact_Patient_Cardio),
        Fact_Patient_Cardio[Blood_Pressure_Category] IN {"Hypertension Stage 2", "Hypertensive Crisis"}
    ),
    [Total_Patients],
    0
) * 100
```

### High Cholesterol Prevalence (%)
```dax
High_Cholesterol_Prevalence_Pct = 
DIVIDE(
    CALCULATE(
        COUNTROWS(Fact_Patient_Cardio),
        Fact_Patient_Cardio[cholesterol] IN {2, 3}
    ),
    [Total_Patients],
    0
) * 100
```

### Variance from Baseline CVD Rate (%)
```dax
CVD_Prevalence_Variance_From_Baseline = 
VAR OverallRate = CALCULATE([CVD_Prevalence_Pct], ALL(Fact_Patient_Cardio))
RETURN
[CVD_Prevalence_Pct] - OverallRate
```
