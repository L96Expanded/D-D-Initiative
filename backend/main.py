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

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="D&D Initiative Tracker API",
    description="API for managing D&D encounters and initiative tracking",
    version="1.0.0"
)

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

# Serve frontend static files if they exist
static_dir = "./static"
if os.path.exists(static_dir):
    from fastapi.responses import FileResponse
    from fastapi.exceptions import HTTPException
    from starlette.exceptions import HTTPException as StarletteHTTPException
    
    # Mount assets directory for static files (js, css, images)
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    
    # Serve index.html for root
    @app.get("/")
    async def serve_root():
        return FileResponse(os.path.join(static_dir, "index.html"))
    
    # Catch-all for 404s - serve index.html for SPA routing
    @app.exception_handler(404)
    async def custom_404_handler(request, exc):
        # Check if it's an API request - return JSON 404
        path = request.url.path
        api_prefixes = ("/api", "/auth", "/users", "/encounters", "/creatures", "/presets", "/upload", "/debug")
        if any(path.startswith(prefix) for prefix in api_prefixes):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        # For non-API routes, serve index.html for SPA routing
        return FileResponse(os.path.join(static_dir, "index.html"))
    
    print(f"Serving frontend SPA from: {static_dir}")
else:
    @app.get("/")
    async def root():
        return {"message": "D&D Initiative Tracker API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)