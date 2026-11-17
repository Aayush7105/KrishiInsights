import os
from typing import List
from dotenv import load_dotenv

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Load environment configuration:
# 1. Root .env and .env.local (contains Neon project configuration)
load_dotenv(os.path.join(root_dir, ".env.local"))
load_dotenv(os.path.join(root_dir, ".env"))
# 2. backend/.env
load_dotenv(os.path.join(backend_dir, ".env"))

def normalize_database_url(url: str) -> str:
    """Ensures PostgreSQL URLs use psycopg2 dialect for SQLAlchemy compatibility."""
    if not url:
        return url
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    return url

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "KrishiInsights API")
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION", "0.1.0")
    API_PREFIX: str = os.getenv("API_PREFIX", "/api")
    
    # Primary Database Configuration (Neon Serverless PostgreSQL)
    raw_db_url = os.getenv("DATABASE_URL")
    if not raw_db_url:
        raise ValueError(
            "CRITICAL: DATABASE_URL is not set. Neon Serverless Postgres is the primary database. "
            "Please ensure .env or .env.local contains a valid Neon connection string."
        )
    DATABASE_URL: str = normalize_database_url(raw_db_url)

    # Direct / Unpooled Connection (Used for Alembic migrations and DDL)
    raw_direct_url = os.getenv("DATABASE_URL_DIRECT") or os.getenv("DATABASE_URL_UNPOOLED") or raw_db_url
    DATABASE_URL_DIRECT: str = normalize_database_url(raw_direct_url)

    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

settings = Settings()
