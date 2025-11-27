from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import time

from app.config import settings
from app.models.database import engine, get_db
from app.models import models
from app.routers import auth, users, encounters, creatures, uploads, presets, simple_creature_images, health
from app.utils.metrics import PrometheusMiddleware, router as metrics_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="D&D Initiative Tracker API",
    description="API for managing D&D encounters and initiative tracking",
    version="1.0.0"
)

# Create database tables - with error handling
try:
    logger.info("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Failed to create database tables: {e}")
    logger.warning("Application will start but database operations may fail")

# Security middleware - Add trusted host middleware
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Add Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Add security headers
    if settings.ENVIRONMENT == "production":
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# Mount static files for uploads
upload_path = settings.UPLOAD_DIR
if not os.path.exists(upload_path):
    os.makedirs(upload_path)

app.mount("/uploads", StaticFiles(directory=upload_path), name="uploads")

# Mount database images directory if it exists
database_images_path = os.getenv("DATABASE_IMAGES_DIR", "database_images")
if os.path.exists(database_images_path):
    app.mount("/database_images", StaticFiles(directory=database_images_path), name="database_images")

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(metrics_router, tags=["Metrics"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(encounters.router, prefix="/encounters", tags=["Encounters"])
app.include_router(creatures.router, prefix="/creatures", tags=["Creatures"])
app.include_router(presets.router, prefix="/presets", tags=["Presets"])
app.include_router(uploads.router, prefix="/upload", tags=["File Upload"])
app.include_router(simple_creature_images.router, prefix="/api/creature-images", tags=["Creature Images"])

# Debug endpoint to check CORS configuration
@app.get("/debug/cors")
async def debug_cors():
    """Debug endpoint to check CORS configuration."""
    return {
        "cors_origins": settings.CORS_ORIGINS,
        "allowed_hosts": settings.ALLOWED_HOSTS,
        "environment": settings.ENVIRONMENT
    }

# Initialize JSON-based creature database
@app.on_event("startup")
async def startup_event():
    """Initialize the creature database."""
    import json
    import os
    
    # Ensure creature database exists
    creature_db_path = "./creature_database.json"
    if not os.path.exists(creature_db_path):
        default_db = {
            "dragon": "/database_images/dragon.jpg",
            "orc": "/database_images/orc.jpg", 
            "skeleton": "/database_images/skeleton.png"
        }
        with open(creature_db_path, 'w') as f:
            json.dump(default_db, f, indent=2)
        print(f"Created default creature database: {creature_db_path}")
    
    # Ensure database images directory exists
    database_images_dir = "./database_images"
    os.makedirs(database_images_dir, exist_ok=True)
    print(f"Database images directory ready: {database_images_dir}")

@app.get("/")
async def root():
    return {
        "message": "D&D Initiative Tracker API", 
        "version": "1.0.1", 
        "status": "healthy",
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)