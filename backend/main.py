from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os

from app.config import settings
from app.models.database import engine, get_db
from app.models import models
from app.routers import auth, users, encounters, creatures, uploads

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="D&D Initiative Tracker API",
    description="API for managing D&D encounters and initiative tracking",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Mount static files for uploads
upload_path = settings.UPLOAD_DIR
if not os.path.exists(upload_path):
    os.makedirs(upload_path)

app.mount("/uploads", StaticFiles(directory=upload_path), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(encounters.router, prefix="/encounters", tags=["Encounters"])
app.include_router(creatures.router, prefix="/creatures", tags=["Creatures"])
app.include_router(uploads.router, prefix="/upload", tags=["File Upload"])

@app.get("/")
async def root():
    return {"message": "D&D Initiative Tracker API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)