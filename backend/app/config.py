from pydantic_settings import BaseSettings
from typing import List, Optional
import os
import json
import sys

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # JWT - No defaults for security
    JWT_SECRET: str
    SECRET_KEY: Optional[str] = None  # Will be set from JWT_SECRET if not provided
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # Azure Blob Storage (for production)
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER_NAME: str = "creature-images"
    USE_AZURE_STORAGE: bool = False  # Auto-enabled if connection string is set
    
    # Database images directory (for built-in creature images)
    DATABASE_IMAGES_DIR: str = "./database_images"
    
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
        
        # Validate critical configuration
        if not self.DATABASE_URL:
            print("ERROR: DATABASE_URL is required but not set!", file=sys.stderr)
            print("Please set DATABASE_URL environment variable or add it to .env file", file=sys.stderr)
            sys.exit(1)
            
        if not self.JWT_SECRET:
            print("ERROR: JWT_SECRET is required but not set!", file=sys.stderr)
            print("Please set JWT_SECRET environment variable or add it to .env file", file=sys.stderr)
            print("Generate a secure secret with: openssl rand -base64 32", file=sys.stderr)
            sys.exit(1)
        
        # Warn about insecure secrets in production
        if self.ENVIRONMENT == "production":
            insecure_secrets = [
                "changeme", "change_me", "your_secret", "your_jwt_secret", 
                "secure_password", "password", "secret"
            ]
            jwt_lower = self.JWT_SECRET.lower()
            if any(insecure in jwt_lower for insecure in insecure_secrets):
                print("WARNING: JWT_SECRET appears to be insecure or a placeholder!", file=sys.stderr)
                print("Please use a cryptographically random secret in production", file=sys.stderr)
        
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
        
        # Use SECRET_KEY for JWT_SECRET if provided
        if not self.SECRET_KEY:
            self.SECRET_KEY = self.JWT_SECRET
        
        # Auto-enable Azure Storage if connection string is provided
        if self.AZURE_STORAGE_CONNECTION_STRING and self.AZURE_STORAGE_CONNECTION_STRING != "":
            self.USE_AZURE_STORAGE = True
            print(f"✓ Azure Blob Storage enabled (container: {self.AZURE_STORAGE_CONTAINER_NAME})", file=sys.stderr)
        else:
            print(f"ℹ Using local file storage in {self.UPLOAD_DIR}", file=sys.stderr)
            if self.ENVIRONMENT == "production":
                print("⚠ WARNING: Production environment using local storage. Consider using Azure Blob Storage!", file=sys.stderr)

settings = Settings()