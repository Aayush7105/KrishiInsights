"""
KrishiInsights - Local PostgreSQL Backup Script
Generates a timestamped custom-format (.dump) backup using PostgreSQL 17 pg_dump.
"""

import os
import sys
import datetime
import subprocess
import urllib.parse
from dotenv import dotenv_values

def backup_local():
    backend_env = dotenv_values("backend/.env")
    url = backend_env.get("DATABASE_URL")
    if not url:
        print("ERROR: DATABASE_URL not found in backend/.env")
        sys.exit(1)

    parsed = urllib.parse.urlparse(url)
    username = parsed.username
    password = parsed.password
    host = parsed.hostname or "localhost"
    port = str(parsed.port or 5432)
    dbname = parsed.path.lstrip("/")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.abspath("database/backups")
    os.makedirs(backup_dir, exist_ok=True)
    backup_file = os.path.join(backup_dir, f"krishiinsights_db_backup_{timestamp}.dump")

    pg_dump_bin = r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"
    if not os.path.exists(pg_dump_bin):
        print(f"ERROR: pg_dump not found at {pg_dump_bin}")
        sys.exit(1)

    print(f"[LOCAL BACKUP INITIATION]")
    print(f"  * Database   : {dbname}")
    print(f"  * Host       : {host}:{port}")
    print(f"  * User       : {username}")
    print(f"  * Target File: {backup_file}")

    cmd = [
        pg_dump_bin,
        "-h", host,
        "-p", port,
        "-U", username,
        "-d", dbname,
        "-Fc",                    # Custom PostgreSQL archive format
        "--no-owner",            # Prevent hardcoding local roles
        "--no-acl",              # Prevent hardcoding local privileges
        "-f", backup_file
    ]

    env = os.environ.copy()
    if password:
        env["PGPASSWORD"] = password

    t0 = datetime.datetime.now()
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    elapsed = (datetime.datetime.now() - t0).total_seconds()

    if res.returncode != 0:
        print(f"ERROR: pg_dump failed with returncode {res.returncode}")
        print("STDERR:", res.stderr)
        sys.exit(1)

    file_size_mb = os.path.getsize(backup_file) / (1024 * 1024)
    print(f"[BACKUP SUCCESSFUL]")
    print(f"  * File Size : {file_size_mb:.2f} MB")
    print(f"  * Duration  : {elapsed:.2f}s")
    print(f"  * Location  : {backup_file}")
    return backup_file

if __name__ == "__main__":
    backup_local()
