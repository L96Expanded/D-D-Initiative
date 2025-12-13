"""
Storage service for handling file uploads to local filesystem or Azure Blob Storage.
"""
import os
import uuid
import aiofiles
import logging
from io import BytesIO
from PIL import Image
from typing import Optional
from fastapi import UploadFile, HTTPException
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

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
        
        if settings.USE_AZURE_STORAGE and not AZURE_AVAILABLE:
            logger.warning("Azure Storage requested but azure-storage-blob not installed. Falling back to local storage.")
            logger.info("Install with: pip install azure-storage-blob")
            self.use_azure = False
        
        if self.use_azure:
            try:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    settings.AZURE_STORAGE_CONNECTION_STRING
                )
                self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
                self._ensure_container_exists()
                logger.info(f"Azure Blob Storage initialized (container: {self.container_name})")
            except Exception as e:
                logger.error(f"Failed to initialize Azure Blob Storage: {e}")
                logger.warning("Falling back to local storage")
                self.use_azure = False
        
        if not self.use_azure:
            logger.info(f"Using local file storage: {settings.UPLOAD_DIR}")
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    def _ensure_container_exists(self):
        """Ensure the Azure Blob Storage container exists."""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                logger.info(f"Creating Azure Blob container: {self.container_name}")
                container_client.create_container(public_access='blob')
                logger.info(f"Container {self.container_name} created successfully")
            else:
                logger.debug(f"Container {self.container_name} already exists")
        except Exception as e:
            logger.error(f"Error ensuring container exists: {e}")
            raise
    
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
            original_size = img.size
            
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            
            # Resize if needed
            if img.width > max_size[0] or img.height > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                logger.debug(f"Resized image from {original_size} to {img.size}")
            
            # Save optimized image to bytes
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            optimized_content = output.getvalue()
            
            compression_ratio = len(optimized_content) / len(content) * 100
            logger.debug(f"Optimized image: {len(content)} -> {len(optimized_content)} bytes ({compression_ratio:.1f}%)")
            
            return optimized_content
        except Exception as e:
            logger.warning(f"Error optimizing image: {e}. Using original.")
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
            
            logger.info(f"Uploading {len(content)} bytes to Azure Blob: {filename}")
            blob_client.upload_blob(
                content,
                overwrite=True,
                content_settings=content_settings
            )
            
            # Return public URL
            url = blob_client.url
            logger.info(f"Successfully uploaded to: {url}")
            return url
        except Exception as e:
            logger.error(f"Error saving to Azure: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to upload file to cloud storage: {str(e)}")
    
    async def _save_to_local(self, filename: str, content: bytes) -> str:
        """Save file to local filesystem and return relative path."""
        try:
            # Create full path
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save file
            logger.info(f"Saving {len(content)} bytes to local storage: {file_path}")
            async with aiofiles.open(file_path, "wb") as buffer:
                await buffer.write(content)
            
            # Return relative path (frontend will prepend API URL)
            relative_path = f"/uploads/{filename}"
            logger.info(f"Saved to local storage: {relative_path}")
            return relative_path
        except Exception as e:
            logger.error(f"Error saving to local storage: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save file locally: {str(e)}")
    
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
            logger.info(f"Deleting blob from Azure: {blob_name}")
            
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            blob_client.delete_blob()
            logger.info(f"Successfully deleted blob: {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting from Azure: {e}")
            return False
    
    async def _delete_from_local(self, image_path: str) -> bool:
        """Delete file from local filesystem."""
        try:
            # Remove leading /uploads/ from path
            relative_path = image_path.lstrip('/uploads/')
            file_path = os.path.join(settings.UPLOAD_DIR, relative_path)
            
            if os.path.exists(file_path):
                logger.info(f"Deleting local file: {file_path}")
                os.remove(file_path)
                logger.info(f"Successfully deleted: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting from local: {e}")
            return False


# Global storage service instance
storage_service = StorageService()
