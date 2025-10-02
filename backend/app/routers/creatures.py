from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.models import User, Creature, Encounter
from app.models.schemas import CreatureUpdate, CreatureResponse, ErrorResponse
from app.utils.dependencies import get_current_user
import uuid

router = APIRouter()

@router.put("/{creature_id}", response_model=CreatureResponse)
async def update_creature(
    creature_id: uuid.UUID,
    creature_data: CreatureUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a creature."""
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