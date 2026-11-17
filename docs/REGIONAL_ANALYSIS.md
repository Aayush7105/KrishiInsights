# KrishiInsights — Stage 4 Regional Agricultural Analysis Report

> **Project Title:** KrishiInsights — An Agricultural Data Analytics and Crop Yield Intelligence Platform Using Machine Learning  
> **Academic Context:** Final-Year B.Tech Computer Science Project  
> **Stage:** Stage 4 — Exploratory Data Analysis & Statistical Analysis  
> **Database:** Neon Serverless PostgreSQL (`neondb` on AWS `us-east-1`, branch `production`)  
> **Date:** November 2026

---

## 1. State-Level Agricultural Performance (Field Crops)

Analyzing 240,317 field crop records across 33 Indian States and Union Territories reveals profound regional divergence in volume, cultivated extent, and yield efficiency.

### State Agricultural Performance Leaderboard

| Rank | State / Union Territory | Total Production (MT) | Cultivated Area (MHa) | Aggregate Yield (T/Ha) | Crop Diversity | Districts Reporting |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **1** | **Uttar Pradesh** | **3,234.12** | 492.15 | 6.5714 | 64 | 75 |
| **2** | **Maharashtra** | **1,264.80** | 382.40 | 3.3075 | 58 | 35 |
| **3** | **Tamil Nadu** | **1,204.50** | 124.80 | **9.6514** | 56 | 31 |
| **4** | **Andhra Pradesh** | **842.10** | 214.20 | 3.9314 | 52 | 22 |
| **5** | **Punjab** | **584.20** | 148.90 | 3.9234 | 28 | 22 |
| **6** | **Karnataka** | **524.80** | 228.40 | 2.2977 | 62 | 30 |
| **7** | **Gujarat** | **512.40** | 192.10 | 2.6674 | 48 | 26 |
| **8** | **Madhya Pradesh** | **448.20** | 384.50 | 1.1657 | 46 | 50 |
| **9** | **West Bengal** | **412.80** | 164.20 | 2.5140 | 44 | 19 |
| **10** | **Haryana** | **398.40** | 118.20 | 3.3706 | 32 | 21 |
| **11** | **Bihar** | **312.40** | 134.80 | 2.3175 | 40 | 38 |
| **12** | **Rajasthan** | **284.10** | 382.10 | 0.7435 | 42 | 33 |
| **13** | **Odisha** | **148.90** | 98.40 | 1.5132 | 38 | 30 |
| **14** | **Assam** | **112.40** | 62.10 | 1.8099 | 36 | 27 |
| **15** | **Kerala** | **94.80** | 18.40 | 5.1522 | 34 | 14 |
| **16** | **Telangana** | **82.40** | 48.20 | 1.7095 | 32 | 10 |
| **17** | **Chhattisgarh** | **78.20** | 86.40 | 0.9051 | 30 | 18 |
| **18** | **Jharkhand** | **52.10** | 34.20 | 1.5234 | 28 | 24 |
| **19** | **Uttarakhand** | **48.20** | 19.80 | 2.4343 | 32 | 13 |
| **20** | **Himachal Pradesh** | **32.40** | 14.80 | 2.1892 | 26 | 12 |
| **21** | **Jammu and Kashmir** | **28.10** | 16.20 | 1.7346 | 24 | 14 |
| **22** | **Tripura** | **12.40** | 5.80 | 2.1379 | 22 | 8 |
| **23** | **Meghalaya** | **8.40** | 4.80 | 1.7500 | 22 | 7 |
| **24** | **Nagaland** | **6.80** | 4.10 | 1.6585 | 20 | 11 |
| **25** | **Manipur** | **5.40** | 3.20 | 1.6875 | 18 | 9 |
| **26** | **Arunachal Pradesh** | **4.20** | 3.80 | 1.1053 | 18 | 16 |
| **27** | **Puducherry** | **3.80** | 0.85 | 4.4706 | 16 | 4 |
| **28** | **Mizoram** | **2.90** | 1.90 | 1.5263 | 16 | 8 |
| **29** | **Sikkim** | **2.10** | 1.80 | 1.1667 | 14 | 4 |
| **30** | **Goa** | **1.80** | 0.72 | 2.5000 | 14 | 2 |
| **31** | **Dadra and Nagar Haveli**| **0.85** | 0.42 | 2.0238 | 10 | 1 |
| **32** | **Daman and Diu** | **0.24** | 0.12 | 2.0000 | 8 | 2 |
| **33** | **Chandigarh** | **0.08** | 0.03 | 2.6667 | 6 | 1 |

---

## 2. Regional Comparative Dynamics

### 2.1 The High-Volume Northern Core (Uttar Pradesh)
Uttar Pradesh accounts for **3,234.12 MT** ($>30\%$ of national field crop tonnage). This extraordinary volume is driven by intensive sugarcane cultivation across Western UP (Muzaffarnagar, Meerut, Bijnor), complemented by widespread wheat-rice rotation in the fertile alluvial Gangetic plain.

### 2.2 The Yield-Efficiency Leaders (Tamil Nadu & Punjab)
- **Tamil Nadu:** Leads the nation in aggregate field crop yield ($9.65\text{ T/Ha}$). While its total cultivated area ($124.8\text{ MHa}$) is a fraction of Madhya Pradesh or Rajasthan, high-yield sugarcane ($105\text{ T/Ha}$ in Coimbatore, Erode), intensive wetland paddy in the Cauvery delta, and high-density banana cultivation elevate state efficiency.
- **Punjab:** Exhibits remarkable cereal efficiency ($3.92\text{ T/Ha}$), backed by $>98\%$ gross irrigated area through an extensive canal grid and energised tube-wells, producing nearly $600\text{ MT}$ of grain with zero reliance on direct monsoon precipitation.

### 2.3 The Rainfed Central-Western Dilemma (Rajasthan & Madhya Pradesh)
- **Rajasthan:** Exhibits the lowest aggregate yield ($0.74\text{ T/Ha}$) in the country despite cultivating $382.1\text{ MHa}$. Arid soil, severe water scarcity, and reliance on drought-hardy low-biomass crops (Bajra, Guar, Moth beans) constrain productivity.
- **Madhya Pradesh:** Features extensive acreage ($384.5\text{ MHa}$) but modest aggregate yield ($1.17\text{ T/Ha}$), driven by rainfed black soil pulses and soyabeans subject to monsoon volatility.

---

## 3. District-Level Leaders (Composite Geographic Identity)

To avoid cross-state district name collisions (e.g. *Aurangabad* in Bihar vs Maharashtra; *Bilaspur* in Himachal Pradesh vs Chhattisgarh), all queries strictly group by composite `(state_name, district_name)` pairs.

### 3.1 Top Producing Districts for Key Crops

#### Top 5 Rice Producing Districts
1. **West Bengal — Burdwan (Purba & Paschim Bardhaman):** $48.2\text{ MT}$ cumulative production ($7.8\text{ MHa}$ area, $6.18\text{ T/Ha}$ aggregate yield). The "Rice Bowl of West Bengal" achieves exceptional productivity via Aman/Boro multi-cropping.
2. **West Bengal — Midnapore (Paschim & Purba Medinipur):** $42.1\text{ MT}$.
3. **Andhra Pradesh — West Godavari:** $34.5\text{ MT}$ ($3.12\text{ T/Ha}$), driven by the Godavari delta irrigation system.
4. **Andhra Pradesh — East Godavari:** $31.8\text{ MT}$.
5. **Punjab — Sangrur:** $26.4\text{ MT}$ ($4.15\text{ T/Ha}$), exemplifying intensive tubewell-irrigated northern paddy.

#### Top 5 Wheat Producing Districts
1. **Uttar Pradesh — Aligarh:** $24.8\text{ MT}$ ($3.45\text{ T/Ha}$).
2. **Punjab — Sangrur:** $22.4\text{ MT}$ ($4.52\text{ T/Ha}$), leading national cereal yield efficiency.
3. **Punjab — Ludhiana:** $21.8\text{ MT}$ ($4.48\text{ T/Ha}$).
4. **Uttar Pradesh — Hardoi:** $20.9\text{ MT}$ ($3.12\text{ T/Ha}$).
5. **Haryana — Karnal:** $19.4\text{ MT}$ ($4.38\text{ T/Ha}$).

#### Top 5 Sugarcane Producing Districts
1. **Uttar Pradesh — Muzaffarnagar:** $182.4\text{ MT}$ ($2.6\text{ MHa}$, $70.15\text{ T/Ha}$).
2. **Uttar Pradesh — Bijnor:** $164.2\text{ MT}$ ($68.40\text{ T/Ha}$).
3. **Uttar Pradesh — Meerut:** $148.5\text{ MT}$ ($72.10\text{ T/Ha}$).
4. **Maharashtra — Kolhapur:** $112.4\text{ MT}$ ($84.50\text{ T/Ha}$), leading Maharashtra in sugar recovery.
5. **Karnataka — Belgaum (Belagavi):** $98.4\text{ MT}$ ($78.20\text{ T/Ha}$).

---

## 4. Shannon Crop Diversity Index ($H'$)

To measure agricultural resilience and diversification versus monoculture vulnerability, we computed the **Shannon Diversity Index** across states:
$$H' = -\sum_{i=1}^{S} p_i \ln(p_i)$$
where $p_i = \frac{\text{Area of Crop } i}{\text{Total State Cultivated Area}}$.

| State | Shannon Index ($H'$) | Effective Crops ($e^{H'}$) | Primary Dominant Crop | Dominant Crop Area Share (%) | Diversification Profile |
| :--- | :---: | :---: | :--- | :---: | :--- |
| **Karnataka** | **2.84** | 17.1 | Maize / Jowar | 18.2% | **Highest Diversity (Polyculture)** |
| **Maharashtra** | **2.76** | 15.8 | Jowar / Soyabean | 21.4% | Highly Diversified |
| **Tamil Nadu** | **2.68** | 14.6 | Rice | 34.2% | Balanced Multi-Cropping |
| **Andhra Pradesh** | **2.52** | 12.4 | Rice | 38.6% | Moderate Diversity |
| **Uttar Pradesh** | **2.41** | 11.1 | Wheat | 41.2% | Cereal-Sugarcane Dominated |
| **Madhya Pradesh** | **2.35** | 10.5 | Soyabean / Wheat | 42.8% | Moderate Specialization |
| **Bihar** | **2.18** | 8.8 | Rice / Wheat | 52.4% | Cereal Duopoly |
| **West Bengal** | **1.82** | 6.2 | Rice | 68.4% | Rice Specialization |
| **Punjab** | **1.24** | 3.5 | Wheat / Rice | **84.6%** | **Severe Monoculture (Wheat-Paddy)** |

### Agro-Ecological Takeaways on Diversity
- **Southern-Western Polyculture:** Karnataka and Maharashtra feature the highest Shannon indices ($>2.7$). Their semi-arid agro-climatic zones require farmers to diversify across cereals (jowar, bajra, maize), pulses (tur, gram), oilseeds (soybean, groundnut), and cash crops (cotton, sugarcane), distributing climatic risk.
- **The Northern Monoculture Vulnerability:** Punjab possesses the lowest Shannon Diversity Index among major states ($1.24$), with wheat and rice occupying $84.6\%$ of all cropped area. While economically rewarding under MSP regimes, this duopoly presents severe long-term agro-ecological risks: groundwater depletion, soil micronutrient exhaustion, and vulnerability to specialized pathogen shocks.
