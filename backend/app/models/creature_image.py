from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base

class CreatureImageDB(Base):
    """Database model for curated D&D creature images."""
    __tablename__ = "creature_images"

    id = Column(Integer, primary_key=True, index=True)
    creature_name = Column(String(255), index=True, nullable=False)
    creature_type = Column(String(50), index=True, default="other")  # player, enemy, ally, other
    image_url = Column(Text, nullable=False)
    image_source = Column(String(255))  # Attribution/source info
    image_license = Column(String(100))  # License type (CC, Public Domain, etc.)
    description = Column(Text)  # Brief description of the image
    tags = Column(Text)  # Comma-separated tags for search
    is_active = Column(Boolean, default=True)  # Allow disabling images
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<CreatureImageDB(name='{self.creature_name}', type='{self.creature_type}')>"