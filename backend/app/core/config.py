import os
from typing import List
from dotenv import load_dotenv

# Search for .env in current working dir or backend/ directory
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "KrishiInsights API")
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION", "0.1.0")
    API_PREFIX: str = os.getenv("API_PREFIX", "/api")
    
    # Database Configuration (Environment-driven, supports local & hosted PostgreSQL)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://krishiinsights_user:password@localhost:5432/krishiinsights_db"
    )

    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

settings = Settings()
