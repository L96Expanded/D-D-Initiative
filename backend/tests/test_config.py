"""Test configuration and environment loading."""
import pytest
import os
from app.config import Settings


class TestConfiguration:
    """Test configuration settings."""
    
    def test_settings_load_from_env(self, monkeypatch):
        """Test that settings load from environment variables."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/testdb")
        monkeypatch.setenv("JWT_SECRET", "test_secret_for_environment")
        monkeypatch.setenv("JWT_ALGORITHM", "HS512")
        monkeypatch.setenv("JWT_EXPIRATION_HOURS", "48")
        
        settings = Settings()
        
        assert settings.DATABASE_URL == "postgresql://test:test@localhost/testdb"
        assert settings.JWT_SECRET == "test_secret_for_environment"
        assert settings.JWT_ALGORITHM == "HS512"
        assert settings.JWT_EXPIRATION_HOURS == 48
        
    def test_allowed_hosts_settings(self):
        """Test allowed hosts settings."""
        settings = Settings()
        
        assert hasattr(settings, "ALLOWED_HOSTS")
        assert isinstance(settings.ALLOWED_HOSTS, list)
        
    def test_database_url_format(self):
        """Test database URL format validation."""
        settings = Settings()
        
        # Should have a valid database URL
        assert settings.DATABASE_URL is not None
        assert len(settings.DATABASE_URL) > 0
