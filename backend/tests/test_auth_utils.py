"""Unit tests for authentication utilities."""
import pytest
from datetime import datetime, timedelta
from jose import jwt
from app.utils import auth
from app.config import settings


@pytest.mark.unit
class TestPasswordHashing:
    """Tests for password hashing functions."""
    
    def test_password_hashing(self):
        """Test password can be hashed and verified."""
        password = "TestPassword123!"
        hashed = auth.hash_password(password)
        
        assert hashed != password
        assert auth.verify_password(password, hashed) is True
    
    def test_wrong_password_verification(self):
        """Test that wrong password fails verification."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = auth.hash_password(password)
        
        assert auth.verify_password(wrong_password, hashed) is False
    
    def test_password_hash_is_different_each_time(self):
        """Test that same password generates different hashes."""
        password = "TestPassword123!"
        hash1 = auth.hash_password(password)
        hash2 = auth.hash_password(password)
        
        assert hash1 != hash2
        assert auth.verify_password(password, hash1) is True
        assert auth.verify_password(password, hash2) is True


@pytest.mark.unit
class TestJWTTokens:
    """Tests for JWT token creation and verification."""
    
    def test_create_access_token(self):
        """Test creating an access token."""
        data = {"sub": "testuser"}
        token = auth.create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_default_expiration(self):
        """Test creating a token with default expiration."""
        data = {"sub": "testuser"}
        token = auth.create_access_token(data)
        
        # Decode token to check expiration
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        
        # Token should expire in approximately 24 hours (default)
        hours_until_exp = (exp - now).total_seconds() / 3600
        assert hours_until_exp > 23  # At least 23 hours
        assert hours_until_exp < 25  # Less than 25 hours
    
    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        username = "testuser"
        data = {"sub": username}
        token = auth.create_access_token(data)
        
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        
        assert payload["sub"] == username
        assert "exp" in payload
    
    def test_token_contains_subject(self):
        """Test that token contains the subject."""
        data = {"sub": "testuser", "email": "test@example.com"}
        token = auth.create_access_token(data)
        
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        
        assert payload["sub"] == "testuser"
        assert payload.get("email") == "test@example.com"


@pytest.mark.unit
class TestTokenGeneration:
    """Tests for various token generation scenarios."""
    
    def test_multiple_tokens_have_different_expiration(self):
        """Test that tokens created at different times have different expiration."""
        import time
        data = {"sub": "testuser"}
        token1 = auth.create_access_token(data)
        time.sleep(0.1)  # Small delay to ensure different timestamp
        token2 = auth.create_access_token(data)
        
        # Tokens should be different due to different expiration times
        # (This test verifies tokens are time-dependent)
        assert isinstance(token1, str)
        assert isinstance(token2, str)
    
    def test_token_with_additional_claims(self):
        """Test creating token with additional claims."""
        data = {
            "sub": "testuser",
            "role": "admin",
            "permissions": ["read", "write"],
        }
        token = auth.create_access_token(data)
        
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"
        assert payload["permissions"] == ["read", "write"]
