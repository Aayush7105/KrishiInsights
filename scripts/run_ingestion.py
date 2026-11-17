"""
KrishiInsights - Data Ingestion Runner
Provides CLI commands for test ingestion, full ingestion, and verification.
"""

import os
import sys
import argparse
import time
from sqlalchemy import text

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.database.session import SessionLocal
from app.services.ingestion_service import IngestionPipeline

CROP_DATA_PATH = os.path.join("datasets", "processed", "clean_crop_data.csv")
RAIN_DATA_PATH = os.path.join("datasets", "raw", "rainfall.csv")

def run_test_ingestion():
    print("\n==========================================")
    print("STEP 1: RUNNING TEST INGESTION (1,000 ROWS)")
    print("==========================================")
    db = SessionLocal()
    try:
        pipeline = IngestionPipeline(db)
        pipeline.populate_lookup_tables(CROP_DATA_PATH)
        pipeline.ingest_rainfall(RAIN_DATA_PATH)
        pipeline.ingest_agricultural_records(CROP_DATA_PATH, batch_size=500, max_rows=1000)

        # Verification of test rows
        agri_count = db.execute(text("SELECT COUNT(*) FROM agricultural_records;")).scalar()
        rain_count = db.execute(text("SELECT COUNT(*) FROM rainfall_records;")).scalar()
        state_count = db.execute(text("SELECT COUNT(*) FROM states;")).scalar()
        dist_count = db.execute(text("SELECT COUNT(*) FROM districts;")).scalar()
        crop_count = db.execute(text("SELECT COUNT(*) FROM crops;")).scalar()

        print("\n[TEST INGESTION VERIFICATION]")
        print(f"  * States: {state_count}")
        print(f"  * Districts: {dist_count}")
        print(f"  * Crops: {crop_count}")
        print(f"  * Rainfall Records: {rain_count}")
        print(f"  * Agricultural Records: {agri_count}")

        # Verify sample joined record
        sample = db.execute(text("""
            SELECT s.state_name, d.district_name, c.crop_name, c.crop_category, 
                   a.season, a.year, a.area, a.production, a.yield_amount, a.yield_unit
            FROM agricultural_records a
            JOIN states s ON a.state_id = s.id
            JOIN districts d ON a.district_id = d.id
            JOIN crops c ON a.crop_id = c.id
            LIMIT 3;
        """)).fetchall()
        print("\n[SAMPLE JOINED RECORDS]")
        for r in sample:
            print(f"  - {r[0]} | {r[1]} | {r[2]} ({r[3]}) | {r[4]} {r[5]} | Yield: {r[8]} {r[9]}")

        # Test duplicate prevention (re-running same 1,000 rows should insert 0 new rows)
        print("\n[TESTING IDEMPOTENT DUPLICATE PREVENTION]")
        initial_count = agri_count
        pipeline.ingest_agricultural_records(CROP_DATA_PATH, batch_size=500, max_rows=1000)
        retest_count = db.execute(text("SELECT COUNT(*) FROM agricultural_records;")).scalar()
        print(f"  * Before re-run: {initial_count}")
        print(f"  * After re-run:  {retest_count}")
        assert initial_count == retest_count, "Duplicate records were incorrectly inserted!"
        print("  * Result: Idempotency VERIFIED (0 duplicate rows created).")

        print("\nTest ingestion successfully passed all verification gates!")
    finally:
        db.close()

def run_full_ingestion():
    print("\n==========================================")
    print("STEP 2: RUNNING FULL DATASET INGESTION")
    print("==========================================")
    db = SessionLocal()
    try:
        pipeline = IngestionPipeline(db)
        t0 = time.time()
        pipeline.run_full_pipeline(CROP_DATA_PATH, RAIN_DATA_PATH)
        elapsed = time.time() - t0
        print(f"\n[FULL INGESTION COMPLETED IN {elapsed:.1f}s]")
    finally:
        db.close()

def run_verification():
    print("\n==========================================")
    print("STEP 3: RUNNING FULL SQL VERIFICATION AUDIT")
    print("==========================================")
    db = SessionLocal()
    try:
        # 1. Row counts
        print("\n--- 1. POSTGRESQL TABLE RECORD COUNTS ---")
        for tbl in ['states', 'districts', 'crops', 'agricultural_records', 'rainfall_records', 'prediction_records']:
            cnt = db.execute(text(f"SELECT COUNT(*) FROM {tbl};")).scalar()
            print(f"  {tbl:<22}: {cnt:,} rows")

        # 2. Agricultural summary
        print("\n--- 2. AGRICULTURAL DATA CHECKS ---")
        agri_stats = db.execute(text("""
            SELECT 
                MIN(year) as min_yr, MAX(year) as max_yr,
                COUNT(DISTINCT state_id) as num_states,
                COUNT(DISTINCT district_id) as num_districts,
                COUNT(DISTINCT crop_id) as num_crops,
                COUNT(DISTINCT season) as num_seasons,
                COUNT(*) FILTER (WHERE yield_amount IS NULL) as null_yields,
                COUNT(*) FILTER (WHERE area <= 0) as non_pos_areas,
                COUNT(*) FILTER (WHERE production < 0) as neg_prods
            FROM agricultural_records;
        """)).fetchone()
        print(f"  Year Range           : {agri_stats[0]} - {agri_stats[1]}")
        print(f"  Distinct States      : {agri_stats[2]}")
        print(f"  Distinct Districts   : {agri_stats[3]}")
        print(f"  Distinct Crops       : {agri_stats[4]}")
        print(f"  Distinct Seasons     : {agri_stats[5]}")
        print(f"  Null Yield Records   : {agri_stats[6]}")
        print(f"  Area <= 0 Records    : {agri_stats[7]}")
        print(f"  Production < 0 Records: {agri_stats[8]}")

        # 3. Unit distribution
        print("\n--- 3. YIELD UNIT DISTRIBUTION ---")
        units = db.execute(text("""
            SELECT yield_unit, production_unit, COUNT(*) 
            FROM agricultural_records 
            GROUP BY yield_unit, production_unit;
        """)).fetchall()
        for u in units:
            print(f"  Yield: {u[0]:<15} | Production: {u[1]:<15} | Count: {u[2]:,}")

        # 4. Top crops
        print("\n--- 4. TOP 5 CROPS BY RECORD COUNT ---")
        top_crops = db.execute(text("""
            SELECT c.crop_name, c.crop_category, COUNT(*) as cnt,
                   ROUND(AVG(a.yield_amount)::numeric, 2) as avg_yield
            FROM agricultural_records a
            JOIN crops c ON a.crop_id = c.id
            GROUP BY c.crop_name, c.crop_category
            ORDER BY cnt DESC
            LIMIT 5;
        """)).fetchall()
        for tc in top_crops:
            print(f"  {tc[0]:<16} ({tc[1]:<12}): {tc[2]:,d} records | Avg Yield: {tc[3]}")

        # 5. Rainfall summary
        print("\n--- 5. RAINFALL DATA CHECKS ---")
        rain_stats = db.execute(text("""
            SELECT 
                MIN(year), MAX(year), COUNT(DISTINCT state_id), COUNT(*),
                ROUND(AVG(annual_rainfall_mm)::numeric, 2),
                ROUND(AVG(monsoon_rainfall_mm)::numeric, 2)
            FROM rainfall_records;
        """)).fetchone()
        print(f"  Year Range           : {rain_stats[0]} - {rain_stats[1]}")
        print(f"  Distinct States      : {rain_stats[2]}")
        print(f"  Total Rainfall Rows  : {rain_stats[3]:,}")
        print(f"  Avg Annual Rainfall  : {rain_stats[4]} mm")
        print(f"  Avg Monsoon Rainfall : {rain_stats[5]} mm")

        # 6. Referential integrity check
        print("\n--- 6. REFERENTIAL INTEGRITY AUDIT ---")
        orphan_agri_state = db.execute(text("SELECT COUNT(*) FROM agricultural_records a LEFT JOIN states s ON a.state_id = s.id WHERE s.id IS NULL;")).scalar()
        orphan_agri_dist = db.execute(text("SELECT COUNT(*) FROM agricultural_records a LEFT JOIN districts d ON a.district_id = d.id WHERE d.id IS NULL;")).scalar()
        orphan_agri_crop = db.execute(text("SELECT COUNT(*) FROM agricultural_records a LEFT JOIN crops c ON a.crop_id = c.id WHERE c.id IS NULL;")).scalar()
        orphan_dist_state = db.execute(text("SELECT COUNT(*) FROM districts d LEFT JOIN states s ON d.state_id = s.id WHERE s.id IS NULL;")).scalar()
        orphan_rain_state = db.execute(text("SELECT COUNT(*) FROM rainfall_records r LEFT JOIN states s ON r.state_id = s.id WHERE s.id IS NULL;")).scalar()

        print(f"  Orphan Agri->State   : {orphan_agri_state}")
        print(f"  Orphan Agri->District: {orphan_agri_dist}")
        print(f"  Orphan Agri->Crop    : {orphan_agri_crop}")
        print(f"  Orphan Dist->State   : {orphan_dist_state}")
        print(f"  Orphan Rain->State   : {orphan_rain_state}")
        assert orphan_agri_state == 0 and orphan_agri_dist == 0 and orphan_agri_crop == 0, "Referential integrity failure!"
        print("  Referential Integrity Status: 100% CLEAN (0 orphan records).")

    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KrishiInsights Database Ingestion Runner")
    parser.add_argument("--test", action="store_true", help="Run 1,000-row test ingestion and idempotency check")
    parser.add_argument("--full", action="store_true", help="Run full 242k record dataset ingestion")
    parser.add_argument("--verify", action="store_true", help="Run SQL verification audit on database")
    args = parser.parse_args()

    if args.test:
        run_test_ingestion()
    elif args.full:
        run_full_ingestion()
    elif args.verify:
        run_verification()
    else:
        parser.print_help()
