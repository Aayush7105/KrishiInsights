from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()

@router.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint returning system status and timestamp.
    """
    return {
        "status": "healthy",
        "service": "KrishiInsights API",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
