# Power BI Data Model Architecture Specification

## 1. Data Model Overview
The Power BI data model is designed following a **Star Schema** architecture to ensure optimal analytical query performance, scalability, and seamless drill-through aggregation.

### Fact & Dimension Tables

```
                      +-----------------------------+
                      |   Dim_Date (Calendar)       |
                      +-----------------------------+
                                     | 1
                                     |
                                     | *
+-----------------------+     +-----------------------------+     +-----------------------+
|  Dim_BP_Category      | 1 * |   Fact_Patient_Cardio       | * 1 | Dim_BMI_Category      |
+-----------------------+-----+-----------------------------+-----+-----------------------+
                              | *                         * |
                               \                         /
                                \ 1                     / 1
                          +---------------+     +------------------+
                          |  Dim_Gender   |     | Dim_Risk_Factors |
                          +---------------+     +------------------+
```

---

## 2. Table Specifications & Relationships

### Primary Fact Table: `Fact_Patient_Cardio`
- **Source**: `data/processed/cardio_cleaned.csv`
- **Granularity**: 1 record per patient (`id`)
- **Key Columns**:
  - `id` (Integer, Primary Key)
  - `age_years` (Decimal Number)
  - `gender` (Integer, FK to `Dim_Gender`)
  - `height` (Integer)
  - `weight` (Decimal)
  - `ap_hi` (Integer)
  - `ap_lo` (Integer)
  - `cholesterol` (Integer)
  - `gluc` (Integer)
  - `smoke` (Integer)
  - `alco` (Integer)
  - `active` (Integer)
  - `cardio` (Integer: 0 = No CVD, 1 = CVD Present)
  - `BMI` (Decimal)
  - `BMI_Category` (Text, FK to `Dim_BMI_Category`)
  - `Blood_Pressure_Category` (Text, FK to `Dim_BP_Category`)

---

## 3. Relationships & Cardinality

| Left Table | Right Table | Join Key | Cardinality | Cross Filter Direction |
| :--- | :--- | :--- | :--- | :--- |
| `Dim_Gender` | `Fact_Patient_Cardio` | `gender` | 1 to Many (`1:*`) | Single (`Dim_Gender` filters Fact) |
| `Dim_BMI_Category` | `Fact_Patient_Cardio` | `BMI_Category` | 1 to Many (`1:*`) | Single (`Dim_BMI_Category` filters Fact) |
| `Dim_BP_Category` | `Fact_Patient_Cardio` | `Blood_Pressure_Category` | 1 to Many (`1:*`) | Single (`Dim_BP_Category` filters Fact) |

> [!NOTE]
> All relationships are enforced with referential integrity enabled and 1-to-many single direction filtering to avoid ambiguous filter context pathways.
