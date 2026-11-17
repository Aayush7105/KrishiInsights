# KrishiInsights Dataset Profiling & Quality Analysis Report

Generated as part of **Stage 2: Dataset Research, Acquisition, and Database Design**.

---

## 1. Executive Summary

| Dataset Identifier | Records | Columns | Coverage Window | Geographic Units | File Size | Quality Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Crop Production** | 246,091 | 7 | 1997 – 2015 | 33 States, 646 Districts | 14.61 MB | Validated; 1.52% missing production filtered |
| **IMD Rainfall** | 4,116 | 19 | 1901 – 2015 | 36 Subdivisions | 511.7 KB | Validated; <0.2% missing imputed |

---

## 2. Agricultural Crop Dataset Profile

* **File Location:** `datasets/raw/agriculture/crop_production.csv`
* **Source Lineage:** Directorate of Economics and Statistics (DES), Ministry of Agriculture & Farmers Welfare via data.gov.in & NDAP.
* **Attributes:** `State_Name`, `District_Name`, `Crop_Year`, `Season`, `Crop`, `Area`, `Production`.
* **Distinct Entities:**
  * States/UTs: **33**
  * Districts: **646**
  * Crops: **124**
  * Seasons: `Kharif`, `Rabi`, `Summer`, `Autumn`, `Winter`, `Whole Year`.
* **Data Quality Findings:**
  1. **Missing Production:** 3,730 rows (1.52%) have null production. These must be excluded from yield calculation because yield cannot be derived without production.
  2. **Non-Positive Area:** 0 records with Area < 0; records with Area = 0 must be handled to avoid division-by-zero.
  3. **Unit Distinction (Crucial):**
     * Field crops (Rice, Wheat, Sugarcane, Pulses) report Production in **Metric Tonnes**.
     * Tree crop **Coconut** reports Production in **Number of Nuts** (median production ~239,000 nuts).
     * Yield for field crops is in **Tonnes/Hectare**; yield for coconut is in **Nuts/Hectare**.
  4. **Duplicates:** 0 exact duplicate rows found across `(State, District, Year, Season, Crop)`.

---

## 3. Rainfall Dataset Profile

* **File Location:** `datasets/raw/rainfall/rainfall.csv`
* **Source Lineage:** India Meteorological Department (IMD) / mausam.imd.gov.in via data.gov.in.
* **Attributes:** `SUBDIVISION`, `YEAR`, `JAN`–`DEC`, `ANNUAL`, `Jan-Feb`, `Mar-May`, `Jun-Sep`, `Oct-Dec`.
* **Granularity & Alignment:**
  * Spatial Granularity: **36 Meteorological Subdivisions**.
  * Mapping Strategy: Mapped deterministically to the 33 Indian States/UTs. Multi-subdivision states (e.g., Maharashtra with 4 subdivisions, UP with 2 subdivisions) use subdivision means.
  * Temporal Granularity: Monthly and seasonal aggregates in millimetres (mm).
    * `Jun-Sep`: Aligned with Monsoon / Kharif.
    * `Oct-Dec` + `Jan-Feb`: Aligned with Post-Monsoon / Winter / Rabi.
    * `Mar-May`: Aligned with Pre-Monsoon / Summer.
    * `ANNUAL`: Aligned with Whole Year.

---

## 4. Architectural Readiness for PostgreSQL

The dataset profiling establishes clear relational requirements:
1. Normalized reference tables: `states`, `districts`, `crops`, and `seasons`.
2. Granular observation tables: `agricultural_records` with composite uniqueness on `(state_id, district_id, crop_id, season_id, year)`.
3. Climate observation tables: `rainfall_records` linked at state level on `(state_id, year)`.
4. Inference history: `prediction_records` for recording future model predictions.
