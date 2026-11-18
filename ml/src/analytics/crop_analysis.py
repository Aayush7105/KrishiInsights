"""
KrishiInsights ML Module - Crop-Wise Statistical Analysis & Rankings
Provides comprehensive single-crop and multi-crop comparative analytics from Neon.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from ml.src.database.connection import run_query

def get_crop_historical_profile(crop_name: str) -> Dict[str, Any]:
    """
    Computes deep statistical profile for a single crop over 1997-2015:
    - Annual production, area, and aggregate yield
    - Max and min production years
    - Production variability (Coefficient of Variation)
    - Top producing states and districts
    - Seasonal production split
    """
    # 1. Annual trend
    trend_sql = """
        SELECT 
            year,
            ROUND(SUM(production)::numeric, 2) as production,
            ROUND(SUM(area)::numeric, 2) as area,
            ROUND((SUM(production) / NULLIF(SUM(area), 0))::numeric, 4) as aggregate_yield,
            COUNT(*) as record_count,
            MAX(production_unit) as production_unit,
            MAX(yield_unit) as yield_unit
        FROM agricultural_records a
        JOIN crops c ON a.crop_id = c.id
        WHERE c.crop_name = :crop_name
        GROUP BY year
        ORDER BY year ASC;
    """
    trend_df = run_query(trend_sql, {"crop_name": crop_name})
    if trend_df.empty:
        raise ValueError(f"Crop '{crop_name}' not found in database.")

    # 2. Key extremes & variability
    max_row = trend_df.loc[trend_df["production"].idxmax()]
    min_row = trend_df.loc[trend_df["production"].idxmin()]
    mean_prod = trend_df["production"].mean()
    std_prod = trend_df["production"].std()
    cv_prod = (std_prod / mean_prod * 100) if mean_prod > 0 else 0.0

    # 3. Top producing states
    state_sql = """
        SELECT 
            s.state_name,
            ROUND(SUM(a.production)::numeric, 2) as total_production,
            ROUND(SUM(a.area)::numeric, 2) as total_area,
            ROUND((SUM(a.production) / NULLIF(SUM(a.area), 0))::numeric, 4) as aggregate_yield,
            ROUND((SUM(a.production) * 100.0 / (SELECT SUM(a2.production) FROM agricultural_records a2 JOIN crops c2 ON a2.crop_id = c2.id WHERE c2.crop_name = :crop_name))::numeric, 2) as national_share_pct
        FROM agricultural_records a
        JOIN crops c ON a.crop_id = c.id
        JOIN states s ON a.state_id = s.id
        WHERE c.crop_name = :crop_name
        GROUP BY s.state_name
        ORDER BY total_production DESC
        LIMIT 5;
    """
    top_states_df = run_query(state_sql, {"crop_name": crop_name})

    # 4. Top producing districts (composite state + district)
    dist_sql = """
        SELECT 
            s.state_name,
            d.district_name,
            ROUND(SUM(a.production)::numeric, 2) as total_production,
            ROUND(SUM(a.area)::numeric, 2) as total_area,
            ROUND((SUM(a.production) / NULLIF(SUM(a.area), 0))::numeric, 4) as aggregate_yield
        FROM agricultural_records a
        JOIN crops c ON a.crop_id = c.id
        JOIN states s ON a.state_id = s.id
        JOIN districts d ON a.district_id = d.id
        WHERE c.crop_name = :crop_name
        GROUP BY s.state_name, d.district_name
        ORDER BY total_production DESC
        LIMIT 5;
    """
    top_districts_df = run_query(dist_sql, {"crop_name": crop_name})

    # 5. Seasonal split
    season_sql = """
        SELECT 
            a.season,
            ROUND(SUM(a.production)::numeric, 2) as total_production,
            ROUND(SUM(a.area)::numeric, 2) as total_area,
            ROUND((SUM(a.production) / NULLIF(SUM(a.area), 0))::numeric, 4) as aggregate_yield,
            COUNT(*) as record_count
        FROM agricultural_records a
        JOIN crops c ON a.crop_id = c.id
        WHERE c.crop_name = :crop_name
        GROUP BY a.season
        ORDER BY total_production DESC;
    """
    seasonal_df = run_query(season_sql, {"crop_name": crop_name})

    return {
        "crop_name": crop_name,
        "production_unit": trend_df.iloc[0]["production_unit"],
        "yield_unit": trend_df.iloc[0]["yield_unit"],
        "annual_trend": trend_df,
        "max_production_year": int(max_row["year"]),
        "max_production": float(max_row["production"]),
        "min_production_year": int(min_row["year"]),
        "min_production": float(min_row["production"]),
        "mean_annual_production": round(float(mean_prod), 2),
        "production_cv_pct": round(float(cv_prod), 2),
        "top_states": top_states_df,
        "top_districts": top_districts_df,
        "seasonal_breakdown": seasonal_df
    }

def get_top_crops_rankings(
    metric: str = "production",
    limit: int = 10,
    min_observations: int = 100
) -> pd.DataFrame:
    """
    Generates standardized rankings across 124 crops.
    Strictly isolates units: field crops (Tonnes) are ranked independently of Coconut (Nuts).
    Supported metrics:
    - 'production': Total cumulative volume (Tonnes)
    - 'area': Total cumulative cultivated area (Hectares)
    - 'yield': Aggregate efficiency (Sum(Prod)/Sum(Area) in Tonnes/Ha)
    """
    valid_metrics = ["production", "area", "yield"]
    if metric not in valid_metrics:
        raise ValueError(f"Invalid metric '{metric}'. Choose from {valid_metrics}")

    if metric == "production":
        sql = """
            SELECT 
                c.crop_name,
                c.crop_category,
                a.production_unit,
                ROUND(SUM(a.production)::numeric, 2) as total_production,
                ROUND(SUM(a.area)::numeric, 2) as total_area,
                ROUND((SUM(a.production) / NULLIF(SUM(a.area), 0))::numeric, 4) as aggregate_yield,
                COUNT(*) as observations
            FROM agricultural_records a
            JOIN crops c ON a.crop_id = c.id
            WHERE a.yield_unit = 'Tonnes/Hectare'
            GROUP BY c.crop_name, c.crop_category, a.production_unit
            HAVING COUNT(*) >= :min_obs
            ORDER BY total_production DESC
            LIMIT :limit;
        """
    elif metric == "area":
        sql = """
            SELECT 
                c.crop_name,
                c.crop_category,
                ROUND(SUM(a.area)::numeric, 2) as total_area,
                ROUND(SUM(a.production)::numeric, 2) as total_production,
                ROUND((SUM(a.production) / NULLIF(SUM(a.area), 0))::numeric, 4) as aggregate_yield,
                a.yield_unit,
                COUNT(*) as observations
            FROM agricultural_records a
            JOIN crops c ON a.crop_id = c.id
            WHERE a.yield_unit = 'Tonnes/Hectare'
            GROUP BY c.crop_name, c.crop_category, a.yield_unit
            HAVING COUNT(*) >= :min_obs
            ORDER BY total_area DESC
            LIMIT :limit;
        """
    else:  # yield
        sql = """
            SELECT 
                c.crop_name,
                c.crop_category,
                ROUND((SUM(a.production) / NULLIF(SUM(a.area), 0))::numeric, 4) as aggregate_yield,
                a.yield_unit,
                ROUND(SUM(a.production)::numeric, 2) as total_production,
                ROUND(SUM(a.area)::numeric, 2) as total_area,
                COUNT(*) as observations
            FROM agricultural_records a
            JOIN crops c ON a.crop_id = c.id
            WHERE a.yield_unit = 'Tonnes/Hectare'
            GROUP BY c.crop_name, c.crop_category, a.yield_unit
            HAVING COUNT(*) >= :min_obs
            ORDER BY aggregate_yield DESC
            LIMIT :limit;
        """
    return run_query(sql, {"min_obs": min_observations, "limit": limit})

def get_crop_growth_and_decline_rankings(
    base_window: tuple = (1997, 1999),
    recent_window: tuple = (2013, 2015),
    min_observations: int = 50,
    limit: int = 10
) -> Dict[str, pd.DataFrame]:
    """
    Computes percentage change between early historical baseline (1997-1999)
    and recent period (2013-2015) using 3-year smoothed windows to avoid single-year anomalies.
    Returns:
    - 'growth' / 'fastest_growing': Top crops with highest production expansion
    - 'decline' / 'declining': Top crops with highest production contraction
    """
    sql = """
        WITH base_period AS (
            SELECT 
                c.crop_name,
                c.crop_category,
                AVG(a.production) as base_avg_prod,
                COUNT(*) as base_obs
            FROM agricultural_records a
            JOIN crops c ON a.crop_id = c.id
            WHERE a.year >= :base_start AND a.year <= :base_end
              AND a.yield_unit = 'Tonnes/Hectare'
            GROUP BY c.crop_name, c.crop_category
            HAVING COUNT(*) >= :min_obs
        ),
        recent_period AS (
            SELECT 
                c.crop_name,
                AVG(a.production) as recent_avg_prod,
                COUNT(*) as recent_obs
            FROM agricultural_records a
            JOIN crops c ON a.crop_id = c.id
            WHERE a.year >= :rec_start AND a.year <= :rec_end
              AND a.yield_unit = 'Tonnes/Hectare'
            GROUP BY c.crop_name
            HAVING COUNT(*) >= :min_obs
        )
        SELECT 
            b.crop_name,
            b.crop_category,
            ROUND(b.base_avg_prod::numeric, 2) as baseline_production,
            ROUND(r.recent_avg_prod::numeric, 2) as recent_production,
            ROUND(((r.recent_avg_prod - b.base_avg_prod) / NULLIF(b.base_avg_prod, 0) * 100)::numeric, 2) as pct_change,
            b.base_obs + r.recent_obs as total_observations
        FROM base_period b
        JOIN recent_period r ON b.crop_name = r.crop_name
        WHERE b.base_avg_prod > 100;  -- Filter out minor experimental crops
    """
    params = {
        "base_start": base_window[0],
        "base_end": base_window[1],
        "rec_start": recent_window[0],
        "rec_end": recent_window[1],
        "min_obs": min_observations
    }
    df = run_query(sql, params)
    growth_df = df.sort_values(by="pct_change", ascending=False).head(limit).reset_index(drop=True)
    decline_df = df.sort_values(by="pct_change", ascending=True).head(limit).reset_index(drop=True)
    return {
        "growth": growth_df,
        "decline": decline_df,
        "fastest_growing": growth_df,
        "declining": decline_df
    }
