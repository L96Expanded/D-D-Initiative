"""
Storage service for handling file uploads to local filesystem or Azure Blob Storage.
"""
import os
import uuid
import aiofiles
from io import BytesIO
from PIL import Image
from typing import Optional
from fastapi import UploadFile
from app.config import settings

# Azure Blob Storage (optional)
try:
    from azure.storage.blob import BlobServiceClient, ContentSettings
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


class StorageService:
    """Handles file storage operations for both local and cloud storage."""
    
    def __init__(self):
        self.use_azure = settings.USE_AZURE_STORAGE and AZURE_AVAILABLE
        if self.use_azure:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                settings.AZURE_STORAGE_CONNECTION_STRING
            )
            self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
            self._ensure_container_exists()
    
    def _ensure_container_exists(self):
        """Ensure the Azure Blob Storage container exists."""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container(public_access='blob')
        except Exception as e:
            print(f"Error ensuring container exists: {e}")
    
    async def save_image(
        self, 
        file: UploadFile, 
        subfolder: str = "",
        max_size: tuple = (1920, 1080)
    ) -> str:
        """
        Save an uploaded image and return its URL or path.
        
        Args:
            file: The uploaded file
            subfolder: Subfolder to organize files
            max_size: Maximum image dimensions (width, height)
            
        Returns:
            str: URL (Azure) or relative path (local) to the saved image
        """
        # Generate unique filename
        file_extension = os.path.splitext(file.filename or "")[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Add subfolder to filename if provided
        if subfolder:
            unique_filename = f"{subfolder}/{unique_filename}"
        
        # Read and optimize image
        content = await file.read()
        optimized_content = await self._optimize_image(content, max_size)
        
        if self.use_azure:
            return await self._save_to_azure(unique_filename, optimized_content, file.content_type)
        else:
            return await self._save_to_local(unique_filename, optimized_content)
    
    async def _optimize_image(self, content: bytes, max_size: tuple) -> bytes:
        """Optimize image size and quality."""
        try:
            img = Image.open(BytesIO(content))
            
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            
            # Resize if needed
            if img.width > max_size[0] or img.height > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized image to bytes
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
        except Exception as e:
            print(f"Error optimizing image: {e}")
            return content  # Return original if optimization fails
    
    async def _save_to_azure(self, filename: str, content: bytes, content_type: Optional[str]) -> str:
        """Save file to Azure Blob Storage and return public URL."""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=filename
            )
            
            # Set content type for proper browser handling
            content_settings = ContentSettings(content_type=content_type or 'image/jpeg')
            
            blob_client.upload_blob(
                content,
                overwrite=True,
                content_settings=content_settings
            )
            
            # Return public URL
            return blob_client.url
        except Exception as e:
            print(f"Error saving to Azure: {e}")
            raise
    
    async def _save_to_local(self, filename: str, content: bytes) -> str:
        """Save file to local filesystem and return relative path."""
        # Create full path
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save file
        async with aiofiles.open(file_path, "wb") as buffer:
            await buffer.write(content)
        
        # Return relative path (frontend will prepend API URL)
        return f"/uploads/{filename}"
    
    async def delete_image(self, image_url: str) -> bool:
        """Delete an image from storage."""
        if self.use_azure:
            return await self._delete_from_azure(image_url)
        else:
            return await self._delete_from_local(image_url)
    
    async def _delete_from_azure(self, image_url: str) -> bool:
        """Delete file from Azure Blob Storage."""
        try:
            # Extract blob name from URL
            blob_name = image_url.split(f"{self.container_name}/")[-1]
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            blob_client.delete_blob()
            return True
        except Exception as e:
            print(f"Error deleting from Azure: {e}")
            return False
    
    async def _delete_from_local(self, image_path: str) -> bool:
        """Delete file from local filesystem."""
        try:
            # Remove leading /uploads/ from path
            relative_path = image_path.lstrip('/uploads/')
            file_path = os.path.join(settings.UPLOAD_DIR, relative_path)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting from local: {e}")
            return False


# Global storage service instance
storage_service = StorageService()
