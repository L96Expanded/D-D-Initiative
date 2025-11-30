from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.models.database import get_db
from app.models.models import User, Encounter, Creature
from app.models.schemas import (
    EncounterCreate, EncounterUpdate, EncounterRoundUpdate, EncounterResponse, 
    EncounterSummary, CreatureCreate, CreatureUpdate, CreatureResponse, ErrorResponse
)
from app.utils.dependencies import get_current_user
import uuid

router = APIRouter()

@router.get("", response_model=List[EncounterSummary])
async def get_user_encounters(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all encounters for the current user."""
    encounters = db.query(
        Encounter.id,
        Encounter.name,
        Encounter.background_image,
        Encounter.created_at,
        func.count(Creature.id).label("creature_count")
    ).outerjoin(Creature).filter(
        Encounter.user_id == current_user.id
    ).group_by(
        Encounter.id, Encounter.name, Encounter.background_image, Encounter.created_at
    ).order_by(Encounter.created_at.desc()).all()
    
    return [
        EncounterSummary(
            id=enc.id,
            name=enc.name,
            background_image=enc.background_image,
            created_at=enc.created_at,
            creature_count=enc.creature_count
        )
        for enc in encounters
    ]

@router.post("", response_model=EncounterResponse, status_code=status.HTTP_201_CREATED)
async def create_encounter(
    encounter_data: EncounterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new encounter."""
    # Create encounter
    db_encounter = Encounter(
        user_id=current_user.id,
        name=encounter_data.name,
        background_image=encounter_data.background_image
    )
    
    db.add(db_encounter)
    db.flush()  # Get the ID without committing
    
    # Create creatures
    for creature_data in encounter_data.creatures:
        db_creature = Creature(
            encounter_id=db_encounter.id,
            name=creature_data.name,
            initiative=creature_data.initiative,
            creature_type=creature_data.creature_type,
            image_url=creature_data.image_url
        )
        db.add(db_creature)
    
    db.commit()
    db.refresh(db_encounter)
    
    return EncounterResponse.model_validate(db_encounter)

@router.get("/{encounter_id}", response_model=EncounterResponse)
async def get_encounter(
    encounter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific encounter."""
    encounter = db.query(Encounter).filter(
        Encounter.id == encounter_id,
        Encounter.user_id == current_user.id
    ).first()
    
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found"
        )
    
    return EncounterResponse.model_validate(encounter)

@router.put("/{encounter_id}", response_model=EncounterResponse)
async def update_encounter(
    encounter_id: uuid.UUID,
    encounter_data: EncounterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an encounter."""
    encounter = db.query(Encounter).filter(
        Encounter.id == encounter_id,
        Encounter.user_id == current_user.id
    ).first()
    
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found"
        )
    
    # Update fields
    if encounter_data.name is not None:
        encounter.name = encounter_data.name
    if encounter_data.background_image is not None:
        encounter.background_image = encounter_data.background_image
    
    db.commit()
    db.refresh(encounter)
    
    return EncounterResponse.model_validate(encounter)

@router.patch("/{encounter_id}/round", response_model=EncounterResponse)
async def update_encounter_round(
    encounter_id: uuid.UUID,
    round_data: EncounterRoundUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the round number of an encounter."""
    encounter = db.query(Encounter).filter(
        Encounter.id == encounter_id,
        Encounter.user_id == current_user.id
    ).first()
    
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found"
        )
    
    encounter.round_number = round_data.round_number
    db.commit()
    db.refresh(encounter)
    
    return EncounterResponse.model_validate(encounter)

@router.delete("/{encounter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_encounter(
    encounter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an encounter."""
    encounter = db.query(Encounter).filter(
        Encounter.id == encounter_id,
        Encounter.user_id == current_user.id
    ).first()
    
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found"
        )
    
    db.delete(encounter)
    db.commit()
    
    return {"message": "Encounter deleted successfully"}

@router.get("/{encounter_id}/creatures", response_model=List[CreatureResponse])
async def get_encounter_creatures(
    encounter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get creatures for a specific encounter."""
    encounter = db.query(Encounter).filter(
        Encounter.id == encounter_id,
        Encounter.user_id == current_user.id
    ).first()
    
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found"
        )
    
    # Return creatures sorted by initiative (highest first)
    creatures = db.query(Creature).filter(
        Creature.encounter_id == encounter_id
    ).order_by(Creature.initiative.desc()).all()
    
    return [CreatureResponse.model_validate(creature) for creature in creatures]

@router.get("/{encounter_id}/creatures/{creature_id}", response_model=CreatureResponse)
async def get_creature(
    encounter_id: uuid.UUID,
    creature_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific creature from an encounter."""
    # Verify encounter ownership and creature belongs to encounter
    creature = db.query(Creature).join(Encounter).filter(
        Creature.id == creature_id,
        Creature.encounter_id == encounter_id,
        Encounter.user_id == current_user.id
    ).first()
    
    if not creature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creature not found"
        )
    
    return CreatureResponse.model_validate(creature)

@router.post("/{encounter_id}/creatures", response_model=CreatureResponse, status_code=status.HTTP_201_CREATED)
async def add_creature_to_encounter(
    encounter_id: uuid.UUID,
    creature_data: CreatureCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a creature to an encounter."""
    encounter = db.query(Encounter).filter(
        Encounter.id == encounter_id,
        Encounter.user_id == current_user.id
    ).first()

    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found"
        )

    db_creature = Creature(
        encounter_id=encounter_id,
        name=creature_data.name,
        initiative=creature_data.initiative,
        creature_type=creature_data.creature_type,
        image_url=creature_data.image_url
    )

    db.add(db_creature)
    db.commit()
    db.refresh(db_creature)

    return CreatureResponse.model_validate(db_creature)

@router.put("/{encounter_id}/creatures/{creature_id}", response_model=CreatureResponse)
async def update_creature(
    encounter_id: uuid.UUID,
    creature_id: uuid.UUID,
    creature_data: CreatureUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a creature in an encounter."""
    # Verify encounter ownership and creature belongs to encounter
    creature = db.query(Creature).join(Encounter).filter(
        Creature.id == creature_id,
        Creature.encounter_id == encounter_id,
        Encounter.user_id == current_user.id
    ).first()
    
    if not creature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creature not found"
        )
    
    # Update fields
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

@router.delete("/{encounter_id}/creatures/{creature_id}", status_code=status.HTTP_200_OK)
async def delete_creature(
    encounter_id: uuid.UUID,
    creature_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a creature from an encounter."""
    # Verify encounter ownership and creature belongs to encounter
    creature = db.query(Creature).join(Encounter).filter(
        Creature.id == creature_id,
        Creature.encounter_id == encounter_id,
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