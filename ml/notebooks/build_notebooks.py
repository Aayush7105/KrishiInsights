"""
Notebook Generator for KrishiInsights Stage 4.

Generates and executes the 5 Stage 4 analytical Jupyter notebooks:
- 01_agricultural_eda.ipynb
- 02_crop_analysis.ipynb
- 03_regional_analysis.ipynb
- 04_rainfall_analysis.ipynb
- 05_rainfall_agriculture_relationship.ipynb
"""

import os
import sys
import io
import contextlib
import nbformat as nbf

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath("."))
os.environ["MPLCONFIGDIR"] = os.path.abspath("tmp/matplotlib")

notebook_dir = "ml/notebooks"
os.makedirs(notebook_dir, exist_ok=True)


def execute_code(code_str: str, global_scope: dict) -> str:
    """Executes a block of Python code and captures its stdout."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            exec(code_str, global_scope)
        except Exception as e:
            print(f"Error executing cell: {e}")
    return buf.getvalue()


def build_and_save_notebook(filename: str, cells_data: list):
    """
    cells_data is a list of tuples:
    ('markdown', md_text) or ('code', code_text)
    """
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11"
        }
    }

    exec_scope = {}
    cell_idx = 1

    for cell_type, content in cells_data:
        if cell_type == "markdown":
            nb.cells.append(nbf.v4.new_markdown_cell(content))
        elif cell_type == "code":
            output_text = execute_code(content, exec_scope)
            outputs = []
            if output_text.strip():
                outputs.append(nbf.v4.new_output(output_type="stream", name="stdout", text=output_text))
            code_cell = nbf.v4.new_code_cell(content, execution_count=cell_idx, outputs=outputs)
            nb.cells.append(code_cell)
            cell_idx += 1

    filepath = os.path.join(notebook_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Created and executed notebook: {filepath}")


# ==========================================
# 1. 01_agricultural_eda.ipynb
# ==========================================
def create_nb01():
    cells = [
        ("markdown", """# KrishiInsights — Agricultural Exploratory Data Analysis (EDA)

**Project:** KrishiInsights (Agricultural Data Analytics & Crop Yield Intelligence Platform)  
**Database:** Neon Serverless PostgreSQL (`neondb`)  
**Stage:** 4 (Statistical Analysis & Exploratory Data Analysis)

### Objectives
1. Inspect metadata and high-level distribution of agricultural records.
2. Calculate national descriptive statistics with strict unit segregation (Metric Tonnes vs Number of Nuts).
3. Compute historical production, area, and aggregate yield trends (1997–2015) with YoY percentage growth.
4. Analyze seasonal production distribution across Kharif, Rabi, Summer, Autumn, Winter, and Whole Year.
"""),
        ("code", """import os
import sys
sys.path.insert(0, os.path.abspath("../.."))

import pandas as pd
from ml.src.analytics.agricultural_eda import (
    calculate_overall_summary_statistics,
    get_annual_production_trends,
    get_seasonal_distribution,
    get_yearly_record_distribution
)

print("Modules successfully imported.")
"""),
        ("markdown", """## 1. High-Level Summary Statistics
Isolates Field Crops (`Tonnes/Hectare`) from Coconut (`Nuts/Hectare`).
"""),
        ("code", """stats = calculate_overall_summary_statistics()

print("=== Agricultural Dataset Metadata ===")
for k, v in stats["metadata"].items():
    print(f"  {k}: {v:,}" if isinstance(v, (int, float)) else f"  {k}: {v}")

print("\\n=== Field Crops Summary (Metric Tonnes / Hectares) ===")
for k, v in stats["field_crops"].items():
    print(f"  {k}: {v}")

print("\\n=== Coconut Summary (Number of Nuts / Hectares) ===")
for k, v in stats["coconut"].items():
    print(f"  {k}: {v}")
"""),
        ("markdown", """## 2. Annual Production, Area, and Aggregate Yield Trends (1997–2015)
Computes mathematically sound national yield:
$$\\text{Aggregate Yield} = \\frac{\\sum \\text{Production}}{\\sum \\text{Area}}$$
"""),
        ("code", """trends_df = get_annual_production_trends(unit_filter="Tonnes/Hectare")
display_cols = ["year", "total_production", "total_area", "aggregate_yield", "production_yoy_pct", "yield_yoy_pct", "production_index_1997"]
print(trends_df[display_cols].to_string(index=False))
"""),
        ("markdown", """## 3. Seasonal Agricultural Breakdown
Examines production and cultivated area shares across crop seasons.
"""),
        ("code", """seasonal_df = get_seasonal_distribution(exclude_coconut=True)
print(seasonal_df[["season", "record_count", "total_production", "total_area", "aggregate_yield", "production_share_pct", "area_share_pct"]].to_string(index=False))
"""),
        ("markdown", """## 4. Yearly Record Distribution
Validates observation density per harvest year.
"""),
        ("code", """record_dist_df = get_yearly_record_distribution()
print(record_dist_df.to_string(index=False))
""")
    ]
    build_and_save_notebook("01_agricultural_eda.ipynb", cells)


# ==========================================
# 2. 02_crop_analysis.ipynb
# ==========================================
def create_nb02():
    cells = [
        ("markdown", """# KrishiInsights — Crop Performance & Comparative Analysis

**Project:** KrishiInsights  
**Database:** Neon Serverless PostgreSQL (`neondb`)  
**Stage:** 4 (Statistical Analysis & Exploratory Data Analysis)

### Objectives
1. Deep single-crop historical performance profiling (Rice, Wheat, Sugarcane).
2. National crop rankings across 124 crops by Production, Cultivated Area, and Aggregate Yield.
3. Production variability analysis using Coefficient of Variation ($CV = \\frac{\\sigma}{\\mu} \\times 100$).
4. Long-term crop growth and decline rankings comparing smoothed 3-year windows (1997–1999 vs 2013–2015).
"""),
        ("code", """import os
import sys
sys.path.insert(0, os.path.abspath("../.."))

import pandas as pd
from ml.src.analytics.crop_analysis import (
    get_crop_historical_profile,
    get_top_crops_rankings,
    get_crop_growth_and_decline_rankings
)

print("Crop analysis modules successfully imported.")
"""),
        ("markdown", """## 1. Single-Crop Deep Profile: Rice
Analyzes national production trend, top producing states, and composite districts.
"""),
        ("code", """rice_profile = get_crop_historical_profile("Rice")

print(f"Crop: {rice_profile['crop_name']}")
print(f"Mean Annual Production: {rice_profile['mean_annual_production']:,} {rice_profile['production_unit']}")
print(f"Production CV: {rice_profile['production_cv_pct']}%")
print(f"Peak Year: {rice_profile['max_production_year']} ({rice_profile['max_production']:,} Tonnes)")
print(f"Lowest Year: {rice_profile['min_production_year']} ({rice_profile['min_production']:,} Tonnes)")

print("\\n--- Top 5 Rice Producing States ---")
print(rice_profile["top_states"].to_string(index=False))

print("\\n--- Top 5 Rice Producing Districts ---")
print(rice_profile["top_districts"].to_string(index=False))
"""),
        ("markdown", """## 2. Top 10 Indian Field Crops Rankings
Ranked independently by cumulative production, cultivated area, and aggregate yield.
"""),
        ("code", """top_prod = get_top_crops_rankings(metric="production", limit=10)
print("=== Top 10 Crops by Cumulative Production (Tonnes) ===")
print(top_prod[["crop_name", "crop_category", "total_production", "aggregate_yield"]].to_string(index=False))

top_area = get_top_crops_rankings(metric="area", limit=10)
print("\\n=== Top 10 Crops by Cultivated Area (Hectares) ===")
print(top_area[["crop_name", "crop_category", "total_area", "aggregate_yield"]].to_string(index=False))

top_yield = get_top_crops_rankings(metric="yield", limit=10)
print("\\n=== Top 10 Field Crops by Aggregate Yield (Tonnes/Ha) ===")
print(top_yield[["crop_name", "crop_category", "aggregate_yield", "total_production"]].to_string(index=False))
"""),
        ("markdown", """## 3. Crop Growth and Decline Analysis
Compares baseline (1997–1999) vs ending horizon (2013–2015) using 3-year smoothed averages.
"""),
        ("code", """growth_analysis = get_crop_growth_and_decline_rankings(limit=5)

print("=== Top 5 Fastest Growing Crops ===")
print(growth_analysis["fastest_growing"].to_string(index=False))

print("\\n=== Top 5 Declining Crops ===")
print(growth_analysis["declining"].to_string(index=False))
""")
    ]
    build_and_save_notebook("02_crop_analysis.ipynb", cells)


# ==========================================
# 3. 03_regional_analysis.ipynb
# ==========================================
def create_nb03():
    cells = [
        ("markdown", """# KrishiInsights — Regional Agricultural Analysis

**Project:** KrishiInsights  
**Database:** Neon Serverless PostgreSQL (`neondb`)  
**Stage:** 4 (Statistical Analysis & Exploratory Data Analysis)

### Objectives
1. State-level agricultural performance summaries across all 33 Indian States & Union Territories.
2. Comparative multi-state analysis over common time horizons.
3. Top producing district rankings utilizing composite `(state_name, district_name)` pairs.
4. Shannon Crop Diversity Index ($H' = -\\sum p_i \\ln p_i$) to quantify agricultural diversification.
"""),
        ("code", """import os
import sys
sys.path.insert(0, os.path.abspath("../.."))

import pandas as pd
from ml.src.analytics.regional_analysis import (
    get_state_performance_summary,
    compare_states,
    get_top_producing_districts,
    compare_districts,
    calculate_state_crop_diversity
)

print("Regional analysis modules successfully imported.")
"""),
        ("markdown", """## 1. State-Level Performance Summary (Field Crops)
"""),
        ("code", """state_df = get_state_performance_summary(exclude_coconut=True)
print(state_df.head(10)[["state_name", "total_production", "total_area", "aggregate_yield", "crop_diversity_count"]].to_string(index=False))
"""),
        ("markdown", """## 2. Multi-State Comparison: Punjab vs Bihar vs Uttar Pradesh
"""),
        ("code", """comp_df = compare_states(["Punjab", "Bihar", "Uttar Pradesh"])
print(comp_df.to_string(index=False))
"""),
        ("markdown", """## 3. Top Producing Districts by Crop (Composite Pairs)
Prevents cross-state district name collisions (e.g. Aurangabad, Bilaspur).
"""),
        ("code", """wheat_districts = get_top_producing_districts("Wheat", limit=8)
print("=== Top 8 Wheat Producing Districts in India ===")
print(wheat_districts.to_string(index=False))
"""),
        ("markdown", """## 4. Shannon Crop Diversity Index
Quantifies agricultural resilience through crop diversification across states.
"""),
        ("code", """diversity_df = calculate_state_crop_diversity()
print("=== Top 5 Most Diversified States (High Shannon Index) ===")
print(diversity_df.head(5)[["state_name", "shannon_diversity_index", "effective_crops_count", "primary_crop"]].to_string(index=False))

print("\\n=== Top 5 Least Diversified States (Monoculture / Specialized) ===")
print(diversity_df.tail(5)[["state_name", "shannon_diversity_index", "effective_crops_count", "primary_crop"]].to_string(index=False))
""")
    ]
    build_and_save_notebook("03_regional_analysis.ipynb", cells)


# ==========================================
# 4. 04_rainfall_analysis.ipynb
# ==========================================
def create_nb04():
    cells = [
        ("markdown", """# KrishiInsights — Historical Rainfall Analysis (1901–2015)

**Project:** KrishiInsights  
**Data Source:** India Meteorological Department (IMD) 115-Year Historical Rainfall Dataset  
**Database:** Neon Serverless PostgreSQL (`neondb`)  
**Stage:** 4 (Statistical Analysis & Exploratory Data Analysis)

### Objectives
1. Analyze 115-year national precipitation patterns (1901–2015).
2. Calculate the Long Period Average (LPA) baseline and categorize deficit ($< -10\\%$) and excess ($> +10\\%$) years.
3. Compute seasonal rainfall distribution (Southwest Monsoon, Post-Monsoon/Rabi, Pre-Monsoon).
4. Evaluate state meteorological profiles and rank top wettest vs driest regions in India.
"""),
        ("code", """import os
import sys
sys.path.insert(0, os.path.abspath("../.."))

import pandas as pd
from ml.src.analytics.rainfall_analysis import (
    get_national_annual_rainfall_trends,
    get_rainfall_summary_statistics,
    get_state_rainfall_profile,
    get_top_wettest_and_driest_states
)

print("Rainfall analysis modules successfully imported.")
"""),
        ("markdown", """## 1. 115-Year National Rainfall Summary Statistics & LPA Baseline
"""),
        ("code", """summary = get_rainfall_summary_statistics()

print(f"Historical Horizon: {summary['time_horizon']['start_year']}–{summary['time_horizon']['end_year']} ({summary['time_horizon']['total_years']} years)")
print(f"Long Period Average (LPA): {summary['annual_rainfall']['mean_mm']} mm (Std: {summary['annual_rainfall']['std_mm']} mm, CV: {summary['annual_rainfall']['cv_pct']}%)")
print(f"Monsoon Mean: {summary['monsoon_rainfall']['mean_mm']} mm ({summary['monsoon_rainfall']['pct_of_annual']}% of annual)")
print(f"Driest Year: {summary['driest_year']['year']} ({summary['driest_year']['rainfall_mm']} mm, {summary['driest_year']['deviation_pct']}% departure)")
print(f"Wettest Year: {summary['wettest_year']['year']} ({summary['wettest_year']['rainfall_mm']} mm, +{summary['wettest_year']['deviation_pct']}% departure)")
print(f"Drought/Deficit Years (< -10% LPA): {summary['anomaly_counts']['drought_years_count']}")
print(f"Excess/Flood Years (> +10% LPA): {summary['anomaly_counts']['excess_years_count']}")
"""),
        ("markdown", """## 2. Annual Rainfall Anomaly Trends
"""),
        ("code", """rain_trends = get_national_annual_rainfall_trends()
print(rain_trends[["year", "annual_rainfall", "monsoon_rainfall", "lpa_deviation_mm", "lpa_deviation_pct", "rainfall_category"]].tail(15).to_string(index=False))
"""),
        ("markdown", """## 3. Top Wettest and Driest Indian States
"""),
        ("code", """wet_dry = get_top_wettest_and_driest_states()

print("=== Top 5 Wettest States in India (1901–2015) ===")
print(wet_dry["wettest"].head(5)[["state_name", "avg_annual_rainfall", "avg_monsoon_rainfall", "cv_pct"]].to_string(index=False))

print("\\n=== Top 5 Driest States in India (1901–2015) ===")
print(wet_dry["driest"].head(5)[["state_name", "avg_annual_rainfall", "avg_monsoon_rainfall", "cv_pct"]].to_string(index=False))
""")
    ]
    build_and_save_notebook("04_rainfall_analysis.ipynb", cells)


# ==========================================
# 5. 05_rainfall_agriculture_relationship.ipynb
# ==========================================
def create_nb05():
    cells = [
        ("markdown", """# KrishiInsights — Agro-Climatic Correlation & Outlier Analysis

**Project:** KrishiInsights  
**Overlapping Window:** 1997–2015 (19 common harvest years)  
**Database:** Neon Serverless PostgreSQL (`neondb`)  
**Stage:** 4 (Statistical Analysis & Exploratory Data Analysis)

### Objectives
1. Measure paired seasonal statistical relationships (Pearson $r$, Spearman $\\rho$, and $p$-values).
2. Evaluate crop-specific rainfall sensitivities (rainfed vs irrigated crops).
3. Demonstrate state-level sensitivity divergence (Punjab/Haryana irrigation vs Odisha/Bihar rainfed).
4. Perform IQR and Z-score outlier detection and classify agro-climatic extremes vs data anomalies.
5. Emphasize critical agricultural caveats (correlation $\\neq$ causation).
"""),
        ("code", """import os
import sys
sys.path.insert(0, os.path.abspath("../.."))

import pandas as pd
from ml.src.analytics.correlation_analysis import (
    calculate_seasonal_correlations,
    calculate_crop_rainfall_correlations,
    calculate_state_level_rainfall_sensitivity
)
from ml.src.analytics.outlier_analysis import (
    detect_outliers_iqr,
    detect_outliers_zscore,
    analyze_crop_yield_anomalies,
    classify_anomalies_summary
)
from ml.src.database.connection import load_agricultural_data

print("Correlation and outlier modules successfully imported.")
"""),
        ("markdown", """## 1. Paired Seasonal Correlation Analysis (1997–2015)
Aligns Southwest Monsoon with Kharif, Winter rainfall with Rabi, and Pre-monsoon with Summer.
"""),
        ("code", """seasonal_corr_df = calculate_seasonal_correlations()
print("=== Paired Seasonal Correlations ===")
print(seasonal_corr_df.to_string(index=False))
"""),
        ("markdown", """## 2. Crop-Specific Rainfall Correlations
Contrasts rainfed coarse grains and pulses against irrigated wheat and sugarcane.
"""),
        ("code", """crop_corr_df = calculate_crop_rainfall_correlations()
print("=== Crop-Specific Correlation with Annual Rainfall ===")
print(crop_corr_df.to_string(index=False))
"""),
        ("markdown", """## 3. State-Level Sensitivity Contrast: Rice (Kharif)
Contrasts high-irrigation canal states against rainfed eastern/central states.
"""),
        ("code", """state_sens_df = calculate_state_level_rainfall_sensitivity(target_crop="Rice")
print("=== State-Level Rainfall Sensitivity Contrast ===")
print(state_sens_df.to_string(index=False))
"""),
        ("markdown", """## 4. Outlier Analysis and Anomaly Classification
Detects statistical outliers and separates legitimate agro-climatic extremes from data anomalies.
"""),
        ("code", """agri_df = load_agricultural_data()
macro_anomalies = classify_anomalies_summary(agri_df)

print("=== Macro Anomaly Classification Summary ===")
for k, v in macro_anomalies.items():
    print(f"  {k}: {v}")

print("\\n=== Rice Yield Outlier Analysis ===")
rice_anomalies = analyze_crop_yield_anomalies(agri_df, crop_name="Rice")
print(f"Total Rice Records: {rice_anomalies['total_records']:,}")
print(f"IQR Upper Bound: {rice_anomalies['iqr_analysis']['upper_bound']} Tonnes/Ha")
print(f"Outliers Count: {rice_anomalies['iqr_analysis']['outlier_count']} ({rice_anomalies['iqr_analysis']['outlier_percentage']}%)")
"""),
        ("markdown", """## 5. Agricultural Caveats & Methodological Warnings
> **Important Disclaimer:**  
> A statistical correlation between rainfall and crop yield does **not** imply direct causality.  
> Agricultural yield is heavily mediated by:
> 1. Irrigation infrastructure (canals, tube-wells)
> 2. Fertilizer and High-Yielding Variety (HYV) seed application
> 3. Soil health, water retention, and topography
> 4. Farm management practices and state procurement policies
""")
    ]
    build_and_save_notebook("05_rainfall_agriculture_relationship.ipynb", cells)


if __name__ == "__main__":
    print("Building and executing 5 Stage 4 Jupyter Notebooks...")
    create_nb01()
    create_nb02()
    create_nb03()
    create_nb04()
    create_nb05()
    print("All 5 Jupyter Notebooks built and saved successfully!")
