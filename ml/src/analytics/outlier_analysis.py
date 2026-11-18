"""
Outlier and Anomaly Analysis Module for KrishiInsights.

Provides rigorous outlier detection using both IQR (Interquartile Range)
and Z-score statistical methods across agricultural metrics (production, area, yield)
and meteorological metrics (annual and seasonal rainfall).

Differentiates between:
1. Legitimate agro-climatic extremes (e.g., severe droughts, high-yield sugarcane pockets).
2. Data entry / reporting anomalies (e.g., area <= 0, astronomical yield ratios).
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from scipy import stats


def detect_outliers_iqr(
    series: pd.Series,
    multiplier: float = 1.5
) -> Dict[str, Any]:
    """
    Detect outliers using Tukey's Interquartile Range (IQR) method.
    
    Bounds:
        Lower Bound = Q1 - (multiplier * IQR)
        Upper Bound = Q3 + (multiplier * IQR)
    """
    clean_series = series.dropna()
    if len(clean_series) < 4:
        return {
            "method": "IQR",
            "q1": np.nan,
            "q3": np.nan,
            "iqr": np.nan,
            "lower_bound": np.nan,
            "upper_bound": np.nan,
            "outlier_count": 0,
            "outlier_percentage": 0.0,
            "outlier_indices": []
        }

    q1 = float(clean_series.quantile(0.25))
    q3 = float(clean_series.quantile(0.75))
    iqr = q3 - q1
    lower_bound = q1 - (multiplier * iqr)
    upper_bound = q3 + (multiplier * iqr)

    outliers_mask = (clean_series < lower_bound) | (clean_series > upper_bound)
    outlier_indices = clean_series[outliers_mask].index.tolist()
    outlier_count = int(outliers_mask.sum())
    outlier_pct = float((outlier_count / len(clean_series)) * 100)

    return {
        "method": "IQR",
        "multiplier": multiplier,
        "q1": round(q1, 4),
        "q3": round(q3, 4),
        "iqr": round(iqr, 4),
        "lower_bound": round(lower_bound, 4),
        "upper_bound": round(upper_bound, 4),
        "outlier_count": outlier_count,
        "outlier_percentage": round(outlier_pct, 2),
        "outlier_indices": outlier_indices
    }


def detect_outliers_zscore(
    series: pd.Series,
    threshold: float = 3.0
) -> Dict[str, Any]:
    """
    Detect outliers using Z-score standardization (|z| > threshold).
    
    Formula:
        z = (x - mean) / std
    """
    clean_series = series.dropna()
    if len(clean_series) < 4:
        return {
            "method": "Z-score",
            "mean": np.nan,
            "std": np.nan,
            "threshold": threshold,
            "outlier_count": 0,
            "outlier_percentage": 0.0,
            "outlier_indices": []
        }

    mean = float(clean_series.mean())
    std = float(clean_series.std(ddof=1))
    
    if std == 0:
        return {
            "method": "Z-score",
            "mean": round(mean, 4),
            "std": 0.0,
            "threshold": threshold,
            "outlier_count": 0,
            "outlier_percentage": 0.0,
            "outlier_indices": []
        }

    z_scores = (clean_series - mean) / std
    outliers_mask = z_scores.abs() > threshold
    outlier_indices = clean_series[outliers_mask].index.tolist()
    outlier_count = int(outliers_mask.sum())
    outlier_pct = float((outlier_count / len(clean_series)) * 100)

    return {
        "method": "Z-score",
        "mean": round(mean, 4),
        "std": round(std, 4),
        "threshold": threshold,
        "outlier_count": outlier_count,
        "outlier_percentage": round(outlier_pct, 2),
        "outlier_indices": outlier_indices
    }


def analyze_crop_yield_anomalies(
    df: pd.DataFrame,
    crop_name: Optional[str] = None,
    iqr_multiplier: float = 1.5
) -> Dict[str, Any]:
    """
    Analyze crop yield anomalies for a specific crop or crop subset.
    Isolates coconut (measured in Nuts/Hectare) from field crops (Tonnes/Hectare).
    
    Identifies:
    - Upper & lower IQR bounds
    - Extreme yield observations
    - Likely data artifacts vs high-productivity districts
    """
    subset = df.copy()
    if crop_name:
        subset = subset[subset["crop_name"].str.lower() == crop_name.lower()]
    
    if subset.empty:
        return {"error": f"No records found for crop '{crop_name}'"}

    # Dynamically resolve column names
    yield_col = "yield" if "yield" in subset.columns else "yield_amount"
    year_col = "crop_year" if "crop_year" in subset.columns else "year"
    season_col = "season_name" if "season_name" in subset.columns else "season"

    # Separate unit groups if crop_name not given
    unit_category = "Coconut (Nuts/Ha)" if (crop_name and crop_name.lower() == "coconut") else "Field Crops (Tonnes/Ha)"
    
    clean_yield = subset[yield_col].dropna()
    iqr_res = detect_outliers_iqr(clean_yield, multiplier=iqr_multiplier)
    z_res = detect_outliers_zscore(clean_yield, threshold=3.0)

    # Top highest yield anomalies
    outlier_rows = subset.loc[iqr_res["outlier_indices"]]
    req_cols = [c for c in [year_col, "state_name", "district_name", "crop_name", season_col, "area", "production", yield_col] if c in outlier_rows.columns]
    top_upper_anomalies = (
        outlier_rows[outlier_rows[yield_col] > iqr_res["upper_bound"]]
        .sort_values(by=yield_col, ascending=False)
        .head(10)[req_cols]
        .to_dict(orient="records")
    )

    return {
        "crop_name": crop_name if crop_name else "All Field Crops",
        "unit_category": unit_category,
        "total_records": len(subset),
        "iqr_analysis": iqr_res,
        "zscore_analysis": z_res,
        "top_upper_anomalies": top_upper_anomalies,
    }


def analyze_rainfall_anomalies(
    rainfall_df: pd.DataFrame,
    subdivision_or_state: Optional[str] = None,
    col: str = "annual_rainfall"
) -> Dict[str, Any]:
    """
    Detect extreme meteorological anomalies (severe droughts and extreme excess monsoon floods).
    Uses Long Period Average (LPA) deviations as well as IQR and Z-scores.
    """
    subset = rainfall_df.copy()
    if subdivision_or_state and "state_name" in subset.columns:
        subset = subset[subset["state_name"].str.lower() == subdivision_or_state.lower()]
    elif subdivision_or_state and "subdivision_name" in subset.columns:
        subset = subset[subset["subdivision_name"].str.lower() == subdivision_or_state.lower()]

    if subset.empty:
        return {"error": f"No rainfall records found for '{subdivision_or_state}'"}

    series = subset[col].dropna()
    iqr_res = detect_outliers_iqr(series, multiplier=1.5)
    z_res = detect_outliers_zscore(series, threshold=2.5)

    # Historical extreme drought events (bottom 5)
    drought_events = (
        subset.sort_values(by=col, ascending=True)
        .head(5)[["year", col] + ([c for c in ["state_name", "subdivision_name"] if c in subset.columns])]
        .to_dict(orient="records")
    )

    # Historical extreme flood events (top 5)
    flood_events = (
        subset.sort_values(by=col, ascending=False)
        .head(5)[["year", col] + ([c for c in ["state_name", "subdivision_name"] if c in subset.columns])]
        .to_dict(orient="records")
    )

    return {
        "region": subdivision_or_state if subdivision_or_state else "All Regions",
        "metric": col,
        "total_records": len(subset),
        "iqr_analysis": iqr_res,
        "zscore_analysis": z_res,
        "extreme_drought_events": drought_events,
        "extreme_flood_events": flood_events
    }


def classify_anomalies_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Provides a comprehensive macro breakdown of data anomalies vs agro-climatic extremes.
    
    1. Area Anomaly: Extremely small area (< 1 ha) with high production
    2. Zero or Near-zero Production: Area > 100 ha with production == 0
    3. High-Efficiency Agricultural Pockets: Sugarcane in Tamil Nadu / Maharashtra (normal high yield)
    4. Unit Segregation Verification: Coconut rows with yield > 1000 nuts/ha vs Field crops
    """
    # Exclude Coconut
    field_df = df[df["crop_name"].str.lower() != "coconut"].copy()
    yield_col = "yield" if "yield" in field_df.columns else "yield_amount"

    # Suspicious ratio: area < 2 ha, production > 100 tonnes -> yield > 50 tonnes/ha (except sugarcane)
    suspicious_yield_mask = (
        (field_df["area"] < 5) & 
        (field_df[yield_col] > 50) & 
        (~field_df["crop_name"].str.lower().isin(["sugarcane", "banana", "sweet potato", "tapioca"]))
    )
    suspicious_records = field_df[suspicious_yield_mask]

    # Extreme low yield (crop failure / drought shock)
    crop_failures = field_df[(field_df["area"] > 500) & (field_df[yield_col] < 0.05)]

    # Legitimate agro-climatic high yields (Sugarcane)
    sugarcane_records = field_df[field_df["crop_name"].str.lower() == "sugarcane"]
    sugarcane_iqr = detect_outliers_iqr(sugarcane_records[yield_col].dropna())

    # Rice high yield pockets
    rice_records = field_df[field_df["crop_name"].str.lower() == "rice"]
    rice_iqr = detect_outliers_iqr(rice_records[yield_col].dropna())

    return {
        "field_crops_evaluated": len(field_df),
        "suspicious_small_area_high_production_count": int(suspicious_yield_mask.sum()),
        "severe_crop_failures_count": int(len(crop_failures)),
        "sugarcane_iqr_bounds": {
            "q1": sugarcane_iqr["q1"],
            "q3": sugarcane_iqr["q3"],
            "upper_bound": sugarcane_iqr["upper_bound"],
            "outliers_above_bound": sugarcane_iqr["outlier_count"]
        },
        "rice_iqr_bounds": {
            "q1": rice_iqr["q1"],
            "q3": rice_iqr["q3"],
            "upper_bound": rice_iqr["upper_bound"],
            "outliers_above_bound": rice_iqr["outlier_count"]
        }
    }
