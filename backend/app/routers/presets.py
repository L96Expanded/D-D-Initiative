from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.models.database import get_db
from app.models.models import User, Preset, PresetCreature
from app.models.schemas import (
    PresetCreate, PresetUpdate, PresetResponse, 
    PresetSummary, CreatureCreate, CreatureCreateNested, ErrorResponse
)
from app.utils.dependencies import get_current_user
import uuid

router = APIRouter()

@router.get("", response_model=List[PresetSummary])
async def get_user_presets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all presets for the current user."""
    presets = db.query(
        Preset.id,
        Preset.name,
        Preset.description,
        Preset.background_image,
        Preset.created_at,
        func.count(PresetCreature.id).label("creature_count")
    ).outerjoin(PresetCreature).filter(
        Preset.user_id == current_user.id
    ).group_by(
        Preset.id, Preset.name, Preset.description, Preset.background_image, Preset.created_at
    ).order_by(Preset.created_at.desc()).all()
    
    return [
        PresetSummary(
            id=preset.id,
            name=preset.name,
            description=preset.description,
            background_image=preset.background_image,
            created_at=preset.created_at,
            creature_count=preset.creature_count
        )
        for preset in presets
    ]

@router.post("", response_model=PresetResponse, status_code=status.HTTP_201_CREATED)
async def create_preset(
    preset_data: PresetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new preset."""
    # Create preset
    db_preset = Preset(
        user_id=current_user.id,
        name=preset_data.name,
        description=preset_data.description,
        background_image=preset_data.background_image
    )
    
    db.add(db_preset)
    db.flush()  # Get the ID without committing
    
    # Create preset creatures
    for creature_data in preset_data.creatures:
        db_creature = PresetCreature(
            preset_id=db_preset.id,
            name=creature_data.name,
            initiative=creature_data.initiative,
            creature_type=creature_data.creature_type,
            image_url=creature_data.image_url
        )
        db.add(db_creature)
    
    db.commit()
    db.refresh(db_preset)
    
    # Convert preset creatures to CreatureCreateNested format for response
    creatures = [
        CreatureCreateNested(
            name=pc.name,
            initiative=pc.initiative,
            creature_type=pc.creature_type,
            image_url=pc.image_url
        )
        for pc in db_preset.preset_creatures
    ]
    
    return PresetResponse(
        id=db_preset.id,
        user_id=db_preset.user_id,
        name=db_preset.name,
        description=db_preset.description,
        background_image=db_preset.background_image,
        created_at=db_preset.created_at,
        updated_at=db_preset.updated_at,
        creatures=creatures
    )

@router.get("/{preset_id}", response_model=PresetResponse)
async def get_preset(
    preset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific preset."""
    preset = db.query(Preset).filter(
        Preset.id == preset_id,
        Preset.user_id == current_user.id
    ).first()
    
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preset not found"
        )
    
    # Convert preset creatures to CreatureCreateNested format
    creatures = [
        CreatureCreateNested(
            name=pc.name,
            initiative=pc.initiative,
            creature_type=pc.creature_type,
            image_url=pc.image_url
        )
        for pc in preset.preset_creatures
    ]
    
    return PresetResponse(
        id=preset.id,
        user_id=preset.user_id,
        name=preset.name,
        description=preset.description,
        background_image=preset.background_image,
        created_at=preset.created_at,
        updated_at=preset.updated_at,
        creatures=creatures
    )

@router.put("/{preset_id}", response_model=PresetResponse)
async def update_preset(
    preset_id: uuid.UUID,
    preset_data: PresetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a preset."""
    preset = db.query(Preset).filter(
        Preset.id == preset_id,
        Preset.user_id == current_user.id
    ).first()
    
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preset not found"
        )
    
    # Update fields
    if preset_data.name is not None:
        preset.name = preset_data.name
    if preset_data.description is not None:
        preset.description = preset_data.description
    if preset_data.background_image is not None:
        preset.background_image = preset_data.background_image
    
    # Update creatures if provided
    if preset_data.creatures is not None:
        # Delete existing creatures
        db.query(PresetCreature).filter(PresetCreature.preset_id == preset_id).delete()
        
        # Add new creatures
        for creature_data in preset_data.creatures:
            db_creature = PresetCreature(
                preset_id=preset_id,
                name=creature_data.name,
                initiative=creature_data.initiative,
                creature_type=creature_data.creature_type,
                image_url=creature_data.image_url
            )
            db.add(db_creature)
    
    db.commit()
    db.refresh(preset)
    
    # Convert preset creatures to CreatureCreateNested format
    creatures = [
        CreatureCreateNested(
            name=pc.name,
            initiative=pc.initiative,
            creature_type=pc.creature_type,
            image_url=pc.image_url
        )
        for pc in preset.preset_creatures
    ]
    
    return PresetResponse(
        id=preset.id,
        user_id=preset.user_id,
        name=preset.name,
        description=preset.description,
        background_image=preset.background_image,
        created_at=preset.created_at,
        updated_at=preset.updated_at,
        creatures=creatures
    )

@router.delete("/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preset(
    preset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a preset."""
    preset = db.query(Preset).filter(
        Preset.id == preset_id,
        Preset.user_id == current_user.id
    ).first()
    
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preset not found"
        )
    
    db.delete(preset)
    db.commit()
    
    return {"message": "Preset deleted successfully"}