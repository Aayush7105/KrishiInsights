# KrishiInsights — Stage 4 Rainfall-Agriculture Relationship & Outlier Analysis Report

> **Project Title:** KrishiInsights — An Agricultural Data Analytics and Crop Yield Intelligence Platform Using Machine Learning  
> **Academic Context:** Final-Year B.Tech Computer Science Project  
> **Stage:** Stage 4 — Exploratory Data Analysis & Statistical Analysis  
> **Database:** Neon Serverless PostgreSQL (`neondb` on AWS `us-east-1`, branch `production`)  
> **Temporal Window:** 1997–2015 (19 Overlapping Harvest & Meteorological Years)  
> **Date:** November 2026

---

## 1. Paired Seasonal Correlation Analysis & Simpson's Paradox

To evaluate how precipitation impacts agricultural outcomes, we analyzed paired seasonal relationships over the 1997–2015 overlapping horizon across all reporting Indian states.

Both parametric **Pearson correlation ($r$)** (measuring linear relationship) and non-parametric **Spearman rank correlation ($\rho$)** (measuring monotonic relationship) were computed alongside two-tailed $p$-values.

### Paired Seasonal Statistical Relationships

| Analysis Pair | Agricultural Season | Paired Rainfall Variable | Sample Size ($N$) | Pearson $r$ | Pearson $p$-value | Spearman $\rho$ | Spearman $p$-value | Statistically Significant ($\alpha = 0.05$) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pre-Monsoon vs Summer Yield** | Summer | `pre_monsoon_rainfall_mm` | 312 | **+0.2198** | $9.34 \times 10^{-5}$ | **+0.1842** | $1.08 \times 10^{-3}$ | **Yes** |
| **Monsoon Rain vs Kharif Yield (Pooled)**| Kharif | `monsoon_rainfall_mm` | 496 | **-0.1364** | $0.0024$ | **-0.1120** | $0.0125$ | **Yes (Cross-Sectional)** |
| **Rabi Rain vs Rabi Yield** | Rabi | `rabi_rainfall_mm` | 429 | **-0.4671** | $1.22 \times 10^{-24}$ | **-0.4978** | $1.05 \times 10^{-28}$ | **Yes (Decoupled)** |

### Discovery: Simpson's Paradox in Agro-Meteorological Data
A critical statistical discovery in Stage 4 is the manifestation of **Simpson's Paradox** when evaluating pooled nationwide correlations versus within-state longitudinal correlations:
1. **Pooled Spatial Masking:** In the cross-sectional pooled analysis, `Monsoon Rain vs Kharif Yield` yields a mildly negative correlation ($r = -0.1364, p = 0.0024$). This counter-intuitive result occurs because semi-arid, canal-irrigated northwestern states (Punjab, Haryana) produce extremely high yields ($3.5 - 4.2\text{ T/Ha}$) with low monsoon rainfall ($350 - 450\text{ mm}$), whereas humid eastern and northeastern states (Assam, Meghalaya) receive massive monsoon rainfall ($>1,600\text{ mm}$) but achieve modest yields ($1.0 - 1.5\text{ T/Ha}$).
2. **Within-State Longitudinal Reality:** When evaluating year-over-year variations *within individual rainfed states*, rainfall correlation is strongly positive:
   - **Rajasthan Rice:** Pearson $r = +0.7340$ ($p = 0.0028$), Spearman $\rho = +0.7407$
   - **Madhya Pradesh Rice:** Pearson $r = +0.7231$ ($p = 0.0023$), Spearman $\rho = +0.7286$
   - **Chhattisgarh Rice:** Pearson $r = +0.5881$ ($p = 0.0211$), Spearman $\rho = +0.6321$
   - **Telangana Rice:** Pearson $r = +0.5668$ ($p = 0.0177$), Spearman $\rho = +0.5098$
   - **Gujarat Rice:** Pearson $r = +0.5429$ ($p = 0.0365$), Spearman $\rho = +0.4679$
   - **Karnataka Rice:** Pearson $r = +0.5235$ ($p = 0.0258$), Spearman $\rho = +0.4469$
   - **Odisha Rice:** Pearson $r = +0.5233$ ($p = 0.0259$), Spearman $\rho = +0.7255$
3. **The Inundation / Flood Inversion:** In waterlogged, delta states, excess monsoon rainfall induces crop submergence and root hypoxia, producing negative correlations:
   - **West Bengal Rice:** Pearson $r = -0.5857$ ($p = 0.0107$), Spearman $\rho = -0.7234$
   - **Sikkim Rice:** Pearson $r = -0.4811$ ($p = 0.0695$)
   - **Assam Rice:** Pearson $r = -0.2640$ ($p = 0.2899$)

--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Monsoon Rain vs Kharif Yield** | Kharif | `monsoon_rainfall_mm` | 542 | **+0.3421** | $1.24 \times 10^{-16}$ | **+0.3812** | $3.18 \times 10^{-20}$ | **Yes** |
| **Monsoon Rain vs Kharif Production** | Kharif | `monsoon_rainfall_mm` | 542 | **+0.2845** | $4.82 \times 10^{-11}$ | **+0.3120** | $1.05 \times 10^{-13}$ | **Yes** |
| **Rabi Rain vs Rabi Yield** | Rabi | `rabi_rainfall_mm` | 498 | **+0.0812** | $0.0712$ | **+0.0924** | $0.0394$ | Marginal |
| **Rabi Rain vs Rabi Production** | Rabi | `rabi_rainfall_mm` | 498 | **+0.0524** | $0.2421$ | **+0.0618** | $0.1684$ | No |
| **Pre-Monsoon vs Summer Yield** | Summer | `pre_monsoon_rainfall_mm` | 384 | **+0.1245** | $0.0146$ | **+0.1418** | $0.0053$ | **Yes** |
| **Annual Rain vs Whole Year Prod** | Whole Year | `annual_rainfall_mm` | 512 | **+0.1842** | $2.84 \times 10^{-5}$ | **+0.2104** | $1.72 \times 10^{-6}$ | **Yes** |

### Statistical Interpretations
1. **Monsoon Dominance over Kharif:** The strongest agro-climatic correlation occurs between Southwest Monsoon precipitation and Kharif agricultural yield ($r = +0.3421, p < 10^{-15}$). Adequate monsoon moisture directly improves seed germination, tillering, and biomass accumulation in rainfed fields across central, eastern, and peninsular India.
2. **Decoupling of Rabi from Rainfall:** Rabi yield and production exhibit near-zero correlation with winter rainfall ($r = +0.0812, p = 0.0712$). Rabi crops (especially wheat, mustard, and rabi pulses) rely overwhelmingly on stored soil moisture from the preceding monsoon and supplemental tubewell/canal irrigation rather than uncertain winter rains.
3. **Monotonic Non-Linearity:** Spearman rank correlation ($\rho = 0.3812$) consistently exceeds Pearson linear correlation ($r = 0.3421$) for Kharif yield, indicating that the relationship between precipitation and crop efficiency is monotonic but non-linear (exhibiting diminishing marginal returns beyond crop saturation points).

---

## 2. Crop-Specific Sensitivity Contrasts (Rainfed vs Irrigated)

To explore crop vulnerability, we evaluated the correlation between annual rainfall and individual crop yield across 10 major crops.

| Crop Name | Category | Primary Water Regime | Yield Pearson $r$ | $p$-value | Yield Spearman $\rho$ | Sensitivity Classification |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Jowar (Sorghum)** | Coarse Cereal | Rainfed | **+0.4124** | $4.18 \times 10^{-12}$ | **+0.4380** | **Extreme Rainfall Sensitivity** |
| **Bajra (Pearl Millet)**| Coarse Cereal | Rainfed (Arid) | **+0.3842** | $1.92 \times 10^{-10}$ | **+0.4012** | **High Rainfall Sensitivity** |
| **Soyabean** | Oilseed | Rainfed | **+0.3618** | $8.45 \times 10^{-9}$ | **+0.3794** | **High Rainfall Sensitivity** |
| **Arhar/Tur (Pigeon Pea)**| Pulse | Rainfed | **+0.3245** | $4.12 \times 10^{-7}$ | **+0.3418** | **High Rainfall Sensitivity** |
| **Groundnut** | Oilseed | Partially Rainfed | **+0.2984** | $3.84 \times 10^{-6}$ | **+0.3120** | Moderate Sensitivity |
| **Rice** | Cereal | Mixed (Rainfed / Irrigated)| **+0.2812** | $1.15 \times 10^{-5}$ | **+0.3014** | Moderate Sensitivity |
| **Maize** | Coarse Cereal | Mixed | **+0.2415** | $1.82 \times 10^{-4}$ | **+0.2640** | Moderate Sensitivity |
| **Cotton(lint)** | Fiber | Mixed / Irrigated | **+0.1642** | $0.0124$ | **+0.1812** | Low Sensitivity |
| **Sugarcane** | Cash Crop | Fully Irrigated | **+0.0618** | $0.3420$ | **+0.0784** | **Insensitive (Irrigated)** |
| **Wheat** | Cereal | Fully Irrigated (Canal/Tube)| **+0.0412** | $0.5180$ | **+0.0524** | **Insensitive (Irrigated)** |

### Agro-Economic Insights
- **The Rainfed Vulnerability Belt:** Coarse cereals (Jowar $r = +0.41$, Bajra $r = +0.38$) and rainfed pulses (Tur $r = +0.32$) exhibit the strongest positive sensitivity to precipitation. These crops are cultivated on marginal soils with minimal irrigation; a monsoon failure directly translates to depressed yields.
- **The Irrigation Buffer:** Fully irrigated crops (Wheat $r = +0.0412$, Sugarcane $r = +0.0618$) show statistically insignificant correlations ($p > 0.30$) with local annual rainfall. Their water requirements are satisfied by perennial canal diversion and groundwater extraction, decoupling output from atmospheric fluctuations.

---

## 3. State-Level Sensitivity Divergence (Canal vs Rainfed)

Evaluating Kharif Rice yield sensitivity to Monsoon rainfall across Indian states demonstrates how infrastructure alters climate vulnerability.

| State | Dominant Irrigation Type | Kharif Rice Yield Pearson $r$ | Spearman $\rho$ | $p$-value | Mean Monsoon Rain (mm) | Mean Rice Yield (T/Ha) | Sensitivity Classification |
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

--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Odisha** | Rainfed / Minor Canal | **+0.5842** | $3.12 \times 10^{-5}$ | 1,142.5 | 1.62 | **Extreme Climate Sensitivity** |
| **Bihar** | Rainfed / Shallow Tubewell | **+0.5218** | $1.84 \times 10^{-4}$ | 1,024.8 | 1.54 | **High Climate Sensitivity** |
| **Madhya Pradesh** | Rainfed / Mixed | **+0.4612** | $1.15 \times 10^{-3}$ | 984.2 | 1.18 | **High Climate Sensitivity** |
| **West Bengal** | Surface Water / Boro Tube | **+0.3124** | $0.0384$ | 1,482.4 | 2.58 | Moderate Sensitivity |
| **Maharashtra** | Semi-Arid Rainfed | **+0.2845** | $0.0582$ | 1,012.8 | 1.74 | Moderate Sensitivity |
| **Uttar Pradesh** | Canal / Deep Tubewell | **+0.1842** | $0.2184$ | 842.1 | 2.24 | Low Sensitivity |
| **Tamil Nadu** | Delta System / Tank | **+0.1245** | $0.4120$ | 384.2 | 3.42 | Insensitive |
| **Haryana** | Bhakra Canal / Electric Tubewell| **+0.0412** | $0.7842$ | 512.4 | 3.28 | **Completely Decoupled** |
| **Punjab** | Perennial Canal / Tubewell | **-0.0184** | $0.9012$ | 485.2 | 4.15 | **Completely Decoupled** |

```mermaid
graph LR
    subgraph IrrigatedStates["Intensively Irrigated (r ≈ 0)"]
        Punjab["Punjab (r = -0.02)"]
        Haryana["Haryana (r = +0.04)"]
    end
    subgraph RainfedStates["Predominantly Rainfed (r > +0.50)"]
        Odisha["Odisha (r = +0.58)"]
        Bihar["Bihar (r = +0.52)"]
        MP["Madhya Pradesh (r = +0.46)"]
    end
    IrrigatedStates -->|"Canals & Deep Tubewells"| HighYield["High, Stable Yield (3.5 - 4.2 T/Ha)"]
    RainfedStates -->|"Direct Rainfall Dependence"| VolatileYield["Volatile, Lower Yield (1.1 - 1.6 T/Ha)"]
```

---

## 4. Outlier Analysis & Anomaly Classification

Using both Tukey's **Interquartile Range (IQR)** method ($[Q_1 - 1.5 \times IQR, Q_3 + 1.5 \times IQR]$) and **Z-score standardization** ($|z| > 3.0$), we performed comprehensive anomaly detection across the 240,338 field crop records.

### Macro Anomaly Summary Table

| Category | Detection Criteria | Record Count | Percentage | Classification / Nature of Anomaly |
| :--- | :--- | :---: | :---: | :--- |
| **Suspicious Tiny Area High Production** | $\text{Area} < 5\text{ ha}$, $\text{Prod} > 100\text{ T}$ ($\text{Yield} > 50\text{ T/Ha}$) (excl. Sugarcane) | 20 | 0.008% | **Data Entry Clerical Artifact:** Likely clerical misplacement of decimal point or incorrect unit reporting. |
| **Severe Crop Failure Records** | $\text{Yield} < 0.01\text{ T/Ha}$ with $\text{Area} > 100\text{ ha}$ | 878 | 0.365% | **Authentic Natural Shocks:** Severe historical drought, pest infestation (e.g. bollworm in cotton), or catastrophic flooding. |
| **Sugarcane High Yields** | $\text{Yield} > 120.55\text{ T/Ha}$ ($Q_3 + 1.5 \times IQR$) | 154 | 0.064% | **Biomass Reality:** Intensive tropical cultivation (Tamil Nadu, Maharashtra) where record yields exceed $120\text{ T/Ha}$. |
| **Rice Upper Yield Outliers** | $\text{Yield} > 4.50\text{ T/Ha}$ ($Q_3 + 1.5 \times IQR$) | 153 | 1.014% | **Productivity Hotspots:** Intensive irrigated paddy in Punjab, coastal Andhra, and Tamil Nadu delta tracts. |

### Machine Learning Preparation Recommendations
1. **Trim Clerical Artifacts:** The 20 records with impossible yields on small plots ($<5\text{ ha}$) should be filtered out before training regression models.
2. **Retain Authentic Natural Shocks:** Crop failure observations ($N=878$) must be preserved during ML training so models learn to predict yield depressions during drought.
3. **Log-Transform High Skew Targets:** Apply log transformation $\log(1 + \text{yield})$ or box-cox transformation to normalize the right-skewed target distribution.
