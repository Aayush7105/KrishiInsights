import os
from typing import List
from dotenv import load_dotenv

# Search for environment variables:
# 1. Local backend/.env (default local PostgreSQL)
# 2. Root .env or .env.local (supports Neon when USE_NEON=true or when specified)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Load backend/.env first
load_dotenv(os.path.join(backend_dir, ".env"))

# If USE_NEON=true is set, load root .env.local / .env
if os.getenv("USE_NEON", "").lower() in ("true", "1", "yes"):
    load_dotenv(os.path.join(root_dir, ".env.local"), override=True)
    load_dotenv(os.path.join(root_dir, ".env"), override=True)
else:
    load_dotenv(os.path.join(root_dir, ".env"))

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
    
    # Database Configuration (Environment-driven, supports local & hosted PostgreSQL)
    DATABASE_URL: str = normalize_database_url(
        os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://krishiinsights_user:password@localhost:5432/krishiinsights_db"
        )
    )

    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

settings = Settings()
