"""
Automated Figure Generation Pipeline for KrishiInsights.

Queries Neon PostgreSQL using analytical modules and saves all
publication-ready PNG figures to ml/reports/figures/.
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath("."))
os.environ["MPLCONFIGDIR"] = os.path.abspath("tmp/matplotlib")

import pandas as pd
from ml.src.database.connection import (
    load_agricultural_data,
    load_rainfall_data,
    load_aligned_agri_rainfall_data
)
from ml.src.analytics.agricultural_eda import (
    get_annual_production_trends,
    get_seasonal_distribution
)
from ml.src.analytics.crop_analysis import (
    get_top_crops_rankings
)
from ml.src.analytics.rainfall_analysis import (
    get_national_annual_rainfall_trends,
    get_top_wettest_and_driest_states
)
from ml.src.analytics.correlation_analysis import (
    calculate_seasonal_correlations,
    calculate_state_level_rainfall_sensitivity
)
from ml.src.visualization.agricultural_charts import (
    plot_production_area_trends,
    plot_national_yield_trend,
    plot_seasonal_distribution,
    plot_top_crops,
    plot_yield_distributions
)
from ml.src.visualization.rainfall_charts import (
    plot_long_term_rainfall_trend,
    plot_lpa_deviations,
    plot_seasonal_rainfall_breakdown,
    plot_wettest_driest_states
)
from ml.src.visualization.comparison_charts import (
    plot_rainfall_yield_scatter,
    plot_paired_correlation_heatmap,
    plot_state_sensitivity_contrast,
    plot_crop_yield_boxplots
)


def generate_all_figures():
    print("--- Starting KrishiInsights Figure Generation Pipeline ---")
    output_dir = "ml/reports/figures"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Agricultural Visualizations
    print("1. Generating Agricultural Charts from Neon...")
    trends_df = get_annual_production_trends(unit_filter="Tonnes/Hectare")
    p1 = plot_production_area_trends(trends_df, f"{output_dir}/agri_trends_production_area.png")
    print(f"   Saved: {p1}")

    p2 = plot_national_yield_trend(trends_df, f"{output_dir}/agri_national_yield_trend.png")
    print(f"   Saved: {p2}")

    seasonal_df = get_seasonal_distribution(exclude_coconut=True)
    p3 = plot_seasonal_distribution(seasonal_df, f"{output_dir}/agri_seasonal_distribution.png")
    print(f"   Saved: {p3}")

    # Top crops rankings
    top_prod = get_top_crops_rankings(metric="production", limit=10)
    top_prod["prod_mt"] = top_prod["total_production"] / 1e6
    p4 = plot_top_crops(
        top_prod,
        "prod_mt",
        "Top 10 Indian Field Crops by Total Production (1997–2015)",
        "Total Production (Million Tonnes)",
        f"{output_dir}/agri_top_crops_production.png",
        color="#2b5c8f"
    )
    print(f"   Saved: {p4}")

    top_area = get_top_crops_rankings(metric="area", limit=10)
    top_area["area_mha"] = top_area["total_area"] / 1e6
    p5 = plot_top_crops(
        top_area,
        "area_mha",
        "Top 10 Indian Field Crops by Cultivated Area (1997–2015)",
        "Cultivated Area (Million Hectares)",
        f"{output_dir}/agri_top_crops_area.png",
        color="#2a9d8f"
    )
    print(f"   Saved: {p5}")

    top_yield = get_top_crops_rankings(metric="yield", limit=10)
    p6 = plot_top_crops(
        top_yield,
        "aggregate_yield",
        "Top 10 Indian Field Crops by Aggregate Yield (Tonnes/Ha)",
        "Aggregate Yield (Tonnes / Hectare)",
        f"{output_dir}/agri_top_crops_yield.png",
        color="#e76f51"
    )
    print(f"   Saved: {p6}")

    # 2. Rainfall Visualizations
    print("2. Generating Rainfall Charts from Neon...")
    rain_trends = get_national_annual_rainfall_trends()
    p7 = plot_long_term_rainfall_trend(rain_trends, f"{output_dir}/rainfall_115yr_trend.png")
    print(f"   Saved: {p7}")

    p8 = plot_lpa_deviations(rain_trends, f"{output_dir}/rainfall_lpa_deviations.png")
    print(f"   Saved: {p8}")

    p9 = plot_seasonal_rainfall_breakdown(rain_trends, f"{output_dir}/rainfall_seasonal_breakdown.png")
    print(f"   Saved: {p9}")

    wet_dry_states = get_top_wettest_and_driest_states()
    p10 = plot_wettest_driest_states(wet_dry_states, f"{output_dir}/rainfall_wettest_driest_states.png")
    print(f"   Saved: {p10}")

    # 3. Correlation & Comparative Visualizations
    print("3. Generating Correlation & Comparison Charts...")
    seasonal_corrs = calculate_seasonal_correlations()
    # Format into a clean 2D DataFrame for heatmap
    rel_col = "relationship" if "relationship" in seasonal_corrs.columns else "analysis_pair"
    heatmap_data = seasonal_corrs.set_index(rel_col)[["pearson_r", "spearman_rho"]].rename(
        columns={"pearson_r": "Pearson r", "spearman_rho": "Spearman rho"}
    )
    p11 = plot_paired_correlation_heatmap(heatmap_data, f"{output_dir}/correlation_paired_heatmap.png")
    print(f"   Saved: {p11}")

    state_sens = calculate_state_level_rainfall_sensitivity()
    key_states = ["Punjab", "Haryana", "Rajasthan", "Bihar", "Odisha", "Maharashtra", "Tamil Nadu", "Gujarat", "Uttar Pradesh", "West Bengal"]
    contrast_sens = state_sens[state_sens["state_name"].isin(key_states)]
    p12 = plot_state_sensitivity_contrast(contrast_sens, f"{output_dir}/correlation_state_sensitivity_contrast.png")
    print(f"   Saved: {p12}")

    # 4. Detailed Dataframe-driven charts (Yield distribution, scatter, boxplot)
    print("4. Fetching detailed observation records for distribution and scatter plots...")
    aligned_df = load_aligned_agri_rainfall_data()
    p13 = plot_rainfall_yield_scatter(
        aligned_df,
        crop_name="Rice",
        rainfall_col="monsoon_rainfall_mm",
        season_name="Kharif",
        save_path=f"{output_dir}/correlation_rice_monsoon_scatter.png"
    )
    print(f"   Saved: {p13}")

    p14 = plot_yield_distributions(aligned_df, crops=["Rice", "Wheat", "Sugarcane", "Maize"],
                                  save_path=f"{output_dir}/agri_yield_distributions.png")
    print(f"   Saved: {p14}")

    p15 = plot_crop_yield_boxplots(aligned_df, crops=["Rice", "Wheat", "Maize", "Cotton(lint)", "Jowar", "Bajra"],
                                  save_path=f"{output_dir}/outliers_crop_yield_boxplots.png")
    print(f"   Saved: {p15}")

    print(f"\n=======================================================")
    print(f" All 15 Stage 4 Figures Successfully Generated! ")
    print(f" Saved to: {os.path.abspath(output_dir)}")
    print(f"=======================================================")


if __name__ == "__main__":
    generate_all_figures()
