# KrishiInsights Datasets Registry & Codebook

This directory stores the official, cleaned, and integrated datasets powering **KrishiInsights** (Agricultural Data Analytics and Crop Yield Intelligence Platform).

---

## 1. Directory Structure

```
datasets/
├── raw/
│   ├── crop_production.csv          # Official crop production records (1997–2015)
│   └── rainfall.csv                 # IMD subdivision-wise rainfall records (1901–2015)
├── processed/
│   ├── clean_crop_data.csv          # Cleaned, standardized crop production records with calculated yield
│   └── combined_data.csv            # Integrated crop and season-matched rainfall dataset
└── README.md                        # Documentation of sources, schemas, transformations, and caveats
```

---

## 2. Source Provenance & Lineage

| Dataset | Source Authority | Official Portal | Coverage Period | Granularity | License / Access |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Crop Production** | Ministry of Agriculture & Farmers Welfare, Directorate of Economics and Statistics (DES) | [Open Government Data Platform (data.gov.in)](https://www.data.gov.in/) & [NDAP (NITI Aayog)](https://ndap.niti.gov.in/) | 1997 – 2015 | District / State / Season / Crop | National Data Sharing and Accessibility Policy (NDSAP) |
| **Meteorological Rainfall** | India Meteorological Department (IMD), Ministry of Earth Sciences | [IMD Mausam](https://mausam.imd.gov.in/) & Open Government Data Platform | 1901 – 2015 | Meteorological Subdivision / Annual / Monthly | Open Access / Public Domain meteorological records |

---

## 3. Raw Data Specifications

### 3.1 Raw Crop Production (`datasets/raw/crop_production.csv`)
* **Total Rows**: 246,091
* **Attributes**:
  * `State_Name` (string): State or Union Territory name
  * `District_Name` (string): Administrative district
  * `Crop_Year` (int): Agricultural harvest year (1997 to 2015)
  * `Season` (string): Sowing/harvest season (`Kharif`, `Rabi`, `Summer`, `Autumn`, `Winter`, `Whole Year`)
  * `Crop` (string): Name of crop (124 distinct crops, e.g., Rice, Wheat, Sugarcane, Cotton)
  * `Area` (float): Cultivated land area in **Hectares**
  * `Production` (float): Total crop output (**Tonnes** for field crops, **Number of Nuts** for Coconut)

### 3.2 Raw Rainfall (`datasets/raw/rainfall.csv`)
* **Total Rows**: 4,116
* **Attributes**:
  * `SUBDIVISION` (string): 36 IMD meteorological subdivisions
  * `YEAR` (int): Calendar year (1901 to 2015)
  * `JAN` - `DEC` (float): Monthly rainfall in **millimetres (mm)**
  * `ANNUAL` (float): Annual total rainfall in **mm**
  * `Jan-Feb`, `Mar-May`, `Jun-Sep`, `Oct-Dec` (float): Seasonal rainfall totals in **mm**

---

## 4. Cleaning & Integration Methodology

All preprocessing is automated and reproducible via `scripts/preprocess_data.py`.

### 4.1 Missing Values and Data Cleaning
1. **Handling Missing Production**: 3,730 records (1.52%) in the raw crop dataset lacked production values. Since yield cannot be calculated without production, records with missing or negative production were removed.
2. **Filtering Non-Positive Cultivated Area**: Records with `Area <= 0` or missing area were excluded to prevent division-by-zero errors in yield calculation.
3. **String Sanitization**: Whitespace trimmed and state aliases reconciled (e.g., historical `Orissa` -> `Odisha`).
4. **Duplicate Removal**: Checked on `(State, District, Year, Season, Crop)`.
5. **Handling Unit Discrepancies**:
   * Coconut is explicitly documented as `Production_Unit = 'Number of Nuts'` and `Yield_Unit = 'Nuts/Hectare'`.
   * All other crops are documented as `Production_Unit = 'Tonnes'` and `Yield_Unit = 'Tonnes/Hectare'`.
6. **Outlier Filtering**: Measurement/data-entry errors with calculated non-coconut yields exceeding 200 Tonnes/Ha were filtered (65 rows).

### 4.2 Yield Calculation Formula
In accordance with agronomical standards:
$$\text{Yield} = \frac{\text{Production}}{\text{Cultivated Area}}$$
* Expressed in **Tonnes per Hectare** (for field crops) and **Nuts per Hectare** (for Coconut).

### 4.3 Geospatial & Temporal Mapping to IMD Rainfall
* IMD's 36 meteorological subdivisions were systematically mapped to the 33 corresponding Indian States and Union Territories.
* Multi-subdivision states (such as Maharashtra spanning Konkan & Goa, Madhya Maharashtra, Marathwada, and Vidarbha, or Uttar Pradesh spanning East and West UP) are aggregated by area-weighted subdivision averages.
* **Temporal & Seasonal Alignment**:
  * `Kharif` & `Autumn` crops are matched with South-West Monsoon rainfall (`Jun-Sep`).
  * `Rabi` & `Winter` crops are matched with post-monsoon and winter rainfall (`Oct-Dec` + `Jan-Feb`).
  * `Summer` crops are matched with pre-monsoon rainfall (`Mar-May`).
  * `Whole Year` crops are matched with `Annual_Rainfall_mm`.
* **Merge Result**: 242,296 records with **100% matched rainfall coverage (0 missing records)** across all Indian states from 1997 to 2015.

---

## 5. Processed Dataset Codebook

### 5.1 `clean_crop_data.csv`
| Column Name | Data Type | Units / Range | Description |
| :--- | :--- | :--- | :--- |
| `State` | string | 33 States/UTs | Indian State or Union Territory |
| `District` | string | 646 Districts | Administrative district |
| `Year` | integer | 1997 – 2015 | Agricultural crop year |
| `Season` | string | Kharif, Rabi, Summer, Autumn, Winter, Whole Year | Agricultural season |
| `Crop` | string | 124 crop types | Crop name |
| `Area` | float | Hectares ($> 0$) | Total cultivated area |
| `Production` | float | Tonnes / Nuts | Total recorded crop production |
| `Area_Unit` | string | "Hectares" | Unit of area measurement |
| `Production_Unit`| string | "Tonnes" or "Number of Nuts" | Unit of production measurement |
| `Yield_Unit` | string | "Tonnes/Hectare" or "Nuts/Hectare" | Unit of yield |
| `Yield` | float | Tonnes/Ha (or Nuts/Ha) | Computed yield ($\text{Production} / \text{Area}$) |

### 5.2 `combined_data.csv`
Includes all columns from `clean_crop_data.csv` plus the following meteorological indicators:

| Column Name | Data Type | Units | Description |
| :--- | :--- | :--- | :--- |
| `Annual_Rainfall_mm` | float | mm | State-level total annual precipitation for the crop year |
| `Monsoon_Rainfall_mm` | float | mm | South-West Monsoon precipitation (June – September) |
| `Post_Monsoon_Rainfall_mm` | float | mm | Post-Monsoon precipitation (October – December) |
| `Winter_Rainfall_mm` | float | mm | Winter precipitation (January – February) |
| `Pre_Monsoon_Rainfall_mm` | float | mm | Pre-Monsoon summer precipitation (March – May) |
| `Rabi_Rainfall_mm` | float | mm | Combined Rabi season precipitation (Oct–Dec + Jan–Feb) |
| `Season_Rainfall_mm` | float | mm | Precipitation specifically aligned with the crop's growing season |

---

## 6. Known Limitations & Technical Caveats

1. **Geographic Granularity**: Rainfall is measured at meteorological subdivision level and aggregated to state level, whereas crop records are reported at district level. State rainfall represents regional precipitation trends, not hyper-local rain gauge readings.
2. **Irrigation Factor**: Yield is influenced by irrigation facilities (canal, borewell), fertilizer use, soil quality, and seed varieties in addition to precipitation. Rainfall correlation must not be confused with sole direct causation.
3. **Data Leakage Safeguard**: In machine learning regression tasks, `Production` must never be used alongside `Area` to predict `Yield`, because Yield is derived directly from Production.

