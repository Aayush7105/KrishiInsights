"""
Records exact local PostgreSQL 17 database state before migration.
"""

import os
import sys
import json
from dotenv import dotenv_values
from sqlalchemy import create_engine, text

def record_local_state():
    backend_env = dotenv_values("backend/.env")
    url = backend_env.get("DATABASE_URL")
    if not url:
        print("ERROR: DATABASE_URL not found in backend/.env")
        sys.exit(1)

    engine = create_engine(url)
    with engine.connect() as conn:
        pg_ver = conn.execute(text("SELECT version();")).scalar()
        print("[LOCAL DATABASE INFO]")
        print(f"  * Version: {pg_ver}")

        # Table row counts
        tables = ['states', 'districts', 'crops', 'agricultural_records', 'rainfall_records', 'prediction_records', 'alembic_version']
        counts = {}
        for t in tables:
            try:
                cnt = conn.execute(text(f"SELECT COUNT(*) FROM {t};")).scalar()
                counts[t] = cnt
            except Exception as e:
                counts[t] = f"Error: {e}"
        print("\n[TABLE RECORD COUNTS]")
        for t, c in counts.items():
            print(f"  * {t:<22}: {c}")

        # Alembic revision
        alembic_rev = conn.execute(text("SELECT version_num FROM alembic_version;")).scalar()
        print(f"\n[ALEMBIC VERSION]: {alembic_rev}")

        # Constraints & indexes
        indexes = conn.execute(text("""
            SELECT tablename, indexname 
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            ORDER BY tablename, indexname;
        """)).fetchall()
        print(f"\n[INDEXES COUNT]: {len(indexes)}")
        for idx in indexes:
            print(f"  - {idx[0]}.{idx[1]}")

        # Key stats
        agri_stats = conn.execute(text("""
            SELECT 
                MIN(year), MAX(year),
                COUNT(DISTINCT state_id),
                COUNT(DISTINCT district_id),
                COUNT(DISTINCT crop_id),
                COUNT(*) FILTER (WHERE yield_amount IS NULL)
            FROM agricultural_records;
        """)).fetchone()
        assert agri_stats is not None
        print("\n[AGRICULTURAL STATS]")
        print(f"  * Year range: {agri_stats[0]} - {agri_stats[1]}")
        print(f"  * States: {agri_stats[2]}, Districts: {agri_stats[3]}, Crops: {agri_stats[4]}")
        print(f"  * Null yields: {agri_stats[5]}")

        units = conn.execute(text("""
            SELECT yield_unit, production_unit, COUNT(*) 
            FROM agricultural_records 
            GROUP BY yield_unit, production_unit;
        """)).fetchall()
        print("\n[YIELD UNITS]")
        for u in units:
            print(f"  * {u[0]} ({u[1]}): {u[2]}")

if __name__ == "__main__":
    record_local_state()
