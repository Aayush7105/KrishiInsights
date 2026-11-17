"""
KrishiInsights - Neon Database Migration & Restore Script
Restores custom-format PostgreSQL backup into Neon neondb using pg_restore.
Uses the unpooled (direct) connection string for administrative efficiency.
"""

import os
import sys
import glob
import subprocess
import urllib.parse
from dotenv import dotenv_values
from sqlalchemy import create_engine, text

def restore_to_neon(backup_file=None):
    if not backup_file:
        backups = sorted(glob.glob("database/backups/krishiinsights_db_backup_*.dump"))
        if not backups:
            print("ERROR: No backup files found in database/backups/")
            sys.exit(1)
        backup_file = backups[-1]

    print(f"[MIGRATION INITIATION]")
    print(f"  * Backup Source : {backup_file}")

    # 1. Parse Neon unpooled connection credentials from .env.local
    envs = dotenv_values(".env.local")
    neon_url = envs.get("DATABASE_URL_UNPOOLED") or envs.get("DATABASE_URL")
    if not neon_url:
        print("ERROR: DATABASE_URL_UNPOOLED not found in .env.local")
        sys.exit(1)

    parsed = urllib.parse.urlparse(neon_url)
    username = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = str(parsed.port or 5432)
    dbname = parsed.path.lstrip("/")

    print(f"  * Target DB     : {dbname}")
    print(f"  * Target Host   : {host}")
    print(f"  * Target User   : {username}")

    # 2. Inspect destination schema - MUST BE EMPTY
    db_alchemy_url = neon_url.replace("postgresql://", "postgresql+psycopg2://", 1) if neon_url.startswith("postgresql://") else neon_url
    engine = create_engine(db_alchemy_url, pool_pre_ping=True)
    with engine.connect() as conn:
        tables = conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"
        )).fetchall()
        if len(tables) > 0:
            print(f"ERROR: Destination schema 'public' is not empty! Found tables: {[t[0] for t in tables]}")
            print("Aborting restore per safety rules to prevent overwriting existing objects.")
            sys.exit(1)
        print("  * Destination Pre-check: VERIFIED EMPTY (0 tables in public schema).")

    # 3. Locate pg_restore
    pg_restore_bin = r"C:\Program Files\PostgreSQL\17\bin\pg_restore.exe"
    if not os.path.exists(pg_restore_bin):
        print(f"ERROR: pg_restore not found at {pg_restore_bin}")
        sys.exit(1)

    # 4. Construct pg_restore command
    cmd = [
        pg_restore_bin,
        "-h", host,
        "-p", port,
        "-U", username,
        "-d", dbname,
        "--no-owner",
        "--no-privileges",
        "-v",
        backup_file
    ]

    env = os.environ.copy()
    if password:
        env["PGPASSWORD"] = password
    env["PGSSLMODE"] = "require"

    print("\n[EXECUTING PG_RESTORE INTO NEON]...")
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)

    # pg_restore exit code: 0 is success, 1 is warning, 2 is fatal error
    if res.returncode > 1:
        print(f"ERROR: pg_restore encountered fatal error (returncode {res.returncode}):")
        print(res.stderr)
        sys.exit(1)

    print(f"[PG_RESTORE COMPLETED] Return code: {res.returncode}")
    if res.stderr:
        # Print non-fatal summary notices
        lines = [line for line in res.stderr.splitlines() if "warning" in line.lower() or "error" in line.lower()]
        if lines:
            print("Notice/Warnings:", lines[:5])

if __name__ == "__main__":
    restore_to_neon()
