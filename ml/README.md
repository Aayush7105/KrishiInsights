# Machine Learning & Analytics Module (`ml/`)

This directory houses the exploratory data analysis (EDA), statistical modeling, analytical engines, feature engineering pipelines, model training workflows, and evaluation artifacts for **KrishiInsights**.

---

## 1. Directory Structure

```text
ml/
├── notebooks/                     # Executed Jupyter analysis notebooks (Stage 4)
│   ├── 01_agricultural_eda.ipynb
│   ├── 02_crop_analysis.ipynb
│   ├── 03_regional_analysis.ipynb
│   ├── 04_rainfall_analysis.ipynb
│   ├── 05_rainfall_agriculture_relationship.ipynb
│   └── build_notebooks.py         # Automated execution & generator pipeline
├── reports/
│   └── figures/                   # 15 High-resolution generated publication charts
│       ├── agri_trends_production_area.png
│       ├── agri_national_yield_trend.png
│       ├── agri_seasonal_distribution.png
│       ├── agri_top_crops_production.png
│       ├── agri_top_crops_area.png
│       ├── agri_top_crops_yield.png
│       ├── agri_yield_distributions.png
│       ├── rainfall_115yr_trend.png
│       ├── rainfall_lpa_deviations.png
│       ├── rainfall_seasonal_breakdown.png
│       ├── rainfall_wettest_driest_states.png
│       ├── correlation_rice_monsoon_scatter.png
│       ├── correlation_paired_heatmap.png
│       ├── correlation_state_sensitivity_contrast.png
│       └── outliers_crop_yield_boxplots.png
├── src/
│   ├── analytics/                 # Core analytical computation modules
│   │   ├── agricultural_eda.py    # Descriptive stats, trends, seasonal aggregations
│   │   ├── crop_analysis.py       # Single-crop profiles, top-10 rankings, CV variability
│   │   ├── regional_analysis.py   # State summaries, multi-state comparison, Shannon diversity
│   │   ├── rainfall_analysis.py   # 115-yr trends, LPA deviations, wettest/driest states
│   │   ├── correlation_analysis.py# Paired seasonal, crop-specific, state sensitivity
│   │   └── outlier_analysis.py    # IQR & Z-score detection, anomaly classification
│   ├── database/
│   │   └── connection.py          # Neon PostgreSQL connection pool & data loaders
│   └── visualization/             # High-resolution chart plotting engines
│       ├── agricultural_charts.py # Agricultural line, bar, KDE distribution charts
│       ├── rainfall_charts.py     # Meteorological series, LPA anomaly bars
│       ├── comparison_charts.py   # Scatter regressions, correlation heatmaps, boxplots
│       └── generate_all_figures.py# Driver script to render and save all 15 figures
├── tests/
│   └── test_analytics.py          # Unit & integration test suite (11 test cases)
├── requirements.txt               # Data science dependencies (Pandas, Scikit-learn, etc.)
└── README.md
```

---

## 2. Core Stage 4 Analytical Deliverables

### Analytical Modules (`ml/src/analytics/`)
1. **`agricultural_eda.py`:** Calculates descriptive statistics (mean, median, std, IQR, min, max) with strict unit isolation (Tonnes/Ha vs Nuts/Ha), annual aggregate trends, YoY growth percentages, and seasonal shares.
2. **`crop_analysis.py`:** Computes single-crop historical profiles, top 10 rankings by production, area, and yield, production variability ($CV\%$), and smoothed 3-year window growth/decline rankings.
3. **`regional_analysis.py`:** Provides state-level performance leaderboards across 33 states/UTs, multi-state comparative queries, composite district rankings `(state_name, district_name)`, and Shannon Crop Diversity Index calculations.
4. **`rainfall_analysis.py`:** Analyzes 115 years of IMD meteorological data (1901–2015), calculates Long Period Average (LPA = 1,180.7 mm), categorizes drought/excess years, and ranks wettest vs driest states.
5. **`correlation_analysis.py`:** Measures paired seasonal correlations (Pearson $r$ and Spearman $\rho$) across the 1997–2015 overlapping horizon, crop-specific rainfall sensitivity, and state-level sensitivity divergence.
6. **`outlier_analysis.py`:** Implements Tukey's IQR and Z-score outlier detection, differentiating clerical data artifacts from authentic agro-climatic extremes.

### Executed Jupyter Notebooks (`ml/notebooks/`)
The five programmatic, self-contained notebooks can be inspected or rerun anytime:
```bash
python ml/notebooks/build_notebooks.py
```

### Visual Artifacts (`ml/reports/figures/`)
All 15 publication-grade figures can be generated using:
```bash
python ml/src/visualization/generate_all_figures.py
```

---

## 3. Running Analytics Tests

To execute the automated test suite verifying analytical formulas and Neon database integration:
```bash
pytest ml/tests/test_analytics.py -v
```
*(All 11 unit and integration tests execute and pass cleanly).*
