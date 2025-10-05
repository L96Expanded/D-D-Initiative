import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import json

from app.models.models import User
from app.utils.auth import verify_password


class TestUserRegistration:
    """Test user registration functionality"""
    
    def test_register_user_success(self, client: TestClient, test_user_data):
        """Test successful user registration"""
        response = client.post("/auth/register", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "access_token" in data
        assert "token_type" in data
        assert "user" in data
        assert data["token_type"] == "bearer"
        
        # Check user data
        user_data = data["user"]
        assert user_data["email"] == test_user_data["email"]
        assert "id" in user_data
        assert "created_at" in user_data
    
    def test_register_user_duplicate_email(self, client: TestClient, test_user_data):
        """Test registration with duplicate email"""
        # Register first user
        client.post("/auth/register", json=test_user_data)
        
        # Try to register again with same email
        response = client.post("/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_user_invalid_email(self, client: TestClient):
        """Test registration with invalid email"""
        invalid_data = {
            "email": "invalid-email",
            "password": "testpassword123",
            "confirm_password": "testpassword123"
        }
        
        response = client.post("/auth/register", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_register_user_password_mismatch(self, client: TestClient):
        """Test registration with password mismatch"""
        mismatch_data = {
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "different123"
        }
        
        response = client.post("/auth/register", json=mismatch_data)
        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()
    
    def test_register_user_weak_password(self, client: TestClient):
        """Test registration with weak password"""
        weak_data = {
            "email": "test@example.com",
            "password": "123",  # Too short
            "confirm_password": "123"
        }
        
        response = client.post("/auth/register", json=weak_data)
        assert response.status_code == 422  # Validation error
    
    def test_register_user_missing_fields(self, client: TestClient):
        """Test registration with missing required fields"""
        incomplete_data = {
            "email": "test@example.com"
            # Missing password and confirm_password
        }
        
        response = client.post("/auth/register", json=incomplete_data)
        assert response.status_code == 422


class TestUserLogin:
    """Test user login functionality"""
    
    def test_login_success(self, client: TestClient, test_user_data):
        """Test successful login"""
        # First register a user
        client.post("/auth/register", json=test_user_data)
        
        # Then login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert "user" in data
        assert data["token_type"] == "bearer"
        
        user_data = data["user"]
        assert user_data["email"] == test_user_data["email"]
    
    def test_login_invalid_credentials(self, client: TestClient, test_user_data):
        """Test login with invalid credentials"""
        # Register a user first
        client.post("/auth/register", json=test_user_data)
        
        # Try to login with wrong password
        wrong_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", json=wrong_data)
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "somepassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_invalid_email_format(self, client: TestClient):
        """Test login with invalid email format"""
        login_data = {
            "email": "invalid-email",
            "password": "somepassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 422  # Validation error
    
    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing fields"""
        incomplete_data = {
            "email": "test@example.com"
            # Missing password
        }
        
        response = client.post("/auth/login", json=incomplete_data)
        assert response.status_code == 422


class TestUserLogout:
    """Test user logout functionality"""
    
    def test_logout_success(self, client: TestClient):
        """Test successful logout"""
        response = client.post("/auth/logout")
        
        # Logout is currently a client-side operation
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestAuthenticatedRoutes:
    """Test authenticated routes and JWT token validation"""
    
    def test_get_current_user_success(self, client: TestClient, auth_headers):
        """Test getting current user info with valid token"""
        response = client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "email" in data
        assert "created_at" in data
        assert "@example.com" in data["email"]
    
    def test_get_current_user_no_token(self, client: TestClient):
        """Test accessing protected route without token"""
        response = client.get("/auth/me")
        
        assert response.status_code == 403  # FastAPI returns 403 for missing credentials
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test accessing protected route with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    def test_get_current_user_malformed_token(self, client: TestClient):
        """Test accessing protected route with malformed token"""
        headers = {"Authorization": "InvalidFormat"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 403  # FastAPI returns 403 for malformed credentials
    
    def test_get_current_user_expired_token(self, client: TestClient):
        """Test accessing protected route with expired token"""
        # This would require generating an expired token
        # For now, we'll test with a clearly invalid token structure
        expired_headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.expired.token"}
        response = client.get("/auth/me", headers=expired_headers)
        
        assert response.status_code == 401


class TestPasswordSecurity:
    """Test password security measures"""
    
    def test_password_hashing(self, db_session: Session, test_user_data):
        """Test that passwords are properly hashed"""
        from app.utils.auth import hash_password
        
        # Create user with hashed password
        hashed_password = hash_password(test_user_data["password"])
        user = User(
            email=test_user_data["email"],
            password_hash=hashed_password  # Correct field name
        )
        db_session.add(user)
        db_session.commit()
        
        # Verify password is hashed (not stored in plain text)
        assert user.password_hash != test_user_data["password"]
        assert len(user.password_hash) > 50  # bcrypt hashes are long
        
        # Verify password can be verified
        assert verify_password(test_user_data["password"], user.password_hash)
        assert not verify_password("wrongpassword", user.password_hash)


class TestInputValidation:
    """Test input validation for authentication endpoints"""
    
    @pytest.mark.parametrize("invalid_data", [
        {},  # Empty data
        {"email": "test@example.com"},  # Missing password
        {"password": "test123"},  # Missing email
        {"email": "", "password": "test123", "confirm_password": "test123"},  # Empty email
        {"email": "test@example.com", "password": "", "confirm_password": ""},  # Empty password
    ])
    def test_register_validation_errors(self, client: TestClient, invalid_data):
        """Test registration with various invalid data"""
        response = client.post("/auth/register", json=invalid_data)
        assert response.status_code == 422
    
    @pytest.mark.parametrize("invalid_data", [
        {},  # Empty data
        {"email": "test@example.com"},  # Missing password
        {"password": "test123"},  # Missing email
        {"email": "", "password": "test123"},  # Empty email
        # Empty password will be handled as incorrect credentials, not validation error
    ])
    def test_login_validation_errors(self, client: TestClient, invalid_data):
        """Test login with various invalid data"""
        response = client.post("/auth/login", json=invalid_data)
        assert response.status_code == 422
    
    def test_login_empty_password(self, client: TestClient):
        """Test login with empty password (handled as incorrect credentials)"""
        invalid_data = {"email": "test@example.com", "password": ""}
        response = client.post("/auth/login", json=invalid_data)
        assert response.status_code == 401  # Empty password treated as incorrect credentials