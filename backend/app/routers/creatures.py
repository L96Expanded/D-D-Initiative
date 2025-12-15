from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.database import get_db
from app.models.models import User, Creature, Encounter
from app.models.schemas import CreatureCreate, CreatureUpdate, CreatureResponse, ErrorResponse
from app.utils.dependencies import get_current_user
import uuid

router = APIRouter()

@router.get("", response_model=List[CreatureResponse])
async def get_creatures(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all creatures for the current user across all encounters."""
    creatures = db.query(Creature).join(Encounter).filter(
        Encounter.user_id == current_user.id
    ).order_by(Creature.initiative.desc()).all()
    
    return [CreatureResponse.model_validate(c) for c in creatures]

@router.post("", response_model=CreatureResponse, status_code=status.HTTP_201_CREATED)
async def create_creature(
    creature_data: CreatureCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new creature and add it to an encounter."""
    # Verify the encounter exists and belongs to the user
    encounter = db.query(Encounter).filter(
        Encounter.id == creature_data.encounter_id,
        Encounter.user_id == current_user.id
    ).first()
    
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found"
        )
    
    # Create creature
    db_creature = Creature(
        encounter_id=creature_data.encounter_id,
        name=creature_data.name,
        initiative=creature_data.initiative,
        creature_type=creature_data.creature_type,
        image_url=creature_data.image_url
    )
    
    db.add(db_creature)
    db.commit()
    db.refresh(db_creature)
    
    return CreatureResponse.model_validate(db_creature)

@router.get("/{creature_id}", response_model=CreatureResponse)
async def get_creature(
    creature_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific creature by ID."""
    creature = db.query(Creature).join(Encounter).filter(
        Creature.id == creature_id,
        Encounter.user_id == current_user.id
    ).first()
    
    if not creature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creature not found"
        )
    
    return CreatureResponse.model_validate(creature)

@router.put("/{creature_id}", response_model=CreatureResponse)
async def update_creature(
    creature_id: uuid.UUID,
    creature_data: CreatureUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a creature by ID."""
    # Get creature and verify ownership
    creature = db.query(Creature).join(Encounter).filter(
        Creature.id == creature_id,
        Encounter.user_id == current_user.id
    ).first()
    
    if not creature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creature not found"
        )
    
    # Update fields if provided
    if creature_data.name is not None:
        creature.name = creature_data.name
    if creature_data.initiative is not None:
        creature.initiative = creature_data.initiative
    if creature_data.creature_type is not None:
        creature.creature_type = creature_data.creature_type
    if creature_data.image_url is not None:
        creature.image_url = creature_data.image_url
    
    db.commit()
    db.refresh(creature)
    
    return CreatureResponse.model_validate(creature)

@router.delete("/{creature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_creature(
    creature_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a creature."""
    # Get creature and verify ownership
    creature = db.query(Creature).join(Encounter).filter(
        Creature.id == creature_id,
        Encounter.user_id == current_user.id
    ).first()
    
    if not creature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creature not found"
        )
    
    db.delete(creature)
    db.commit()
    
    return {"message": "Creature deleted successfully"}