"""Test user endpoints."""
import pytest
from fastapi import status


class TestUserEndpoints:
    """Test user-related endpoints."""
    
    def test_get_current_user_profile(self, client, authenticated_headers):
        """Test getting current user profile."""
        response = client.get("/users/profile", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "password_hash" not in data  # Should not expose password hash
        
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication."""
        response = client.get("/users/profile")
        
        # Accept both 401 and 403 (varies between environments)
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        
    def test_update_user_profile(self, client, authenticated_headers):
        """Test updating user profile."""
        response = client.put("/users/profile", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "email" in data
        
    def test_delete_user_account(self, client, authenticated_headers):
        """Test deleting user account."""
        response = client.delete("/users/account", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
