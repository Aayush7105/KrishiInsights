"""
KrishiInsights ML Module - Regional Agricultural Analysis
Provides state-wise and district-wise statistical comparisons from Neon.
Strictly preserves composite (state, district) identity to prevent district name collisions.
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from ml.src.database.connection import run_query

def get_state_performance_summary(
    crop_category: Optional[str] = None,
    exclude_coconut: bool = True
) -> pd.DataFrame:
    """
    Computes macro agricultural performance for all 33 states/UTs:
    - Total production (Tonnes)
    - Total cultivated area (Hectares)
    - Aggregate yield (Sum(Prod)/Sum(Area) in Tonnes/Ha)
    - Crop diversity (Number of distinct crops cultivated)
    - Total observations
    """
    cat_clause = "AND c.crop_category = :category" if crop_category else ""
    unit_clause = "AND a.yield_unit = 'Tonnes/Hectare'" if exclude_coconut else ""

    sql = f"""
        SELECT 
            s.state_name,
            ROUND(SUM(a.production)::numeric, 2) as total_production,
            ROUND(SUM(a.area)::numeric, 2) as total_area,
            ROUND((SUM(a.production) / NULLIF(SUM(a.area), 0))::numeric, 4) as aggregate_yield,
            COUNT(DISTINCT a.crop_id) as crop_diversity_count,
            COUNT(DISTINCT a.district_id) as districts_count,
            COUNT(*) as record_count
        FROM agricultural_records a
        JOIN states s ON a.state_id = s.id
        JOIN crops c ON a.crop_id = c.id
        WHERE 1=1 {cat_clause} {unit_clause}
        GROUP BY s.state_name
        ORDER BY total_production DESC;
    """
    params = {}
    if crop_category:
        params["category"] = crop_category
    return run_query(sql, params)

def compare_states(
    state_names: List[str],
    crop_name: Optional[str] = None,
    year_range: Optional[Tuple[int, int]] = (1997, 2015)
) -> pd.DataFrame:
    """
    Compares two or more states over a common time horizon.
    If crop_name is specified, compares that specific crop across the states.
    """
    crop_clause = "AND c.crop_name = :crop_name" if crop_name else "AND a.yield_unit = 'Tonnes/Hectare'"
    sql = f"""
        SELECT 
            s.state_name,
            a.year,
            ROUND(SUM(a.production)::numeric, 2) as production,
            ROUND(SUM(a.area)::numeric, 2) as area,
            ROUND((SUM(a.production) / NULLIF(SUM(a.area), 0))::numeric, 4) as aggregate_yield,
            COUNT(*) as records
        FROM agricultural_records a
        JOIN states s ON a.state_id = s.id
        JOIN crops c ON a.crop_id = c.id
        WHERE s.state_name IN :states
          AND a.year >= :min_yr AND a.year <= :max_yr
          {crop_clause}
        GROUP BY s.state_name, a.year
        ORDER BY a.year ASC, s.state_name ASC;
    """
    params = {
        "states": tuple(state_names),
        "min_yr": year_range[0] if year_range else 1997,
        "max_yr": year_range[1] if year_range else 2015
    }
    if crop_name:
        params["crop_name"] = crop_name
    return run_query(sql, params)

def get_top_producing_districts(
    crop_name: str,
    limit: int = 10
) -> pd.DataFrame:
    """
    Identifies top producing districts for a specific crop across India.
    Crucial: Districts are uniquely represented as (state_name, district_name)
    to prevent name collisions across state borders (e.g., Aurangabad, Bilaspur).
    """
    sql = """
        SELECT 
            s.state_name,
            d.district_name,
            ROUND(SUM(a.production)::numeric, 2) as total_production,
            ROUND(SUM(a.area)::numeric, 2) as total_area,
            ROUND((SUM(a.production) / NULLIF(SUM(a.area), 0))::numeric, 4) as aggregate_yield,
            MAX(a.yield_unit) as yield_unit,
            COUNT(*) as observations,
            MIN(a.year) as first_year,
            MAX(a.year) as last_year
        FROM agricultural_records a
        JOIN states s ON a.state_id = s.id
        JOIN districts d ON a.district_id = d.id
        JOIN crops c ON a.crop_id = c.id
        WHERE c.crop_name = :crop_name
        GROUP BY s.state_name, d.district_name
        ORDER BY total_production DESC
        LIMIT :limit;
    """
    return run_query(sql, {"crop_name": crop_name, "limit": limit})

def compare_districts(
    district_specs: List[Tuple[str, str]],
    crop_name: Optional[str] = None
) -> pd.DataFrame:
    """
    Compares specific districts specified as (state_name, district_name) tuples.
    Example: [('Uttar Pradesh', 'KANPUR NAGAR'), ('West Bengal', 'BURDWAN')]
    """
    # Build conditions
    clauses = []
    params = {}
    for i, (st, dist) in enumerate(district_specs):
        clauses.append(f"(s.state_name = :st_{i} AND d.district_name = :dist_{i})")
        params[f"st_{i}"] = st
        params[f"dist_{i}"] = dist

    where_dist = " OR ".join(clauses)
    crop_clause = "AND c.crop_name = :crop_name" if crop_name else "AND a.yield_unit = 'Tonnes/Hectare'"
    if crop_name:
        params["crop_name"] = crop_name

    sql = f"""
        SELECT 
            s.state_name,
            d.district_name,
            a.year,
            ROUND(SUM(a.production)::numeric, 2) as production,
            ROUND(SUM(a.area)::numeric, 2) as area,
            ROUND((SUM(a.production) / NULLIF(SUM(a.area), 0))::numeric, 4) as aggregate_yield
        FROM agricultural_records a
        JOIN states s ON a.state_id = s.id
        JOIN districts d ON a.district_id = d.id
        JOIN crops c ON a.crop_id = c.id
        WHERE ({where_dist}) {crop_clause}
        GROUP BY s.state_name, d.district_name, a.year
        ORDER BY a.year ASC, s.state_name, d.district_name;
    """
    return run_query(sql, params)

def calculate_state_crop_diversity() -> pd.DataFrame:
    """
    Calculates agricultural crop diversity across Indian states:
    - Richness: Number of distinct crops grown
    - Relative Evenness: Shannon Diversity Index H' = -sum(p_i * ln(p_i))
      where p_i is the proportion of cultivated area allocated to crop i.
    """
    sql = """
        SELECT 
            s.state_name,
            c.crop_name,
            SUM(a.area) as crop_area
        FROM agricultural_records a
        JOIN states s ON a.state_id = s.id
        JOIN crops c ON a.crop_id = c.id
        WHERE a.area > 0
        GROUP BY s.state_name, c.crop_name;
    """
    df = run_query(sql)

    # Compute Shannon index per state in pandas
    results = []
    for state, group in df.groupby("state_name"):
        total_st_area = group["crop_area"].sum()
        p = group["crop_area"] / total_st_area
        shannon_h = -np.sum(p * np.log(p.replace(0, np.nan).dropna()))
        primary_crop = group.loc[group["crop_area"].idxmax()]["crop_name"]
        effective_crops = round(float(np.exp(shannon_h)), 2)
        results.append({
            "state_name": state,
            "crop_richness": len(group),
            "shannon_diversity_index": round(float(shannon_h), 3),
            "effective_crops_count": effective_crops,
            "primary_crop": primary_crop,
            "total_cultivated_area": round(float(total_st_area), 2)
        })

    div_df = pd.DataFrame(results).sort_values(by="shannon_diversity_index", ascending=False).reset_index(drop=True)
    return div_df
