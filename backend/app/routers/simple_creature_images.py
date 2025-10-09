from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, Dict, Any, List
import json
import os
import shutil
from uuid import uuid4
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["creature_images"])

# Path to the creature database JSON file
CREATURE_DB_PATH = os.getenv("CREATURE_DB_PATH", "./creature_database.json")
DATABASE_IMAGES_DIR = os.getenv("DATABASE_IMAGES_DIR", "./database_images")

def load_creature_database() -> Dict[str, str]:
    """Load the creature database from JSON file."""
    try:
        if os.path.exists(CREATURE_DB_PATH):
            with open(CREATURE_DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"Creature database file not found: {CREATURE_DB_PATH}")
            return {}
    except Exception as e:
        logger.error(f"Error loading creature database: {e}")
        return {}

def save_creature_database(creature_db: Dict[str, str]) -> bool:
    """Save the creature database to JSON file."""
    try:
        with open(CREATURE_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(creature_db, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving creature database: {e}")
        return False

def scan_local_images() -> Dict[str, str]:
    """Scan database images directory and return creature name to image path mapping."""
    local_creatures = {}
    
    if not os.path.exists(DATABASE_IMAGES_DIR):
        logger.info(f"Database images directory {DATABASE_IMAGES_DIR} does not exist")
        return local_creatures
    
    # Supported image extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    
    for file_path in Path(DATABASE_IMAGES_DIR).iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            # Convert filename to creature name (replace underscores with spaces)
            creature_name = file_path.stem.replace('_', ' ').lower()
            image_url = f"/database_images/{file_path.name}"
            local_creatures[creature_name] = image_url
            logger.info(f"Found local image: {creature_name} -> {file_path.name}")
    
    return local_creatures

def find_creature_image(creature_name: str, creature_db: Dict[str, str]) -> Optional[str]:
    """Find the best matching image for a creature name."""
    name_lower = creature_name.lower().strip()
    
    # 1. Exact match
    if name_lower in creature_db:
        return creature_db[name_lower]
    
    # 2. Partial match (contains any word from the creature name)
    name_words = name_lower.split()
    for db_creature, image_url in creature_db.items():
        for word in name_words:
            if len(word) > 2 and word in db_creature:
                logger.info(f"Partial match: '{creature_name}' matched '{db_creature}' on word '{word}'")
                return image_url
    
    # 3. Reverse partial match (any word from db creature name in input)
    for db_creature, image_url in creature_db.items():
        db_words = db_creature.split()
        for db_word in db_words:
            if len(db_word) > 2 and db_word in name_lower:
                logger.info(f"Reverse partial match: '{creature_name}' matched '{db_creature}' on word '{db_word}'")
                return image_url
    
    return None

@router.get("/get_creature_image")
async def get_creature_image(
    name: str,
    creature_type: str = "other",  # Keep for compatibility but not used
    user_image_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get creature image from JSON database with intelligent matching.
    """
    logger.info(f"Getting image for creature: {name}")
    
    try:
        # Priority 1: User provided image
        if user_image_url:
            logger.info(f"Using user provided image: {user_image_url}")
            return {
                "image_url": user_image_url,
                "source": "user",
                "name": name,
                "found_match": True
            }
        
        # Load creature database
        creature_db = load_creature_database()
        
        # Scan for local images and merge with database
        local_creatures = scan_local_images()
        # Local images override database entries
        creature_db.update(local_creatures)
        
        # Priority 2: Find in database
        image_url = find_creature_image(name, creature_db)
        
        if image_url:
            source = "local" if name.lower() in local_creatures else "database"
            logger.info(f"Found image for '{name}': {image_url} (source: {source})")
            return {
                "image_url": image_url,
                "source": source,
                "name": name,
                "found_match": True
            }
        
        # Priority 3: Default fallback
        default_image = "https://via.placeholder.com/400x400/cccccc/666666?text=No+Image"
        logger.info(f"Using default fallback for '{name}'")
        
        return {
            "image_url": default_image,
            "source": "default",
            "name": name,
            "found_match": False
        }
        
    except Exception as e:
        logger.error(f"Error getting image for '{name}': {e}")
        return {
            "image_url": "https://via.placeholder.com/400x400/ff0000/ffffff?text=Error",
            "source": "error",
            "name": name,
            "found_match": False,
            "error": str(e)
        }

@router.get("/list_all_creatures")
async def list_all_creatures() -> Dict[str, Any]:
    """List all creatures in the database."""
    try:
        creature_db = load_creature_database()
        local_creatures = scan_local_images()
        
        # Merge local and database creatures
        all_creatures = {**creature_db, **local_creatures}
        
        creature_list = [
            {
                "name": name,
                "image_url": image_url,
                "source": "local" if name in local_creatures else "database"
            }
            for name, image_url in sorted(all_creatures.items())
        ]
        
        return {
            "creatures": creature_list,
            "total": len(creature_list),
            "local_count": len(local_creatures),
            "database_count": len(creature_db)
        }
        
    except Exception as e:
        logger.error(f"Error listing creatures: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search_creatures")
async def search_creatures(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for creatures by name."""
    try:
        creature_db = load_creature_database()
        local_creatures = scan_local_images()
        all_creatures = {**creature_db, **local_creatures}
        
        query_lower = query.lower()
        results = []
        
        for name, image_url in all_creatures.items():
            if query_lower in name.lower() and len(results) < limit:
                results.append({
                    "name": name,
                    "image_url": image_url,
                    "source": "local" if name in local_creatures else "database"
                })
        
        return results
        
    except Exception as e:
        logger.error(f"Error searching creatures: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_creature")
async def add_creature(
    creature_name: str = Form(...),
    image_url: str = Form(...),
) -> Dict[str, Any]:
    """Add a new creature to the database."""
    try:
        creature_db = load_creature_database()
        creature_name_lower = creature_name.lower().strip()
        
        creature_db[creature_name_lower] = image_url
        
        if save_creature_database(creature_db):
            logger.info(f"Added creature: {creature_name_lower} -> {image_url}")
            return {
                "message": "Creature added successfully",
                "name": creature_name_lower,
                "image_url": image_url
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save database")
            
    except Exception as e:
        logger.error(f"Error adding creature: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload_creature_image")
async def upload_creature_image(
    creature_name: str = Form(...),
    image: UploadFile = File(...)
) -> Dict[str, Any]:
    """Upload and associate a new creature image."""
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create upload directory if it doesn't exist
        os.makedirs(DATABASE_IMAGES_DIR, exist_ok=True)
        
        # Generate filename from creature name
        clean_name = creature_name.lower().replace(' ', '_').replace('-', '_')
        file_extension = os.path.splitext(image.filename)[1] if image.filename else '.jpg'
        filename = f"{clean_name}{file_extension}"
        file_path = os.path.join(DATABASE_IMAGES_DIR, filename)
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # The image will be automatically picked up by scan_local_images()
        # No need to modify the JSON database
        
        logger.info(f"Uploaded creature image: {creature_name} -> {filename}")
        
        return {
            "message": "Creature image uploaded successfully",
            "creature_name": creature_name.lower(),
            "filename": filename,
            "image_url": f"/local_images/{filename}"
        }
        
    except Exception as e:
        logger.error(f"Error uploading creature image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/remove_creature/{creature_name}")
async def remove_creature(creature_name: str) -> Dict[str, Any]:
    """Remove a creature from the database."""
    try:
        creature_db = load_creature_database()
        creature_name_lower = creature_name.lower().strip()
        
        if creature_name_lower in creature_db:
            del creature_db[creature_name_lower]
            if save_creature_database(creature_db):
                logger.info(f"Removed creature: {creature_name_lower}")
                return {"message": f"Creature '{creature_name_lower}' removed successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to save database")
        else:
            raise HTTPException(status_code=404, detail=f"Creature '{creature_name_lower}' not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing creature: {e}")
        raise HTTPException(status_code=500, detail=str(e))