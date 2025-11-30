from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid
from .enums import CreatureType

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    confirm_password: str

class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Creature Schemas
class CreatureBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    initiative: int = Field(..., ge=0, le=100)
    creature_type: CreatureType
    image_url: Optional[str] = None

class CreatureCreateNested(CreatureBase):
    """Schema for creating creatures nested within encounters (no encounter_id needed)."""
    pass

class CreatureCreate(CreatureBase):
    encounter_id: uuid.UUID

class CreatureUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    initiative: Optional[int] = Field(None, ge=0, le=100)
    creature_type: Optional[CreatureType] = None
    image_url: Optional[str] = None

class CreatureResponse(CreatureBase):
    id: uuid.UUID
    encounter_id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Encounter Schemas
class EncounterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    background_image: Optional[str] = None

class EncounterCreate(EncounterBase):
    creatures: List[CreatureCreateNested] = []

class EncounterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    background_image: Optional[str] = None

class EncounterRoundUpdate(BaseModel):
    round_number: int = Field(..., ge=1)

class EncounterResponse(EncounterBase):
    id: uuid.UUID
    user_id: uuid.UUID
    round_number: int
    created_at: datetime
    updated_at: datetime
    creatures: List[CreatureResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class EncounterSummary(EncounterBase):
    id: uuid.UUID
    created_at: datetime
    creature_count: int
    
    model_config = ConfigDict(from_attributes=True)

# Preset Schemas
class PresetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    background_image: Optional[str] = None

class PresetCreate(PresetBase):
    creatures: List[CreatureCreateNested] = []

class PresetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    background_image: Optional[str] = None
    creatures: Optional[List[CreatureCreateNested]] = None

class PresetResponse(PresetBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    creatures: List[CreatureCreateNested] = []  # Using CreatureCreateNested since presets are templates without encounters
    
    model_config = ConfigDict(from_attributes=True)

class PresetSummary(PresetBase):
    id: uuid.UUID
    created_at: datetime
    creature_count: int
    
    model_config = ConfigDict(from_attributes=True)

# File Upload Schemas
class FileUpload(BaseModel):
    filename: str
    url: str

# Error Schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None