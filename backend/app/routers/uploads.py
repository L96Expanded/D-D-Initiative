from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from fastapi.responses import FileResponse
import os
from typing import List
from app.config import settings
from app.models.schemas import FileUpload, ErrorResponse
from app.utils.dependencies import get_current_user
from app.models.models import User
from app.utils.storage import storage_service

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

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
        # Save the file using storage service (Azure or local)
        file_url = await storage_service.save_image(file, subfolder="user_uploads")
        
        # Extract filename from URL for response
        filename = file_url.split("/")[-1]
        
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
    # Construct image URL/path
    if settings.USE_AZURE_STORAGE:
        # For Azure, we need the full URL (stored in database)
        # This endpoint might need updating to accept full URL
        image_path = filename
    else:
        image_path = f"/uploads/user_uploads/{filename}"
    
    await storage_service.delete_image(image_path)
    
    return {"message": "Image deleted successfully"}