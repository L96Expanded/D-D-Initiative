import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import User
from app.utils.auth import hash_password, create_access_token


class TestUserProfile:
    """Test user profile endpoints."""

    def test_get_user_profile_success(self, client: TestClient, auth_headers):
        """Test successful user profile retrieval."""
        response = client.get("/users/profile", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "@example.com" in data["email"]

    def test_get_user_profile_unauthorized(self, client: TestClient):
        """Test profile retrieval without authentication."""
        response = client.get("/users/profile")
        
        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]

    def test_get_user_profile_invalid_token(self, client: TestClient):
        """Test profile retrieval with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/users/profile", headers=headers)
        
        assert response.status_code == 401  # Unauthorized for invalid token

    def test_update_user_profile_success(self, client: TestClient, auth_headers):
        """Test successful user profile update."""
        response = client.put("/users/profile", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data

    def test_update_user_profile_unauthorized(self, client: TestClient):
        """Test profile update without authentication."""
        response = client.put("/users/profile")
        
        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]


class TestAccountDeletion:
    """Test account deletion functionality."""

    def test_delete_account_success(self, client: TestClient, auth_headers, db_session: Session):
        """Test successful account deletion."""
        # Get the current user ID from the token to verify deletion
        profile_response = client.get("/users/profile", headers=auth_headers)
        user_id_str = profile_response.json()["id"]
        user_id = uuid.UUID(user_id_str)  # Convert string to UUID
        
        # Delete the account
        response = client.delete("/users/account", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Verify user is deleted from database
        user = db_session.query(User).filter(User.id == user_id).first()
        assert user is None

    def test_delete_account_unauthorized(self, client: TestClient):
        """Test account deletion without authentication."""
        response = client.delete("/users/account")
        
        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]

    def test_delete_account_invalid_token(self, client: TestClient):
        """Test account deletion with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.delete("/users/account", headers=headers)
        
        assert response.status_code == 401  # Unauthorized for invalid token


class TestUserProfileValidation:
    """Test user profile data validation and edge cases."""

    def test_profile_with_deleted_user_token(self, client: TestClient, db_session: Session):
        """Test accessing profile with token for deleted user."""
        # Create a user
        test_user = User(
            email="deleted@example.com",
            password_hash=hash_password("testpass123")
        )
        db_session.add(test_user)
        db_session.commit()
        
        # Create token for the user
        token = create_access_token({"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Delete the user directly from database
        db_session.delete(test_user)
        db_session.commit()
        
        # Try to access profile with token for deleted user
        response = client.get("/users/profile", headers=headers)
        
        assert response.status_code == 401
        assert "User not found" in response.json()["detail"]

    def test_profile_with_malformed_user_id_in_token(self, client: TestClient):
        """Test accessing profile with malformed user ID in token."""
        # Create token with invalid UUID format
        token = create_access_token({"sub": "not-a-valid-uuid"})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/users/profile", headers=headers)
        
        assert response.status_code == 401
        assert "Invalid user ID format" in response.json()["detail"]

    def test_profile_with_missing_user_id_in_token(self, client: TestClient):
        """Test accessing profile with token missing user ID."""
        # Create token without sub claim
        token = create_access_token({"other": "data"})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/users/profile", headers=headers)
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]


class TestUserRouterEdgeCases:
    """Test edge cases and error conditions in user router."""

    def test_update_profile_with_deleted_user(self, client: TestClient, db_session: Session):
        """Test updating profile for deleted user."""
        # Create a user
        test_user = User(
            email="willbedeleted@example.com",
            password_hash=hash_password("testpass123")
        )
        db_session.add(test_user)
        db_session.commit()
        
        # Create token for the user
        token = create_access_token({"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Delete the user directly from database
        db_session.delete(test_user)
        db_session.commit()
        
        # Try to update profile for deleted user
        response = client.put("/users/profile", headers=headers)
        
        assert response.status_code == 401
        assert "User not found" in response.json()["detail"]

    def test_delete_account_twice(self, client: TestClient, auth_headers, db_session: Session):
        """Test deleting account twice (idempotent behavior)."""
        # First deletion should succeed
        response1 = client.delete("/users/account", headers=auth_headers)
        assert response1.status_code == 204
        
        # Second deletion with same token should fail (user not found)
        response2 = client.delete("/users/account", headers=auth_headers)
        assert response2.status_code == 401
        assert "User not found" in response2.json()["detail"]

    def test_all_user_endpoints_comprehensive(self, client: TestClient, auth_headers):
        """Test all user endpoints in sequence to ensure comprehensive coverage."""
        # Test profile retrieval
        profile_response = client.get("/users/profile", headers=auth_headers)
        assert profile_response.status_code == 200
        
        # Test profile update
        update_response = client.put("/users/profile", headers=auth_headers)
        assert update_response.status_code == 200
        
        # Test account deletion (should be last as it deletes the user)
        delete_response = client.delete("/users/account", headers=auth_headers)
        assert delete_response.status_code == 204


class TestDatabaseSessionHandling:
    """Test database session handling in user operations."""

    def test_profile_operations_with_db_session(self, client: TestClient, auth_headers, db_session: Session):
        """Test that profile operations properly handle database sessions."""
        # Test profile retrieval
        response = client.get("/users/profile", headers=auth_headers)
        assert response.status_code == 200
        
        # Ensure database session is still valid
        user_count = db_session.query(User).count()
        assert user_count >= 1
        
        # Test profile update
        response = client.put("/users/profile", headers=auth_headers)
        assert response.status_code == 200
        
        # Ensure database session is still valid after update
        user_count_after = db_session.query(User).count()
        assert user_count_after >= 1