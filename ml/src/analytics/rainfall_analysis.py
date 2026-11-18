"""
KrishiInsights ML Module - Rainfall Exploratory Data Analysis
Analyzes historical IMD meteorological precipitation records (1901-2015) from Neon.
Strictly acknowledges meteorological subdivision granularity vs state alignments.
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from ml.src.database.connection import run_query

def get_national_annual_rainfall_trends() -> pd.DataFrame:
    """
    Computes national historical annual and seasonal rainfall trends from 1901 to 2015:
    - Annual mean and median precipitation (mm)
    - Southwest Monsoon (Jun-Sep), Rabi/Winter (Oct-Feb), Pre-monsoon (Mar-May)
    - Year-over-year changes and deviation from long-period average (LPA).
    """
    sql = """
        SELECT 
            year,
            ROUND(AVG(annual_rainfall_mm)::numeric, 2) as annual_rainfall,
            ROUND(AVG(monsoon_rainfall_mm)::numeric, 2) as monsoon_rainfall,
            ROUND(AVG(rabi_rainfall_mm)::numeric, 2) as rabi_rainfall,
            ROUND(AVG(pre_monsoon_rainfall_mm)::numeric, 2) as pre_monsoon_rainfall,
            COUNT(DISTINCT state_id) as reporting_states
        FROM rainfall_records
        GROUP BY year
        ORDER BY year ASC;
    """
    df = run_query(sql)

    # Long Period Average (LPA) over the 115-year historical horizon
    lpa = df["annual_rainfall"].mean()
    df["lpa_deviation_mm"] = df["annual_rainfall"] - lpa
    df["lpa_deviation_pct"] = ((df["annual_rainfall"] - lpa) / lpa) * 100
    df["annual_yoy_pct"] = df["annual_rainfall"].pct_change() * 100

    # Categorize IMD drought (< -10% LPA) and excess (> +10% LPA) years
    conditions = [
        (df["lpa_deviation_pct"] <= -10.0),
        (df["lpa_deviation_pct"] >= 10.0)
    ]
    choices = ["Drought / Deficit", "Excess / Flood"]
    df["rainfall_category"] = np.select(conditions, choices, default="Normal")

    return df

def get_rainfall_summary_statistics() -> Dict[str, Any]:
    """
    Computes macro descriptive statistics for rainfall across 1901-2015.
    """
    trends_df = get_national_annual_rainfall_trends()
    annual = trends_df["annual_rainfall"]
    monsoon = trends_df["monsoon_rainfall"]

    # Historical extreme years
    driest_year = trends_df.loc[annual.idxmin()]
    wettest_year = trends_df.loc[annual.idxmax()]

    stats = {
        "time_period": f"{int(trends_df['year'].min())} - {int(trends_df['year'].max())}",
        "total_years": len(trends_df),
        "mean_annual_rainfall_mm": round(float(annual.mean()), 2),
        "median_annual_rainfall_mm": round(float(annual.median()), 2),
        "std_annual_rainfall_mm": round(float(annual.std()), 2),
        "cv_annual_rainfall_pct": round(float((annual.std() / annual.mean()) * 100), 2),
        "min_annual_rainfall_mm": round(float(annual.min()), 2),
        "min_annual_year": int(driest_year["year"]),
        "max_annual_rainfall_mm": round(float(annual.max()), 2),
        "max_annual_year": int(wettest_year["year"]),
        "iqr_annual_rainfall_mm": round(float(annual.quantile(0.75) - annual.quantile(0.25)), 2),
        "mean_monsoon_share_pct": round(float((monsoon.mean() / annual.mean()) * 100), 2),
        "total_deficit_years": int((trends_df["rainfall_category"] == "Drought / Deficit").sum()),
        "total_excess_years": int((trends_df["rainfall_category"] == "Excess / Flood").sum()),
        # Nested structures for notebook compatibility
        "time_horizon": {
            "start_year": int(trends_df["year"].min()),
            "end_year": int(trends_df["year"].max()),
            "total_years": len(trends_df)
        },
        "annual_rainfall": {
            "mean_mm": round(float(annual.mean()), 2),
            "std_mm": round(float(annual.std()), 2),
            "cv_pct": round(float((annual.std() / annual.mean()) * 100), 2)
        },
        "monsoon_rainfall": {
            "mean_mm": round(float(monsoon.mean()), 2),
            "pct_of_annual": round(float((monsoon.mean() / annual.mean()) * 100), 2)
        },
        "driest_year": {
            "year": int(driest_year["year"]),
            "rainfall_mm": round(float(annual.min()), 2),
            "deviation_pct": round(float(driest_year["lpa_deviation_pct"]), 2)
        },
        "wettest_year": {
            "year": int(wettest_year["year"]),
            "rainfall_mm": round(float(annual.max()), 2),
            "deviation_pct": round(float(wettest_year["lpa_deviation_pct"]), 2)
        },
        "anomaly_counts": {
            "drought_years_count": int((trends_df["rainfall_category"] == "Drought / Deficit").sum()),
            "excess_years_count": int((trends_df["rainfall_category"] == "Excess / Flood").sum())
        }
    }
    return stats

def get_state_rainfall_profile(state_name: str) -> Dict[str, Any]:
    """
    Analyzes historical precipitation profile for a specific state.
    """
    sql = """
        SELECT 
            r.year,
            r.annual_rainfall_mm,
            r.monsoon_rainfall_mm,
            r.rabi_rainfall_mm,
            r.pre_monsoon_rainfall_mm,
            r.source_id
        FROM rainfall_records r
        JOIN states s ON r.state_id = s.id
        WHERE s.state_name = :state_name
        ORDER BY r.year ASC;
    """
    df = run_query(sql, {"state_name": state_name})
    if df.empty:
        raise ValueError(f"No rainfall records found for state '{state_name}'.")

    mean_ann = df["annual_rainfall_mm"].mean()
    std_ann = df["annual_rainfall_mm"].std()

    return {
        "state_name": state_name,
        "source_id": "IMD",
        "mean_annual_mm": round(float(mean_ann), 2),
        "std_annual_mm": round(float(std_ann), 2),
        "cv_pct": round(float((std_ann / mean_ann) * 100), 2) if mean_ann > 0 else 0.0,
        "min_year": int(df.loc[df["annual_rainfall_mm"].idxmin()]["year"]),
        "min_rainfall": float(df["annual_rainfall_mm"].min()),
        "max_year": int(df.loc[df["annual_rainfall_mm"].idxmax()]["year"]),
        "max_rainfall": float(df["annual_rainfall_mm"].max()),
        "history": df
    }

def get_top_wettest_and_driest_states() -> Dict[str, pd.DataFrame]:
    """
    Ranks Indian states by average annual rainfall across 1901-2015.
    """
    sql = """
        SELECT 
            s.state_name,
            ROUND(AVG(r.annual_rainfall_mm)::numeric, 2) as avg_annual_rainfall,
            ROUND(AVG(r.monsoon_rainfall_mm)::numeric, 2) as avg_monsoon_rainfall,
            ROUND(STDDEV(r.annual_rainfall_mm)::numeric, 2) as rainfall_variability_std,
            ROUND((STDDEV(r.annual_rainfall_mm) / NULLIF(AVG(r.annual_rainfall_mm), 0) * 100)::numeric, 2) as cv_pct,
            COUNT(*) as years_recorded
        FROM rainfall_records r
        JOIN states s ON r.state_id = s.id
        GROUP BY s.state_name
        ORDER BY avg_annual_rainfall DESC;
    """
    df = run_query(sql)
    return {
        "wettest": df.head(10).reset_index(drop=True),
        "driest": df.tail(10).sort_values(by="avg_annual_rainfall", ascending=True).reset_index(drop=True)
    }
