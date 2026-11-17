"""
KrishiInsights ML Module - Agricultural Exploratory Data Analysis (EDA)
Calculates comprehensive national and macro-level agricultural statistics from Neon.
Strictly enforces unit isolation (Metric Tonnes vs Number of Nuts).
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from ml.src.database.connection import run_query, load_agricultural_data

def calculate_overall_summary_statistics() -> Dict[str, Any]:
    """
    Computes summary descriptive statistics for agricultural records.
    Separates field crops (Tonnes) from tree crops like Coconut (Nuts).
    """
    sql = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT state_id) as num_states,
            COUNT(DISTINCT district_id) as num_districts,
            COUNT(DISTINCT crop_id) as num_crops,
            COUNT(DISTINCT season) as num_seasons,
            MIN(year) as min_year,
            MAX(year) as max_year
        FROM agricultural_records;
    """
    meta_df = run_query(sql)
    meta = meta_df.iloc[0].to_dict()

    # Field crops statistics (Tonnes / Hectares)
    field_sql = """
        SELECT 
            'Field Crops (Tonnes)' as crop_group,
            COUNT(*) as count,
            ROUND(AVG(area)::numeric, 2) as mean_area,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY area)::numeric, 2) as median_area,
            ROUND(STDDEV(area)::numeric, 2) as std_area,
            ROUND(MIN(area)::numeric, 2) as min_area,
            ROUND(MAX(area)::numeric, 2) as max_area,
            ROUND((PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY area) - PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY area))::numeric, 2) as iqr_area,
            ROUND(AVG(production)::numeric, 2) as mean_production,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY production)::numeric, 2) as median_production,
            ROUND(STDDEV(production)::numeric, 2) as std_production,
            ROUND(MIN(production)::numeric, 2) as min_production,
            ROUND(MAX(production)::numeric, 2) as max_production,
            ROUND((PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY production) - PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY production))::numeric, 2) as iqr_production,
            ROUND(AVG(yield_amount)::numeric, 4) as mean_yield,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY yield_amount)::numeric, 4) as median_yield,
            ROUND(STDDEV(yield_amount)::numeric, 4) as std_yield,
            ROUND(MIN(yield_amount)::numeric, 4) as min_yield,
            ROUND(MAX(yield_amount)::numeric, 4) as max_yield,
            ROUND((PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY yield_amount) - PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY yield_amount))::numeric, 4) as iqr_yield
        FROM agricultural_records
        WHERE yield_unit = 'Tonnes/Hectare';
    """
    field_df = run_query(field_sql)

    # Coconut statistics (Number of Nuts / Hectare)
    coconut_sql = """
        SELECT 
            'Coconut (Number of Nuts)' as crop_group,
            COUNT(*) as count,
            ROUND(AVG(area)::numeric, 2) as mean_area,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY area)::numeric, 2) as median_area,
            ROUND(STDDEV(area)::numeric, 2) as std_area,
            ROUND(MIN(area)::numeric, 2) as min_area,
            ROUND(MAX(area)::numeric, 2) as max_area,
            ROUND((PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY area) - PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY area))::numeric, 2) as iqr_area,
            ROUND(AVG(production)::numeric, 2) as mean_production,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY production)::numeric, 2) as median_production,
            ROUND(STDDEV(production)::numeric, 2) as std_production,
            ROUND(MIN(production)::numeric, 2) as min_production,
            ROUND(MAX(production)::numeric, 2) as max_production,
            ROUND((PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY production) - PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY production))::numeric, 2) as iqr_production,
            ROUND(AVG(yield_amount)::numeric, 2) as mean_yield,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY yield_amount)::numeric, 2) as median_yield,
            ROUND(STDDEV(yield_amount)::numeric, 2) as std_yield,
            ROUND(MIN(yield_amount)::numeric, 2) as min_yield,
            ROUND(MAX(yield_amount)::numeric, 2) as max_yield,
            ROUND((PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY yield_amount) - PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY yield_amount))::numeric, 2) as iqr_yield
        FROM agricultural_records
        WHERE yield_unit = 'Nuts/Hectare';
    """
    coconut_df = run_query(coconut_sql)

    return {
        "metadata": meta,
        "field_crops": field_df.iloc[0].to_dict(),
        "coconut": coconut_df.iloc[0].to_dict()
    }

def get_annual_production_trends(unit_filter: str = "Tonnes/Hectare") -> pd.DataFrame:
    """
    Calculates annual total production, total cultivated area, and mathematically
    sound aggregate yield (Sum(Production) / Sum(Area)) from 1997 to 2015.
    Also computes year-over-year (YoY) percentage changes.
    """
    sql = """
        SELECT 
            year,
            ROUND(SUM(production)::numeric, 2) as total_production,
            ROUND(SUM(area)::numeric, 2) as total_area,
            ROUND((SUM(production) / NULLIF(SUM(area), 0))::numeric, 4) as aggregate_yield,
            COUNT(*) as record_count
        FROM agricultural_records
        WHERE yield_unit = :unit
        GROUP BY year
        ORDER BY year ASC;
    """
    df = run_query(sql, {"unit": unit_filter})
    
    # Calculate Year-over-Year (YoY) percentage changes
    df["production_yoy_pct"] = df["total_production"].pct_change() * 100
    df["area_yoy_pct"] = df["total_area"].pct_change() * 100
    df["yield_yoy_pct"] = df["aggregate_yield"].pct_change() * 100

    # Long-term change (relative to base year 1997)
    base_prod = df.iloc[0]["total_production"]
    base_area = df.iloc[0]["total_area"]
    base_yield = df.iloc[0]["aggregate_yield"]
    df["production_index_1997"] = (df["total_production"] / base_prod) * 100
    df["area_index_1997"] = (df["total_area"] / base_area) * 100
    df["yield_index_1997"] = (df["aggregate_yield"] / base_yield) * 100

    return df

def get_seasonal_distribution(exclude_coconut: bool = True) -> pd.DataFrame:
    """
    Compares agricultural performance across Kharif, Rabi, Summer, Autumn, Winter, and Whole Year.
    Whole Year records are cataloged as separate non-seasonal administrative submissions.
    """
    unit_clause = "AND yield_unit = 'Tonnes/Hectare'" if exclude_coconut else ""
    sql = f"""
        SELECT 
            season,
            COUNT(*) as record_count,
            ROUND(SUM(production)::numeric, 2) as total_production,
            ROUND(SUM(area)::numeric, 2) as total_area,
            ROUND((SUM(production) / NULLIF(SUM(area), 0))::numeric, 4) as aggregate_yield,
            COUNT(DISTINCT crop_id) as distinct_crops,
            COUNT(DISTINCT state_id) as distinct_states
        FROM agricultural_records
        WHERE 1=1 {unit_clause}
        GROUP BY season
        ORDER BY total_production DESC;
    """
    df = run_query(sql)
    total_prod = df["total_production"].sum()
    total_area = df["total_area"].sum()
    df["production_share_pct"] = (df["total_production"] / total_prod) * 100
    df["area_share_pct"] = (df["total_area"] / total_area) * 100
    return df

def get_yearly_record_distribution() -> pd.DataFrame:
    """Returns number of observations recorded per harvest year."""
    sql = """
        SELECT 
            year,
            COUNT(*) as record_count,
            COUNT(DISTINCT state_id) as states_reporting,
            COUNT(DISTINCT district_id) as districts_reporting,
            COUNT(DISTINCT crop_id) as crops_reported
        FROM agricultural_records
        GROUP BY year
        ORDER BY year ASC;
    """
    return run_query(sql)
