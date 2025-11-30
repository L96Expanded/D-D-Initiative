"""Test database functionality."""
import pytest
from app.models.database import get_db, Base
from sqlalchemy.orm import Session


class TestDatabase:
    """Test database operations."""
    
    def test_get_db_session(self, test_db_session):
        """Test database session creation."""
        assert test_db_session is not None
        assert isinstance(test_db_session, Session)
        
    def test_base_metadata_exists(self):
        """Test that Base metadata is configured."""
        assert Base.metadata is not None
        assert len(Base.metadata.tables) > 0
        
    def test_database_tables_include_users(self):
        """Test that users table exists in metadata."""
        assert "users" in Base.metadata.tables
        
    def test_database_tables_include_encounters(self):
        """Test that encounters table exists in metadata."""
        assert "encounters" in Base.metadata.tables
        
    def test_database_tables_include_creatures(self):
        """Test that creatures table exists in metadata."""
        assert "creatures" in Base.metadata.tables
