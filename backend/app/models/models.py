from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .database import Base
from .enums import CreatureType
from .creature_image import CreatureImageDB

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    encounters = relationship("Encounter", back_populates="user", cascade="all, delete-orphan")
    presets = relationship("Preset", back_populates="user", cascade="all, delete-orphan")

class Encounter(Base):
    __tablename__ = "encounters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    background_image = Column(String(255), nullable=True)
    round_number = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="encounters")
    creatures = relationship("Creature", back_populates="encounter", cascade="all, delete-orphan")

class Preset(Base):
    __tablename__ = "presets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    background_image = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="presets")
    preset_creatures = relationship("PresetCreature", back_populates="preset", cascade="all, delete-orphan")

class Creature(Base):
    __tablename__ = "creatures"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    initiative = Column(Integer, nullable=False)
    creature_type = Column(Enum(CreatureType), nullable=False)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    encounter = relationship("Encounter", back_populates="creatures")

class PresetCreature(Base):
    __tablename__ = "preset_creatures"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    preset_id = Column(UUID(as_uuid=True), ForeignKey("presets.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    initiative = Column(Integer, nullable=False)
    creature_type = Column(Enum(CreatureType), nullable=False)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    preset = relationship("Preset", back_populates="preset_creatures")