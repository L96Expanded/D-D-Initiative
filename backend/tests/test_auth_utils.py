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
        hashed = auth.get_password_hash(password)
        
        assert hashed != password
        assert auth.verify_password(password, hashed) is True
    
    def test_wrong_password_verification(self):
        """Test that wrong password fails verification."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = auth.get_password_hash(password)
        
        assert auth.verify_password(wrong_password, hashed) is False
    
    def test_password_hash_is_different_each_time(self):
        """Test that same password generates different hashes."""
        password = "TestPassword123!"
        hash1 = auth.get_password_hash(password)
        hash2 = auth.get_password_hash(password)
        
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
    
    def test_create_access_token_with_expiration(self):
        """Test creating a token with custom expiration."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=15)
        token = auth.create_access_token(data, expires_delta=expires_delta)
        
        # Decode token to check expiration
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        
        # Token should expire in approximately 15 minutes
        assert (exp - now).total_seconds() > 840  # 14 minutes
        assert (exp - now).total_seconds() < 960  # 16 minutes
    
    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        username = "testuser"
        data = {"sub": username}
        token = auth.create_access_token(data)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert payload["sub"] == username
        assert "exp" in payload
    
    def test_token_contains_subject(self):
        """Test that token contains the subject."""
        data = {"sub": "testuser", "email": "test@example.com"}
        token = auth.create_access_token(data)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert payload["sub"] == "testuser"
        assert payload.get("email") == "test@example.com"


@pytest.mark.unit
class TestAuthUtils:
    """Tests for authentication utility functions."""
    
    def test_username_validation(self):
        """Test username validation logic."""
        # Valid usernames
        assert auth.validate_username("user123") is True
        assert auth.validate_username("test_user") is True
        assert auth.validate_username("TestUser") is True
        
        # Invalid usernames
        assert auth.validate_username("ab") is False  # Too short
        assert auth.validate_username("user@name") is False  # Special chars
        assert auth.validate_username("") is False  # Empty
    
    def test_email_validation(self):
        """Test email validation logic."""
        # Valid emails
        assert auth.validate_email("test@example.com") is True
        assert auth.validate_email("user.name@domain.co.uk") is True
        
        # Invalid emails
        assert auth.validate_email("invalid-email") is False
        assert auth.validate_email("@example.com") is False
        assert auth.validate_email("test@") is False
        assert auth.validate_email("") is False
    
    def test_password_strength_validation(self):
        """Test password strength requirements."""
        # Strong passwords
        assert auth.validate_password_strength("TestPass123!") is True
        assert auth.validate_password_strength("MyP@ssw0rd") is True
        
        # Weak passwords
        assert auth.validate_password_strength("short") is False  # Too short
        assert auth.validate_password_strength("alllowercase123") is False  # No uppercase
        assert auth.validate_password_strength("ALLUPPERCASE123") is False  # No lowercase
        assert auth.validate_password_strength("NoNumbers!") is False  # No numbers
        assert auth.validate_password_strength("") is False  # Empty


@pytest.mark.unit
class TestTokenGeneration:
    """Tests for various token generation scenarios."""
    
    def test_multiple_tokens_are_different(self):
        """Test that multiple tokens for same user are different."""
        data = {"sub": "testuser"}
        token1 = auth.create_access_token(data)
        token2 = auth.create_access_token(data)
        
        assert token1 != token2
    
    def test_token_with_additional_claims(self):
        """Test creating token with additional claims."""
        data = {
            "sub": "testuser",
            "role": "admin",
            "permissions": ["read", "write"],
        }
        token = auth.create_access_token(data)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"
        assert payload["permissions"] == ["read", "write"]
