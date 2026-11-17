import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load from backend/.env or root .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))
load_dotenv()

db_url = os.getenv("DATABASE_URL")

if not db_url or "YOUR_PASSWORD_HERE" in db_url:
    print("\n[!] ACTION REQUIRED:")
    print("Database password placeholder detected in 'backend/.env'.")
    print("Please open 'backend/.env' and replace 'YOUR_PASSWORD_HERE' with your PostgreSQL password for 'krishiinsights_user'.")
    print("Example: DATABASE_URL=postgresql+psycopg2://krishiinsights_user:mysecretpassword@localhost:5432/krishiinsights_db\n")
    sys.exit(1)

# Mask password when displaying connection string
masked_url = db_url
if "@" in db_url and "://" in db_url:
    proto_user, host_db = db_url.split("@", 1)
    if ":" in proto_user:
        proto, user = proto_user.split("://", 1)[0], proto_user.split("://", 1)[1]
        user_name = user.split(":")[0]
        masked_url = f"{proto}://{user_name}:****@{host_db}"

print(f"Attempting connection to: {masked_url}")

try:
    engine = create_engine(db_url, connect_args={"connect_timeout": 5})
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version();")).scalar()
        current_user = conn.execute(text("SELECT current_user;")).scalar()
        current_db = conn.execute(text("SELECT current_database();")).scalar()
        print("\n[SUCCESS] Connected to PostgreSQL successfully!")
        print(f"  * Current Database: {current_db}")
        print(f"  * Authenticated User: {current_user}")
        print(f"  * Server Version: {version}\n")
except Exception as e:
    print(f"\n[ERROR] Connection failed: {e}\n")
    sys.exit(2)
