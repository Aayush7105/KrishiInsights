from fastapi import APIRouter
from datetime import datetime, timezone
from sqlalchemy import text
from app.core.config import settings
from app.database.session import engine

router = APIRouter()

@router.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint returning system status, timestamp, and database connectivity.
    """
    db_status = "unconfigured"
    if "YOUR_PASSWORD_HERE" not in settings.DATABASE_URL:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1;"))
                db_status = "connected"
        except Exception as e:
            db_status = "disconnected"

    return {
        "status": "healthy",
        "service": "KrishiInsights API",
        "version": "0.1.0",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
