"""
Independent Verification Script for Neon Database Connectivity in Stage 4.
Inspects active connection parameters and queries live row counts from Neon.
"""

import os
import sys
from urllib.parse import urlparse

sys.path.insert(0, ".")
from ml.src.database.connection import get_engine, run_query

def audit_database_connection():
    print("=== Stage 4 Database Connection Verification ===")
    raw_url = os.getenv("DATABASE_URL")
    if not raw_url:
        print("[FAIL] DATABASE_URL is missing!")
        return False

    parsed = urlparse(raw_url)
    hostname = parsed.hostname or ""
    dbname = (parsed.path or "").lstrip("/")

    print(f"Host: {hostname[:12]}...{hostname[-15:] if len(hostname) > 27 else ''}")
    print(f"Database Name: {dbname}")
    print(f"Is Neon Cloud Host: {'neon.tech' in hostname}")
    print(f"Is Localhost: {'localhost' in hostname or '127.0.0.1' in hostname}")

    if "neon.tech" not in hostname:
        print("[FAIL] Database is NOT connected to Neon!")
        return False
    if "localhost" in hostname or "127.0.0.1" in hostname:
        print("[FAIL] Database is pointing to localhost!")
        return False

    # Execute system queries
    engine = get_engine()
    with engine.connect() as conn:
        db_res = run_query("SELECT current_database(), current_user, version();")
        print(f"Connected DB: {db_res.iloc[0]['current_database']}")
        print(f"Connected User: {db_res.iloc[0]['current_user']}")
        print(f"Postgres Version: {db_res.iloc[0]['version'][:60]}...")

        # Record counts
        counts = run_query("""
            SELECT 
                (SELECT COUNT(*) FROM states) as states_count,
                (SELECT COUNT(*) FROM districts) as districts_count,
                (SELECT COUNT(*) FROM crops) as crops_count,
                (SELECT COUNT(*) FROM agricultural_records) as agri_records_count,
                (SELECT COUNT(*) FROM rainfall_records) as rainfall_records_count;
        """)
        print("\n=== Live Row Counts in Neon Database ===")
        for col in counts.columns:
            print(f"  {col}: {counts.iloc[0][col]:,}")

    return True

if __name__ == "__main__":
    audit_database_connection()
