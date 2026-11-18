"""
Independent Rainfall Verification Script for KrishiInsights Stage 4.
Audits meteorological records, source subdivisions, state mappings, and time horizon.
"""

import sys
sys.path.insert(0, ".")
from ml.src.database.connection import run_query

def audit_rainfall():
    print("=== Rainfall Dataset Verification ===")
    
    # 1. Row counts, year range, and nulls
    meta = run_query("""
        SELECT 
            COUNT(*) as total_rainfall_records,
            MIN(year) as min_year,
            MAX(year) as max_year,
            COUNT(DISTINCT state_id) as states_count,
            COUNT(DISTINCT source_id) as source_id_count,
            COUNT(*) FILTER (WHERE annual_rainfall_mm IS NULL) as null_annual,
            COUNT(*) FILTER (WHERE monsoon_rainfall_mm IS NULL) as null_monsoon,
            COUNT(*) FILTER (WHERE rabi_rainfall_mm IS NULL) as null_rabi,
            COUNT(*) FILTER (WHERE pre_monsoon_rainfall_mm IS NULL) as null_pre_monsoon
        FROM rainfall_records;
    """)
    print("Metadata & Invariants:")
    print(meta.to_string(index=False))

    # 2. Duplicate state-year check
    dups = run_query("""
        SELECT state_id, year, COUNT(*)
        FROM rainfall_records
        GROUP BY state_id, year
        HAVING COUNT(*) > 1;
    """)
    print(f"\nDuplicate (state_id, year) observations: {len(dups)}")

    # 3. Source check
    sub_map = run_query("""
        SELECT 
            s.state_name,
            COUNT(DISTINCT r.source_id) as num_sources,
            STRING_AGG(DISTINCT r.source_id, ', ') as sources
        FROM rainfall_records r
        JOIN states s ON r.state_id = s.id
        GROUP BY s.state_name
        ORDER BY num_sources DESC
        LIMIT 5;
    """)
    print("\nState Rainfall Sources (Top 5):")
    print(sub_map.to_string(index=False))

    # 4. Long Period Average (LPA) Recalculation
    lpa_df = run_query("""
        SELECT 
            ROUND(AVG(annual_rainfall_mm)::numeric, 2) as national_lpa_mm,
            ROUND(STDDEV(annual_rainfall_mm)::numeric, 2) as national_std_mm,
            ROUND((STDDEV(annual_rainfall_mm) / AVG(annual_rainfall_mm) * 100)::numeric, 2) as national_cv_pct,
            ROUND(AVG(monsoon_rainfall_mm)::numeric, 2) as monsoon_mean_mm,
            ROUND((AVG(monsoon_rainfall_mm) / AVG(annual_rainfall_mm) * 100)::numeric, 2) as monsoon_share_pct
        FROM rainfall_records;
    """)
    print("\nNational Climatological Baselines:")
    print(lpa_df.to_string(index=False))

    # 5. Check if rainfall is ever presented as district-level
    dist_rain_check = run_query("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'agricultural_records' AND column_name LIKE '%rainfall%';
    """)
    print(f"\nRainfall columns directly in agricultural_records: {dist_rain_check.empty} (Expected: True - no fake district rainfall)")

if __name__ == "__main__":
    audit_rainfall()
