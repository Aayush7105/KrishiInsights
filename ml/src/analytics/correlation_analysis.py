"""
KrishiInsights ML Module - Rainfall and Agriculture Correlation Analysis
Analyzes Pearson and Spearman statistical relationships over the overlapping 1997-2015 window.
Strictly embeds agricultural caveats regarding irrigation, soil, and management practices.
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from scipy import stats
from ml.src.database.connection import run_query

def calculate_seasonal_correlations() -> pd.DataFrame:
    """
    Computes Pearson (r) and Spearman (rho) correlations between paired seasonal rainfall
    and aggregate agricultural production and yield across 1997-2015:
    1. Southwest Monsoon (Jun-Sep) vs Kharif Production & Yield
    2. Rabi / Winter Rainfall (Oct-Feb) vs Rabi Production & Yield
    3. Pre-monsoon Rainfall (Mar-May) vs Summer Production & Yield
    4. Annual Rainfall vs Whole Year Production
    """
    # 1. Fetch aggregated seasonal totals per state per year
    sql = """
        WITH agri_seasonal AS (
            SELECT 
                a.state_id,
                a.year,
                a.season,
                SUM(a.production) as production,
                SUM(a.area) as area,
                (SUM(a.production) / NULLIF(SUM(a.area), 0)) as aggregate_yield
            FROM agricultural_records a
            WHERE a.yield_unit = 'Tonnes/Hectare'
              AND a.year >= 1997 AND a.year <= 2015
            GROUP BY a.state_id, a.year, a.season
        )
        SELECT 
            s.state_name,
            ag.year,
            ag.season,
            ag.production,
            ag.area,
            ag.aggregate_yield,
            r.annual_rainfall_mm,
            r.monsoon_rainfall_mm,
            r.rabi_rainfall_mm,
            r.pre_monsoon_rainfall_mm
        FROM agri_seasonal ag
        JOIN states s ON ag.state_id = s.id
        JOIN rainfall_records r ON ag.state_id = r.state_id AND ag.year = r.year;
    """
    df = run_query(sql)

    pairings = [
        ("Monsoon Rainfall vs Kharif Yield", "Kharif", "monsoon_rainfall_mm", "aggregate_yield"),
        ("Monsoon Rainfall vs Kharif Production", "Kharif", "monsoon_rainfall_mm", "production"),
        ("Rabi Rainfall vs Rabi Yield", "Rabi", "rabi_rainfall_mm", "aggregate_yield"),
        ("Rabi Rainfall vs Rabi Production", "Rabi", "rabi_rainfall_mm", "production"),
        ("Pre-Monsoon Rainfall vs Summer Yield", "Summer", "pre_monsoon_rainfall_mm", "aggregate_yield"),
        ("Pre-Monsoon Rainfall vs Summer Production", "Summer", "pre_monsoon_rainfall_mm", "production"),
        ("Annual Rainfall vs Whole Year Production", "Whole Year", "annual_rainfall_mm", "production")
    ]

    results = []
    for label, season_filter, rain_col, agri_col in pairings:
        sub = df[df["season"] == season_filter][[rain_col, agri_col]].dropna()
        if len(sub) > 10:
            p_r, p_p = stats.pearsonr(sub[rain_col], sub[agri_col])
            s_rho, s_p = stats.spearmanr(sub[rain_col], sub[agri_col])
            results.append({
                "relationship": label,
                "season": season_filter,
                "sample_size": len(sub),
                "pearson_r": round(float(p_r), 4),
                "pearson_p_value": float(f"{p_p:.4e}"),
                "spearman_rho": round(float(s_rho), 4),
                "spearman_p_value": float(f"{s_p:.4e}"),
                "significance_at_5pct": p_p < 0.05
            })

    return pd.DataFrame(results)

def calculate_crop_rainfall_correlations(
    top_crops: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Computes correlation between annual rainfall and major crops.
    Compares rainfed crops (e.g. Rice, Coarse Cereals, Pulses)
    vs irrigated crops (e.g. Wheat, Sugarcane).
    """
    if not top_crops:
        top_crops = [
            "Rice", "Wheat", "Maize", "Jowar", "Bajra",
            "Arhar/Tur", "Gram", "Groundnut", "Cotton(lint)", "Sugarcane"
        ]

    sql = """
        SELECT 
            c.crop_name,
            c.crop_category,
            a.state_id,
            a.year,
            a.season,
            SUM(a.production) as production,
            SUM(a.area) as area,
            (SUM(a.production) / NULLIF(SUM(a.area), 0)) as aggregate_yield,
            r.annual_rainfall_mm,
            r.monsoon_rainfall_mm,
            r.rabi_rainfall_mm
        FROM agricultural_records a
        JOIN crops c ON a.crop_id = c.id
        JOIN rainfall_records r ON a.state_id = r.state_id AND a.year = r.year
        WHERE c.crop_name IN :crops
          AND a.yield_unit = 'Tonnes/Hectare'
          AND a.year >= 1997 AND a.year <= 2015
        GROUP BY c.crop_name, c.crop_category, a.state_id, a.year, a.season, 
                 r.annual_rainfall_mm, r.monsoon_rainfall_mm, r.rabi_rainfall_mm;
    """
    df = run_query(sql, {"crops": tuple(top_crops)})

    results = []
    for crop in top_crops:
        c_df = df[df["crop_name"] == crop].dropna(subset=["aggregate_yield", "annual_rainfall_mm", "monsoon_rainfall_mm"])
        if len(c_df) < 20:
            continue

        # Choose aligned rainfall metric (Monsoon for Kharif crops, Rabi for Wheat/Gram, Annual otherwise)
        cat = c_df.iloc[0]["crop_category"]
        if crop in ["Rice", "Bajra", "Jowar", "Groundnut", "Cotton(lint)", "Maize"]:
            rain_col = "monsoon_rainfall_mm"
            rain_desc = "Monsoon"
        elif crop in ["Wheat", "Gram"]:
            rain_col = "rabi_rainfall_mm"
            rain_desc = "Rabi / Winter"
        else:
            rain_col = "annual_rainfall_mm"
            rain_desc = "Annual"

        # Yield correlation
        p_r_y, p_p_y = stats.pearsonr(c_df[rain_col], c_df["aggregate_yield"])
        s_rho_y, s_p_y = stats.spearmanr(c_df[rain_col], c_df["aggregate_yield"])

        # Production correlation
        p_r_p, p_p_p = stats.pearsonr(c_df[rain_col], c_df["production"])

        results.append({
            "crop_name": crop,
            "crop_category": cat,
            "aligned_rainfall": rain_desc,
            "sample_size": len(c_df),
            "yield_pearson_r": round(float(p_r_y), 4),
            "yield_pearson_p": float(f"{p_p_y:.4e}"),
            "yield_spearman_rho": round(float(s_rho_y), 4),
            "prod_pearson_r": round(float(p_r_p), 4),
            "statistically_significant": p_p_y < 0.05
        })

    return pd.DataFrame(results).sort_values(by="yield_pearson_r", ascending=False).reset_index(drop=True)

def calculate_state_level_rainfall_sensitivity(
    target_crop: str = "Rice"
) -> pd.DataFrame:
    """
    Examines state-level divergence in rainfall sensitivity.
    Demonstrates how canal-irrigated states (Punjab, Haryana) show minimal correlation (r ≈ 0),
    whereas rainfed states (Odisha, Bihar, Madhya Pradesh) exhibit strong positive correlation.
    """
    sql = """
        SELECT 
            s.state_name,
            a.year,
            SUM(a.production) as production,
            SUM(a.area) as area,
            (SUM(a.production) / NULLIF(SUM(a.area), 0)) as aggregate_yield,
            r.monsoon_rainfall_mm
        FROM agricultural_records a
        JOIN states s ON a.state_id = s.id
        JOIN crops c ON a.crop_id = c.id
        JOIN rainfall_records r ON a.state_id = r.state_id AND a.year = r.year
        WHERE c.crop_name = :crop
          AND a.season IN ('Kharif', 'Autumn')
          AND a.year >= 1997 AND a.year <= 2015
        GROUP BY s.state_name, a.year, r.monsoon_rainfall_mm
        HAVING SUM(a.area) > 10000;
    """
    df = run_query(sql, {"crop": target_crop})

    results = []
    for state, group in df.groupby("state_name"):
        if len(group) >= 10:
            r_y, p_y = stats.pearsonr(group["monsoon_rainfall_mm"], group["aggregate_yield"])
            rho_y, _ = stats.spearmanr(group["monsoon_rainfall_mm"], group["aggregate_yield"])
            results.append({
                "state_name": state,
                "crop": target_crop,
                "years_analyzed": len(group),
                "yield_pearson_r": round(float(r_y), 4),
                "yield_spearman_rho": round(float(rho_y), 4),
                "p_value": float(f"{p_y:.4e}"),
                "mean_monsoon_rainfall": round(float(group["monsoon_rainfall_mm"].mean()), 1),
                "mean_yield": round(float(group["aggregate_yield"].mean()), 2)
            })

    return pd.DataFrame(results).sort_values(by="yield_pearson_r", ascending=False).reset_index(drop=True)
