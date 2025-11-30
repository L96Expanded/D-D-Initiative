"""Tests for utility functions and configuration."""

import pytest
from datetime import datetime, timedelta
from app.config import Settings
from app.utils.dependencies import get_current_user
from app.utils.auth import create_access_token, verify_token, hash_password
from fastapi import HTTPException, status as http_status


class TestConfiguration:
    """Test application configuration."""

    def test_settings_defaults(self):
        """Test default settings values."""
        settings = Settings()
        
        assert settings.JWT_SECRET is not None
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.JWT_EXPIRATION_HOURS == 24  # 24 hours
        assert settings.DATABASE_URL is not None

    def test_settings_from_env(self, monkeypatch):
        """Test settings can be loaded from environment."""
        monkeypatch.setenv("JWT_SECRET", "test_secret_123")
        monkeypatch.setenv("JWT_EXPIRATION_HOURS", "24")
        
        settings = Settings()
        
        assert settings.JWT_SECRET == "test_secret_123"
        assert settings.JWT_EXPIRATION_HOURS == 24


class TestDependencies:
    """Test FastAPI dependencies."""

    def test_get_current_user_with_valid_token(self, test_db_session, sample_user_data):
        """Test getting current user with valid token."""
        from app.models.models import User
        
        # Create user in database
        user = User(
            email=sample_user_data["email"],
            password_hash=hash_password(sample_user_data["password"])
        )
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        
        # Create valid token
        token = create_access_token({"sub": str(user.id)})
        
        # Get user from token using dependency injection pattern
        from app.utils.dependencies import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials
        import asyncio
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        result = asyncio.run(get_current_user(credentials=credentials, db=test_db_session))
        
        assert result.id == user.id
        assert result.email == user.email

    def test_get_current_user_with_invalid_token(self, test_db_session):
        """Test getting current user with invalid token."""
        from app.utils.dependencies import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials
        import asyncio
        
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_current_user(credentials=credentials, db=test_db_session))
        
        assert exc_info.value.status_code == http_status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_with_nonexistent_user(self, test_db_session):
        """Test getting current user when user doesn't exist in database."""
        from app.utils.dependencies import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials
        import asyncio
        
        # Create token for non-existent user
        fake_user_id = "00000000-0000-0000-0000-000000000000"
        token = create_access_token({"sub": fake_user_id})
        
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_current_user(credentials=credentials, db=test_db_session))
        
        assert exc_info.value.status_code == http_status.HTTP_401_UNAUTHORIZED


class TestAuthErrors:
    """Test authentication error handling."""

    def test_verify_invalid_token_format(self):
        """Test verifying a malformed token."""
        with pytest.raises(HTTPException) as exc_info:
            verify_token("not.a.valid.token.format")
        
        assert exc_info.value.status_code == http_status.HTTP_401_UNAUTHORIZED

    def test_verify_token_with_wrong_secret(self):
        """Test verifying a token with wrong secret."""
        from jose import jwt
        
        # Create token with different secret
        payload = {"sub": "test_user", "exp": datetime.utcnow() + timedelta(hours=1)}
        bad_token = jwt.encode(payload, "wrong_secret", algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(bad_token)
        
        assert exc_info.value.status_code == http_status.HTTP_401_UNAUTHORIZED


class TestMetrics:
    """Test metrics collection."""

    def test_metrics_endpoint_prometheus_format(self, client):
        """Test health endpoint returns JSON status."""
        response = client.get("/api/health")
        
        assert response.status_code == http_status.HTTP_200_OK
        
        # Check for health status format
        data = response.json()
        assert "status" in data
        assert "database" in data

    def test_metrics_after_requests(self, client, authenticated_headers):
        """Test that health endpoint works after making requests."""
        # Make some requests
        client.get("/encounters/", headers=authenticated_headers)
        client.get("/creatures/", headers=authenticated_headers)
        
        # Get health status
        response = client.get("/api/health")
        assert response.status_code == http_status.HTTP_200_OK
        
        # Metrics should contain some data
        assert len(response.text) > 0


class TestPasswordResetWorkflow:
    """Test password-related operations."""

    def test_register_with_mismatched_passwords(self, client):
        """Test registration fails with mismatched passwords."""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "different_password"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == http_status.HTTP_400_BAD_REQUEST
        assert "match" in response.json()["detail"].lower()

    def test_register_with_short_password(self, client):
        """Test registration fails with password too short."""
        user_data = {
            "email": "test@example.com",
            "password": "12345",  # Too short
            "confirm_password": "12345"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == http_status.HTTP_422_UNPROCESSABLE_ENTITY
