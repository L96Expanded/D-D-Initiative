from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from fastapi.responses import FileResponse
import aiofiles
import os
import uuid
from PIL import Image
from typing import List
from app.config import settings
from app.models.schemas import FileUpload, ErrorResponse
from app.utils.dependencies import get_current_user
from app.models.models import User

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_SIZE = (1920, 1080)  # Max width and height

def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return os.path.splitext(filename)[1].lower()

def validate_image_file(file: UploadFile) -> bool:
    """Validate image file type and size."""
    if not file.content_type or not file.content_type.startswith("image/"):
        return False
    
    extension = get_file_extension(file.filename or "")
    if extension not in ALLOWED_EXTENSIONS:
        return False
    
    return True

async def save_image(file: UploadFile, subfolder: str = "") -> str:
    """Save uploaded image and return the file path."""
    # Generate unique filename
    file_extension = get_file_extension(file.filename or "")
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create full path
    upload_dir = os.path.join(settings.UPLOAD_DIR, subfolder) if subfolder else settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    async with aiofiles.open(file_path, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)
    
    # Optimize image
    try:
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Resize if too large
            if img.size[0] > MAX_IMAGE_SIZE[0] or img.size[1] > MAX_IMAGE_SIZE[1]:
                img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(file_path, optimize=True, quality=85)
    except Exception as e:
        # If image processing fails, remove the file
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image file: {str(e)}"
        )
    
    # Return relative path for URL
    return os.path.join(subfolder, unique_filename).replace("\\", "/") if subfolder else unique_filename

@router.post("/images", response_model=FileUpload)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload an image file."""
    # Validate file
    if not validate_image_file(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file. Only JPEG, PNG, and WebP files are allowed."
        )
    
    # Check file size
    if hasattr(file, 'size') and file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE // 1024 // 1024}MB."
        )
    
    try:
        # Save the file
        filename = await save_image(file, "user_uploads")
        file_url = f"/uploads/{filename}"
        
        return FileUpload(filename=filename, url=file_url)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@router.get("/images/{filename}")
async def get_image(filename: str):
    """Serve an uploaded image."""
    file_path = os.path.join(settings.UPLOAD_DIR, "user_uploads", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    return FileResponse(file_path)

@router.delete("/images/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Delete an uploaded image."""
    file_path = os.path.join(settings.UPLOAD_DIR, "user_uploads", filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    return {"message": "Image deleted successfully"}