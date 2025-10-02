from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.models import User
from app.models.schemas import UserResponse, ErrorResponse
from app.utils.dependencies import get_current_user

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get user profile."""
    return UserResponse.model_validate(current_user)

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile."""
    # For now, just return the current user
    # This can be expanded later to allow profile updates
    return UserResponse.model_validate(current_user)

@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account."""
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}