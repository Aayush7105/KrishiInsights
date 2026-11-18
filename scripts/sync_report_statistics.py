"""
Syncs Markdown reports with exact Neon database numbers verified during Stage 4 independent audit.
"""

import re

def find_block(pattern: str, text: str) -> str:
    m = re.search(pattern, text, re.DOTALL)
    assert m is not None, f"Pattern not found: {pattern}"
    return m.group(0)

def update_agricultural_analysis():
    filepath = "docs/AGRICULTURAL_ANALYSIS.md"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update Annual Historical Trajectory Table
    old_traj = find_block(r"### Annual Historical Trajectory Table.*?(?=---)", content)
    new_traj = """### Annual Historical Trajectory Table

| Year | Total Production (MT) | Total Area (MHa) | Aggregate Yield (T/Ha) | Production YoY (%) | Yield YoY (%) | Production Index (1997=100) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1997** | 537.51 | 230.37 | 2.3333 | — | — | 100.00 |
| **1998** | 529.01 | 165.34 | 3.1994 | -1.58% | +37.12% | 98.42 |
| **1999** | 574.85 | 157.33 | 3.6537 | +8.67% | +14.20% | 106.95 |
| **2000** | 569.30 | 163.85 | 3.4745 | -0.97% | -4.90% | 105.91 |
| **2001** | 584.25 | 163.84 | 3.5660 | +2.63% | +2.63% | 108.70 |
| **2002** | 546.02 | 155.53 | 3.5108 | -6.54% | -1.55% | 101.58 |
| **2003** | 562.23 | 167.96 | 3.3474 | +2.97% | -4.65% | 104.60 |
| **2004** | 525.48 | 165.92 | 3.1671 | -6.54% | -5.39% | 97.76 |
| **2005** | 590.57 | 161.08 | 3.6664 | +12.39% | +15.77% | 109.87 |
| **2006** | 589.35 | 168.74 | 3.4926 | -0.21% | -4.74% | 109.64 |
| **2007** | 579.53 | 151.01 | 3.8378 | -1.67% | +9.88% | 107.82 |
| **2008** | 675.45 | 169.24 | 3.9911 | +16.55% | +3.99% | 125.66 |
| **2009** | 618.50 | 163.87 | 3.7743 | -8.43% | -5.43% | 115.07 |
| **2010** | 711.41 | 175.35 | 4.0572 | +15.02% | +7.50% | 132.35 |
| **2011** | 709.03 | 151.80 | 4.6709 | -0.33% | +15.13% | 131.91 |
| **2012** | 676.60 | 150.34 | 4.5005 | -4.57% | -3.65% | 125.88 |
| **2013** | 683.69 | 139.68 | 4.8946 | +1.05% | +8.76% | 127.20 |
| **2014** | 596.73 | 114.38 | 5.2170 | -12.72% | +6.59% | 111.02 |
| **2015** | 6.94 | 4.60 | 1.5075 | -98.84% | -71.10% | 1.29 |

*(Note: 2015 reflects a partial reporting sample of 8 states / 636 records; growth metrics are evaluated on the 1997–2014 complete series).*

### Macro Trajectory Findings
1. **Steady Productivity Expansion:** While total cultivated area stabilized after 1998 in the range of $140\\text{ MHa}$ to $175\\text{ MHa}$, national production expanded from $537.51\\text{ MT}$ in 1997 to a peak of $683.69\\text{ MT}$ in 2013 ($+27.2\\%$).
2. **Efficiency as the Primary Growth Engine:** National weighted yield rose from $2.33\\text{ T/Ha}$ in 1997 to $4.89\\text{ T/Ha}$ in 2013 and $5.22\\text{ T/Ha}$ in 2014 ($+123.6\\%$), proving that agricultural expansion in India has been driven by yield intensification rather than physical land expansion.
3. **Severe Climate Shock Years:**
   - **2002 Drought:** Production dropped by $-6.54\\%$ YoY to $546.02\\text{ MT}$ as aggregate yield declined.
   - **2004 Deficit:** Production dropped by $-6.54\\%$ YoY to $525.48\\text{ MT}$.
   - **2009 Deficit:** Production dropped by $-8.43\\%$ YoY to $618.50\\text{ MT}$ due to delayed and deficient monsoon rains.
   - **2014 Deficit:** Production declined by $-12.72\\%$ YoY to $596.73\\text{ MT}$ following widespread rainfall deficit across central and northern India.

"""
    content = content.replace(old_traj, new_traj)

    # 2. Update Seasonal Distribution
    old_season = find_block(r"## 2\. Seasonal Distribution of Indian Agriculture.*?(?=---)", content)
    new_season = """## 2. Seasonal Distribution of Indian Agriculture

Indian agriculture is structured across distinct crop seasons: Kharif (Monsoon), Rabi (Winter), Summer (Zaid), Autumn, Winter (Boro/rice), and administrative Whole Year submissions.

| Season | Observations | Total Production (MT) | Cultivated Area (MHa) | Aggregate Yield (T/Ha) | Production Share (%) | Area Share (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Whole Year** | 54,125 | 4,115.58 | 225.97 | 18.2128 | **37.87%** | **7.74%** |
| **Kharif** | 94,269 | 4,029.60 | 1,403.36 | 2.8714 | **37.08%** | **48.06%** |
| **Rabi** | 66,160 | 2,051.69 | 947.91 | 2.1644 | **18.88%** | **32.46%** |
| **Winter** | 6,050 | 434.55 | 219.60 | 1.9788 | **4.00%** | **7.52%** |
| **Summer** | 14,810 | 170.63 | 75.31 | 2.2656 | **1.57%** | **2.58%** |
| **Autumn** | 4,924 | 64.39 | 48.07 | 1.3396 | **0.59%** | **1.65%** |

### Key Seasonal Insights
- **Kharif is the Area Giant:** Kharif accounts for nearly half ($48.06\\%$) of all gross cultivated area in India ($1,403.36\\text{ MHa}$), reflecting heavy national reliance on the Southwest Monsoon.
- **Rabi Stability:** Rabi encompasses $947.91\\text{ MHa}$ ($32.46\\%$) with consistent yields ($2.16\\text{ T/Ha}$) supported by canal and tubewell irrigation.
- **Whole Year High Biomass:** The "Whole Year" category accounts for $37.87\\%$ of total production despite only $7.74\\%$ of area, with aggregate yield reaching $18.21\\text{ T/Ha}$ because perennial high-tonnage crops (Sugarcane) are reported under this administrative category.

"""
    content = content.replace(old_season, new_season)

    # 3. Update Crop Rankings
    old_rankings = find_block(r"## 3\. National Crop Rankings across 124 Crops.*?(?=## 4\.)", content)
    new_rankings = """## 3. National Crop Rankings across 124 Crops

### 3.1 Top 10 Field Crops by Total Cumulative Production (1997–2015)

| Rank | Crop Name | Crop Category | Cumulative Production (MT) | Cultivated Area (MHa) | Aggregate Yield (T/Ha) |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **1** | **Sugarcane** | Cash Crop | **5,208.05** | 76.31 | 68.2453 |
| **2** | **Rice** | Cereal | **1,605.22** | 746.32 | 2.1509 |
| **3** | **Wheat** | Cereal | **1,332.83** | 470.71 | 2.8315 |
| **4** | **Potato** | Horticulture | **424.78** | 22.23 | 19.1064 |
| **5** | **Cotton(lint)** | Fiber | **296.98** | 156.56 | 1.8969 |
| **6** | **Maize** | Coarse Cereal | **273.32** | 121.48 | 2.2499 |
| **7** | **Jute** | Fiber | **181.56** | 14.73 | 12.3286 |
| **8** | **Banana** | Horticulture | **146.13** | 5.24 | 27.8626 |
| **9** | **Soyabean** | Oilseed | **141.84** | 135.45 | 1.0472 |
| **10** | **Bajra** | Coarse Cereal | **129.68** | 140.97 | 0.9199 |

### 3.2 Top 10 Field Crops by Cultivated Area (1997–2015)

| Rank | Crop Name | Crop Category | Cultivated Area (MHa) | Cumulative Production (MT) | Aggregate Yield (T/Ha) |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **1** | **Rice** | Cereal | **746.32** | 1,605.22 | 2.1509 |
| **2** | **Wheat** | Cereal | **470.71** | 1,332.83 | 2.8315 |
| **3** | **Cotton(lint)** | Fiber | **156.56** | 296.98 | 1.8969 |
| **4** | **Bajra** | Coarse Cereal | **140.97** | 129.68 | 0.9199 |
| **5** | **Jowar** | Coarse Cereal | **137.66** | 114.60 | 0.8325 |
| **6** | **Soyabean** | Oilseed | **135.45** | 141.84 | 1.0472 |
| **7** | **Maize** | Coarse Cereal | **121.48** | 273.32 | 2.2499 |
| **8** | **Gram** | Pulse | **118.19** | 99.41 | 0.8411 |
| **9** | **Groundnut** | Oilseed | **102.71** | 111.74 | 1.0880 |
| **10** | **Rapeseed &Mustard** | Oilseed | **86.57** | 90.87 | 1.0496 |

### 3.3 Top 10 Field Crops by Aggregate Yield (Efficiency Leaders, $N \\ge 100$)

| Rank | Crop Name | Crop Category | Aggregate Yield (T/Ha) | Total Production (MT) | Cultivated Area (MHa) |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **1** | **Sugarcane** | Cash Crop | **68.2453** | 5,208.05 | 76.31 |
| **2** | **Tapioca** | Tuber | **29.8526** | 105.01 | 3.52 |
| **3** | **Papaya** | Horticulture | **29.4829** | 3.92 | 0.13 |
| **4** | **Banana** | Horticulture | **27.8626** | 146.13 | 5.24 |
| **5** | **Grapes** | Horticulture | **26.1811** | 1.75 | 0.07 |
| **6** | **Potato** | Horticulture | **19.1064** | 424.78 | 22.23 |
| **7** | **Cabbage** | Horticulture | **15.3190** | 0.31 | 0.02 |
| **8** | **Pineapple** | Horticulture | **13.0720** | 2.13 | 0.16 |
| **9** | **Jute** | Fiber | **12.3286** | 181.56 | 14.73 |
| **10** | **Onion** | Horticulture | **11.4834** | 72.40 | 6.30 |

---

"""
    content = content.replace(old_rankings, new_rankings)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated docs/AGRICULTURAL_ANALYSIS.md successfully.")


def update_rainfall_analysis():
    filepath = "docs/RAINFALL_ANALYSIS.md"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Document both unweighted state-average and IMD area-weighted LPA
    old_sec1 = find_block(r"## 1\. 115-Year National Meteorological Historical Overview.*?(?=---)", content)
    new_sec1 = """## 1. 115-Year National Meteorological Historical Overview (1901–2015)

The India Meteorological Department (IMD) rainfall dataset contains **3,772 records** across 115 years (1901–2015) spanning 36 meteorological subdivisions aligned with 33 modern administrative states.

### Summary Statistics across 115 Years

In agro-meteorological research, national rainfall can be evaluated under two frameworks:
1. **Database Unweighted State-Average LPA:** Direct average across all 33 reporting administrative states/UTs in `rainfall_records` (plotted in `rainfall_115yr_trend.png`).
2. **Official IMD Area-Weighted LPA:** Standard national normal where each meteorological subdivision is weighted by geographic land area.

| Metric | Database Unweighted State-Average Baseline | Official IMD Area-Weighted Normal Baseline |
| :--- | :---: | :---: |
| **Annual Precipitation Mean (LPA)** | **1,608.94 mm** | **1,180.72 mm** |
| **Southwest Monsoon (Jun–Sep) Mean** | **1,164.53 mm (72.38%)** | **880.84 mm (74.60%)** |
| **Standard Deviation ($\\\\sigma$)** | 917.32 mm | 109.82 mm |
| **Coefficient of Variation ($CV\\\\%$)** | **57.01%** | **9.30%** |
| **Temporal Horizon** | 1901–2015 (115 years) | 1901–2015 (115 years) |
| **Observations Analyzed** | 3,772 state-year records | All-India area-weighted series |

> [!NOTE]
> **Methodological Clarification:** The unweighted database average ($1,608.94\\text{ mm}$) yields higher baseline values than the area-weighted national normal ($1,180.72\\text{ mm}$) because each state/UT receives equal weight in the database table, meaning small northeastern and island states with extreme rainfall (e.g., Meghalaya, Arunachal Pradesh, Goa, and A&N Islands receiving $2,500 - 3,500\\text{ mm}$) exert an equal arithmetic influence. Both baselines confirm the identical hydrological reality: the Southwest Monsoon contributes $>72-75\\%$ of annual precipitation.

"""
    content = content.replace(old_sec1, new_sec1)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated docs/RAINFALL_ANALYSIS.md successfully.")


def update_rainfall_agri_relationship():
    filepath = "docs/RAINFALL_AGRICULTURE_RELATIONSHIP.md"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    old_sec1 = find_block(r"## 1\. Paired Seasonal Correlation Analysis.*?(?=---)", content)
    new_sec1 = """## 1. Paired Seasonal Correlation Analysis & Simpson's Paradox

To evaluate how precipitation impacts agricultural outcomes, we analyzed paired seasonal relationships over the 1997–2015 overlapping horizon across all reporting Indian states.

Both parametric **Pearson correlation ($r$)** (measuring linear relationship) and non-parametric **Spearman rank correlation ($\\rho$)** (measuring monotonic relationship) were computed alongside two-tailed $p$-values.

### Paired Seasonal Statistical Relationships

| Analysis Pair | Agricultural Season | Paired Rainfall Variable | Sample Size ($N$) | Pearson $r$ | Pearson $p$-value | Spearman $\\rho$ | Spearman $p$-value | Statistically Significant ($\\alpha = 0.05$) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pre-Monsoon vs Summer Yield** | Summer | `pre_monsoon_rainfall_mm` | 312 | **+0.2198** | $9.34 \\times 10^{-5}$ | **+0.1842** | $1.08 \\times 10^{-3}$ | **Yes** |
| **Monsoon Rain vs Kharif Yield (Pooled)**| Kharif | `monsoon_rainfall_mm` | 496 | **-0.1364** | $0.0024$ | **-0.1120** | $0.0125$ | **Yes (Cross-Sectional)** |
| **Rabi Rain vs Rabi Yield** | Rabi | `rabi_rainfall_mm` | 429 | **-0.4671** | $1.22 \\times 10^{-24}$ | **-0.4978** | $1.05 \\times 10^{-28}$ | **Yes (Decoupled)** |

### Discovery: Simpson's Paradox in Agro-Meteorological Data
A critical statistical discovery in Stage 4 is the manifestation of **Simpson's Paradox** when evaluating pooled nationwide correlations versus within-state longitudinal correlations:
1. **Pooled Spatial Masking:** In the cross-sectional pooled analysis, `Monsoon Rain vs Kharif Yield` yields a mildly negative correlation ($r = -0.1364, p = 0.0024$). This counter-intuitive result occurs because semi-arid, canal-irrigated northwestern states (Punjab, Haryana) produce extremely high yields ($3.5 - 4.2\\text{ T/Ha}$) with low monsoon rainfall ($350 - 450\\text{ mm}$), whereas humid eastern and northeastern states (Assam, Meghalaya) receive massive monsoon rainfall ($>1,600\\text{ mm}$) but achieve modest yields ($1.0 - 1.5\\text{ T/Ha}$).
2. **Within-State Longitudinal Reality:** When evaluating year-over-year variations *within individual rainfed states*, rainfall correlation is strongly positive:
   - **Rajasthan Rice:** Pearson $r = +0.7340$ ($p = 0.0028$), Spearman $\\rho = +0.7407$
   - **Madhya Pradesh Rice:** Pearson $r = +0.7231$ ($p = 0.0023$), Spearman $\\rho = +0.7286$
   - **Chhattisgarh Rice:** Pearson $r = +0.5881$ ($p = 0.0211$), Spearman $\\rho = +0.6321$
   - **Telangana Rice:** Pearson $r = +0.5668$ ($p = 0.0177$), Spearman $\\rho = +0.5098$
   - **Gujarat Rice:** Pearson $r = +0.5429$ ($p = 0.0365$), Spearman $\\rho = +0.4679$
   - **Karnataka Rice:** Pearson $r = +0.5235$ ($p = 0.0258$), Spearman $\\rho = +0.4469$
   - **Odisha Rice:** Pearson $r = +0.5233$ ($p = 0.0259$), Spearman $\\rho = +0.7255$
3. **The Inundation / Flood Inversion:** In waterlogged, delta states, excess monsoon rainfall induces crop submergence and root hypoxia, producing negative correlations:
   - **West Bengal Rice:** Pearson $r = -0.5857$ ($p = 0.0107$), Spearman $\\rho = -0.7234$
   - **Sikkim Rice:** Pearson $r = -0.4811$ ($p = 0.0695$)
   - **Assam Rice:** Pearson $r = -0.2640$ ($p = 0.2899$)

"""
    content = content.replace(old_sec1, new_sec1)

    # Update Section 3: State-Level Contrast Table
    old_sec3 = find_block(r"## 3\. State-Level Sensitivity Divergence.*?(?=---)", content)
    new_sec3 = """## 3. State-Level Sensitivity Divergence (Canal vs Rainfed)

Evaluating Kharif Rice yield sensitivity to Monsoon rainfall across Indian states demonstrates how infrastructure alters climate vulnerability.

| State | Dominant Irrigation Type | Kharif Rice Yield Pearson $r$ | Spearman $\\rho$ | $p$-value | Mean Monsoon Rain (mm) | Mean Rice Yield (T/Ha) | Sensitivity Classification |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Rajasthan** | Semi-Arid Rainfed | **+0.7340** | **+0.7407** | $0.0028$ | 368.3 | 1.44 | **Extreme Climate Sensitivity** |
| **Madhya Pradesh** | Rainfed / Mixed | **+0.7231** | **+0.7286** | $0.0023$ | 937.9 | 1.00 | **Extreme Climate Sensitivity** |
| **Chhattisgarh** | Rainfed / Minor Canal | **+0.5881** | **+0.6321** | $0.0211$ | 1,129.4 | 1.39 | **High Climate Sensitivity** |
| **Telangana** | Mixed Rainfed / Well | **+0.5668** | **+0.5098** | $0.0177$ | 769.7 | 2.77 | **High Climate Sensitivity** |
| **Gujarat** | Semi-Arid Rainfed | **+0.5429** | **+0.4679** | $0.0365$ | 730.4 | 1.68 | **High Climate Sensitivity** |
| **Karnataka** | Mixed Rainfed / Tank | **+0.5235** | **+0.4469** | $0.0258$ | 1,435.7 | 2.54 | **High Climate Sensitivity** |
| **Odisha** | Rainfed / Minor Canal | **+0.5233** | **+0.7255** | $0.0259$ | 1,161.0 | 1.06 | **High Climate Sensitivity** |
| **Punjab** | Perennial Canal / Tubewell | **+0.2553** | **+0.3333** | $0.3066$ | 393.8 | 3.73 | **Decoupled (Irrigated)** |
| **Uttar Pradesh** | Canal / Deep Tubewell | **+0.1419** | **+0.1744** | $0.5744$ | 650.5 | 2.11 | **Decoupled (Irrigated)** |
| **Assam** | Flood-Prone Rainfed | **-0.2640** | **-0.2590** | $0.2899$ | 1,614.4 | 1.02 | **Negative (Flood Prone)** |
| **West Bengal** | Deltaic / Lowland Flooding | **-0.5857** | **-0.7234** | $0.0107$ | 1,579.6 | 2.08 | **Negative (Submergence Shock)** |

```mermaid
graph LR
    subgraph IrrigatedStates["Intensively Irrigated (r ≈ 0.15 - 0.25, Insignificant)"]
        Punjab["Punjab (r = +0.26, p = 0.31)"]
        UP["Uttar Pradesh (r = +0.14, p = 0.57)"]
    end
    subgraph RainfedStates["Predominantly Rainfed (r > +0.50, p < 0.05)"]
        Rajasthan["Rajasthan (r = +0.73)"]
        MP["Madhya Pradesh (r = +0.72)"]
        Chhattisgarh["Chhattisgarh (r = +0.59)"]
        Odisha["Odisha (r = +0.52)"]
    end
    subgraph FloodStates["Delta / Flood Inundation (r < 0, p < 0.05)"]
        WB["West Bengal (r = -0.59)"]
    end
    IrrigatedStates -->|"Canals & Deep Tubewells"| HighYield["High, Stable Yield (2.1 - 3.7 T/Ha)"]
    RainfedStates -->|"Direct Rainfall Dependence"| VolatileYield["Volatile Yield (1.0 - 1.4 T/Ha)"]
    FloodStates -->|"Waterlogging & Submergence"| SubmergedYield["Crop Inundation Shock"]
```

"""
    content = content.replace(old_sec3, new_sec3)

    # Update Outliers section
    old_outliers = find_block(r"## 4\. Outlier Analysis & Anomaly Classification.*?(?=\Z)", content)
    new_outliers = """## 4. Outlier Analysis & Anomaly Classification

Using both Tukey's **Interquartile Range (IQR)** method ($[Q_1 - 1.5 \\times IQR, Q_3 + 1.5 \\times IQR]$) and **Z-score standardization** ($|z| > 3.0$), we performed comprehensive anomaly detection across the 240,338 field crop records.

### Macro Anomaly Summary Table

| Category | Detection Criteria | Record Count | Percentage | Classification / Nature of Anomaly |
| :--- | :--- | :---: | :---: | :--- |
| **Suspicious Tiny Area High Production** | $\\text{Area} < 5\\text{ ha}$, $\\text{Prod} > 100\\text{ T}$ ($\\text{Yield} > 50\\text{ T/Ha}$) (excl. Sugarcane) | 20 | 0.008% | **Data Entry Clerical Artifact:** Likely clerical misplacement of decimal point or incorrect unit reporting. |
| **Severe Crop Failure Records** | $\\text{Yield} < 0.01\\text{ T/Ha}$ with $\\text{Area} > 100\\text{ ha}$ | 878 | 0.365% | **Authentic Natural Shocks:** Severe historical drought, pest infestation (e.g. bollworm in cotton), or catastrophic flooding. |
| **Sugarcane High Yields** | $\\text{Yield} > 120.55\\text{ T/Ha}$ ($Q_3 + 1.5 \\times IQR$) | 154 | 0.064% | **Biomass Reality:** Intensive tropical cultivation (Tamil Nadu, Maharashtra) where record yields exceed $120\\text{ T/Ha}$. |
| **Rice Upper Yield Outliers** | $\\text{Yield} > 4.50\\text{ T/Ha}$ ($Q_3 + 1.5 \\times IQR$) | 153 | 1.014% | **Productivity Hotspots:** Intensive irrigated paddy in Punjab, coastal Andhra, and Tamil Nadu delta tracts. |

### Machine Learning Preparation Recommendations
1. **Trim Clerical Artifacts:** The 20 records with impossible yields on small plots ($<5\\text{ ha}$) should be filtered out before training regression models.
2. **Retain Authentic Natural Shocks:** Crop failure observations ($N=878$) must be preserved during ML training so models learn to predict yield depressions during drought.
3. **Log-Transform High Skew Targets:** Apply log transformation $\\log(1 + \\text{yield})$ or box-cox transformation to normalize the right-skewed target distribution.
"""
    content = content.replace(old_outliers, new_outliers)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated docs/RAINFALL_AGRICULTURE_RELATIONSHIP.md successfully.")


def update_statistical_findings():
    filepath = "docs/STATISTICAL_FINDINGS.md"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    old_factsheet = find_block(r"### Master Statistical Fact Sheet.*?(?=---)", content)
    new_factsheet = """### Master Statistical Fact Sheet

| Quantitative Metric | Exact Evaluated Value | Statistical Context / Interpretation |
| :--- | :--- | :--- |
| **Total Ingested Observations** | **242,296 agricultural, 3,772 rainfall** | 100% verified against Neon primary source of truth. |
| **Field Crop Observations** | **240,338 records** | Yield measured in Metric Tonnes per Hectare ($\\text{T/Ha}$). |
| **Coconut Observations** | **1,958 records** | Yield strictly segregated; measured in Nuts per Hectare. |
| **Field Crop Yield: Mean vs Median** | **Mean: 4.42 T/Ha, Median: 1.00 T/Ha** | Extreme right skewness ($\\\\sigma = 12.11\\\\text{ T/Ha}, \\\\text{IQR} = 1.78\\\\text{ T/Ha}$). |
| **National Production (1997 vs Peak 2013)** | **1997: 537.51 MT $\\\\to$ 2013: 683.69 MT** | Complete field crop harvest series; peak reached in 2013. |
| **National Cultivated Area** | **1997: 230.37 MHa $\\\\to$ 2013: 139.68 MHa** | Stabilized around $140 - 175\\\\text{ MHa}$ across full reporting years. |
| **National Aggregate Yield Gain** | **1997: 2.33 T/Ha $\\\\to$ 2013: 4.89 T/Ha $\\\\to$ 2014: 5.22 T/Ha** | Driven by yield intensification and mechanization. |
| **Kharif Season Acreage Dominance**| **48.06% of total cultivated area** | 1,403.36 MHa cultivated during Southwest Monsoon. |
| **Rabi Season Crop Area** | **32.46% of total cultivated area** | 947.91 MHa cultivated under winter season. |
| **Whole Year Production Dominance** | **37.87% of production (4,115.58 MT)** | Driven by perennial high-biomass Sugarcane ($18.21\\\\text{ T/Ha}$). |
| **Top Producing Crop by Tonnage** | **Sugarcane: 5,208.05 Million Tonnes** | High biomass perennial cash crop ($68.25\\\\text{ T/Ha}$ aggregate yield). |
| **Top Cultivated Crop by Acreage** | **Rice: 746.32 Million Hectares** | Core staple grain across India ($1,605.22\\\\text{ MT}$ production). |
| **Top Agricultural State (Volume)**| **Uttar Pradesh: 3,234.49 Million Tonnes** | Produces $>30\\\\%$ of all national field crop output ($7.46\\\\text{ T/Ha}$). |
| **Top Agricultural State (Yield)** | **Tamil Nadu: 8.95 T/Ha aggregate yield** | Intensive sugarcane, delta paddy, and banana cultivation. |
| **Most Diversified State** | **Karnataka (Effective Crops: 17.1)** | Polyculture spreading climatic and market risks ($H' = 2.84$). |
| **Monoculture Concentration** | **Punjab (Wheat + Rice = 84.6% of area)**| Intensive Green Revolution cereal duopoly ($H' = 1.24$). |
| **Rainfall Baseline (State-Avg LPA)**| **1,608.94 mm (Std: 917.32 mm, CV: 57.01%)** | Unweighted database state-average mean precipitation (1901–2015). |
| **Rainfall Baseline (IMD National LPA)**| **1,180.72 mm (Std: 109.82 mm, CV: 9.30%)** | Official IMD area-weighted all-India normal. |
| **Southwest Monsoon Proportion** | **72.38% (1,164.53 mm)** | Principal hydrological contributor to Indian water table. |
| **Pre-Monsoon vs Summer Yield** | **Pearson $r = +0.2198$ ($p = 9.34 \\\\times 10^{-5}$)** | Statistically significant positive relationship. |
| **Simpson's Paradox (Pooled Kharif)**| **Pearson $r = -0.1364$ ($p = 0.0024$)** | Spatial confounding: high-yield irrigated vs rainfed states. |
| **Rainfed State Sensitivity** | **Rajasthan ($r = +0.73$), MP ($r = +0.72$), Odisha ($r = +0.52$)** | Direct, acute sensitivity of rice yield to monsoon rainfall. |
| **Flood Inundation State Sensitivity**| **West Bengal ($r = -0.59, p = 0.0107$)** | Excess rainfall triggers waterlogging and submergence yield loss. |
| **Irrigated Decoupling** | **Punjab ($r = +0.26, p = 0.31$), UP ($r = +0.14, p = 0.57$)** | Tubewell and canal infrastructure shields yields from rainfall. |

"""
    content = content.replace(old_factsheet, new_factsheet)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated docs/STATISTICAL_FINDINGS.md successfully.")


if __name__ == "__main__":
    update_agricultural_analysis()
    update_rainfall_analysis()
    update_rainfall_agri_relationship()
    update_statistical_findings()
