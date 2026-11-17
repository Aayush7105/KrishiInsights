# KrishiInsights Datasets Registry & Codebook

This directory stores the official, cleaned, and integrated datasets powering **KrishiInsights** (Agricultural Data Analytics and Crop Yield Intelligence Platform).

---

## 1. Canonical Directory Structure

```text
datasets/
├── raw/
│   ├── crop_production.csv      # Official district crop production records (1997–2015)
│   └── rainfall.csv             # IMD subdivision-wise rainfall records (1901–2015)
├── processed/
│   ├── clean_crop_data.csv      # Cleaned crop production records with calculated yield (242,296 records)
│   └── combined_data.csv        # Integrated crop and season-matched rainfall dataset (242,296 records)
├── metadata/
│   ├── crop_production_profile.json # Structural & quality profile for crop data
│   ├── rainfall_profile.json        # Structural & quality profile for rainfall data
│   ├── dataset_sources.json         # Source provenance, URLs, licensing, and lineage
│   └── DATASET_PROFILING_REPORT.md  # Comprehensive Markdown data profiling report
└── README.md
```

> [!IMPORTANT]
> **Single Canonical Storage:** The root `datasets/` directory is the single authoritative storage location. The `ml/` module reads from this directory via relative paths. No duplicate physical dataset copies are maintained inside `ml/data/`.

---

## 2. Source Provenance & Lineage

| Dataset | Source Authority | Official Portal | Coverage Window | Spatial Granularity | License / Access |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Crop Production** | Ministry of Agriculture & Farmers Welfare, Directorate of Economics and Statistics (DES) | [data.gov.in](https://www.data.gov.in/) & [NDAP (NITI Aayog)](https://ndap.niti.gov.in/) | 1997 – 2015 | District / State / Season / Crop | Government Open Data License - India (GODL-India) / NDSAP |
| **Meteorological Rainfall** | India Meteorological Department (IMD), Ministry of Earth Sciences | [mausam.imd.gov.in](https://mausam.imd.gov.in/) & Open Government Data Platform | 1901 – 2015 | 36 Meteorological Subdivisions | Open Access / Public Meteorological Records |

---

## 3. Dataset Specifications & Attributes

### 3.1 Raw Crop Production (`datasets/raw/crop_production.csv`)
* **Total Rows**: 246,091 | **File Size**: 15.3 MB | **Format**: CSV
* **Attributes**:
  * `State_Name` (string): State or Union Territory name (33 states/UTs)
  * `District_Name` (string): Administrative district (646 districts)
  * `Crop_Year` (int): Harvest year (1997 to 2015)
  * `Season` (string): Cropping season (`Kharif`, `Rabi`, `Summer`, `Autumn`, `Winter`, `Whole Year`)
  * `Crop` (string): Standardized crop name (124 distinct crops, e.g. Rice, Wheat, Sugarcane, Cotton)
  * `Area` (float): Cultivated land area in **Hectares**
  * `Production` (float): Output volume (**Metric Tonnes** for field crops, **Number of Nuts** for Coconut)

### 3.2 Raw Rainfall (`datasets/raw/rainfall.csv`)
* **Total Rows**: 4,116 | **File Size**: 524 KB | **Format**: CSV
* **Attributes**:
  * `SUBDIVISION` (string): 36 IMD meteorological subdivisions
  * `YEAR` (int): Calendar year (1901 to 2015)
  * `JAN` - `DEC` (float): Monthly rainfall in **millimetres (mm)**
  * `ANNUAL` (float): Annual total rainfall in **mm**
  * `Jan-Feb`, `Mar-May`, `Jun-Sep`, `Oct-Dec` (float): Seasonal rainfall totals in **mm**

---

## 4. Key Data Quality Findings & Validation Rules

1. **Missing Production:** 3,730 records (1.52%) in the raw crop dataset lack production values. Because yield is derived as $\text{Yield} = \text{Production} / \text{Area}$, records with null or negative production cannot produce valid yields and are excluded during processing.
2. **Cultivated Area Validation:** Records with non-positive or missing area are excluded to prevent division-by-zero errors.
3. **Unit Transparency (Coconut vs. Field Crops):**
   * Field crops (Wheat, Rice, Maize, Sugarcane, Pulses) report Production in **Metric Tonnes**, yielding **Tonnes/Hectare**.
   * Coconut is reported in **Number of Nuts** (median production ~239,000 nuts), yielding **Nuts/Hectare**.
   * The units are explicitly tagged in `Production_Unit` and `Yield_Unit` to prevent metric mixing.
4. **Spatial Granularity Alignment:**
   * Rainfall is measured at meteorological subdivision level, whereas crop records are reported at district level.
   * IMD's 36 subdivisions are aggregated deterministically to the 33 corresponding States/UTs. State-level rainfall is assigned to districts without falsely claiming it as local rain gauge data.
5. **Temporal & Seasonal Alignment:**
   * `Kharif` & `Autumn` crops are matched with South-West Monsoon rainfall (`Jun-Sep`).
   * `Rabi` & `Winter` crops are matched with post-monsoon and winter rainfall (`Oct-Dec` + `Jan-Feb`).
   * `Summer` crops are matched with pre-monsoon rainfall (`Mar-May`).
   * `Whole Year` crops are matched with `ANNUAL` rainfall.

---

## 5. Machine Learning & Ingestion Path

All preprocessing and database ingestion modules reference this canonical directory:
* Data Preprocessing: `scripts/preprocess_data.py`
* Ingestion Service: `backend/app/services/ingestion_service.py`
* Metadata Profiles: `datasets/metadata/`
