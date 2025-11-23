"""Health check and monitoring router."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any
import sys
import os

from app.models.database import get_db

router = APIRouter(prefix="/api/health", tags=["health"])

# Version information
VERSION = os.getenv("APP_VERSION", "1.0.0")


@router.get("", status_code=status.HTTP_200_OK)
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.
    
    Returns:
        dict: Health status including:
            - status: Overall health status
            - version: Application version
            - database: Database connectivity status
            - timestamp: Current server time
            - python_version: Python runtime version
    """
    health_status = {
        "status": "healthy",
        "version": VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }
    
    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        health_status["database"] = {
            "status": "connected",
            "message": "Database is accessible"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = {
            "status": "disconnected",
            "message": f"Database error: {str(e)}"
        }
    
    return health_status


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Readiness probe for Kubernetes/container orchestration.
    
    Returns 200 if the application is ready to serve requests.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check() -> Dict[str, str]:
    """
    Liveness probe for Kubernetes/container orchestration.
    
    Returns 200 if the application is alive.
    """
    return {"status": "alive"}
