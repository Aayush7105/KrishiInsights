"""
KrishiInsights - Preflight check for Neon destination database.
Verifies project, branch, database, role permissions, and public schema object count.
Credentials are read dynamically from .env.local without logging or printing secrets.
"""

import os
import sys
import urllib.parse
from dotenv import dotenv_values
from sqlalchemy import create_engine, text

def check_neon():
    envs = dotenv_values(".env.local")
    url = envs.get("DATABASE_URL_UNPOOLED") or envs.get("DATABASE_URL")
    if not url:
        print("ERROR: No DATABASE_URL found in .env.local")
        sys.exit(1)

    parsed = urllib.parse.urlparse(url)
    db_name = parsed.path.lstrip("/")
    host = parsed.hostname
    sslmode = urllib.parse.parse_qs(parsed.query).get("sslmode", ["missing"])[0]

    print("[NEON METADATA]")
    print(f"  * Target Database   : {db_name}")
    print(f"  * Host              : {host}")
    print(f"  * SSL Mode          : {sslmode}")

    db_url = url.replace("postgresql://", "postgresql+psycopg2://", 1) if url.startswith("postgresql://") else url
    engine = create_engine(db_url, pool_pre_ping=True)
    with engine.connect() as conn:
        user, db, in_recovery = conn.execute(text("SELECT current_user, current_database(), pg_is_in_recovery();")).fetchone()
        server_ver = conn.execute(text("SELECT version();")).scalar()

        # Check existing tables in public schema
        tables = conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"
        )).fetchall()

        # Check permission to create table
        test_tbl = "_perm_test"
        conn.execute(text(f"CREATE TABLE {test_tbl} (id serial primary key);"))
        conn.execute(text(f"DROP TABLE {test_tbl};"))
        conn.commit()

        print("\n[NEON CONNECTION & PERMISSIONS]")
        print(f"  * Connected User    : {user}")
        print(f"  * Connected DB      : {db}")
        print(f"  * Server Version    : {server_ver.split(',')[0]}")
        print(f"  * In Recovery (RO)  : {in_recovery}")
        print(f"  * DDL Permissions   : VERIFIED (CREATE/DROP TABLE succeeded)")
        print(f"  * Public Tables     : {len(tables)} tables")
        if tables:
            print("  * Warning: Existing tables found:", [t[0] for t in tables])
        else:
            print("  * Public Schema Status: EMPTY (0 tables - ready for migration)")

if __name__ == "__main__":
    check_neon()
