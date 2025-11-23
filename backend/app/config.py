from pydantic_settings import BaseSettings
from typing import List
import os
import json

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://dnd_user:secure_password@localhost:5432/dnd_tracker"
    
    # JWT
    JWT_SECRET: str = "your_jwt_secret_key_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # CORS - Updated for production
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Production settings
    ENVIRONMENT: str = "development"  # development, staging, production
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    SECURE_COOKIES: bool = False
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Handle JSON string parsing for CORS_ORIGINS from environment
        cors_origins_env = os.getenv('CORS_ORIGINS')
        if cors_origins_env:
            try:
                self.CORS_ORIGINS = json.loads(cors_origins_env)
            except json.JSONDecodeError:
                pass  # Keep default if JSON parsing fails
                
        # Handle JSON string parsing for ALLOWED_HOSTS from environment  
        allowed_hosts_env = os.getenv('ALLOWED_HOSTS')
        if allowed_hosts_env:
            try:
                self.ALLOWED_HOSTS = json.loads(allowed_hosts_env)
            except json.JSONDecodeError:
                pass  # Keep default if JSON parsing fails

settings = Settings()