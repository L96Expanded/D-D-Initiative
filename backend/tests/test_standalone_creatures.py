import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid

from app.models.models import Creature, Encounter, User
from app.models.enums import CreatureType


class TestStandaloneCreatureOperations:
    """Test standalone creature endpoints (not through encounters)"""
    
    def test_update_creature_success(self, client: TestClient, auth_headers, test_creature):
        """Test updating a creature directly"""
        creature_id = test_creature["id"]
        update_data = {
            "name": "Updated Dragon",
            "initiative": 25,
            "creature_type": "enemy",
            "image_url": "https://example.com/updated_dragon.jpg"
        }
        
        response = client.put(f"/creatures/{creature_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == update_data["name"]
        assert data["initiative"] == update_data["initiative"]
        assert data["creature_type"] == update_data["creature_type"]
        assert data["image_url"] == update_data["image_url"]
        assert data["id"] == str(creature_id)  # API returns string UUID
    
    def test_update_creature_partial(self, client: TestClient, auth_headers, test_creature):
        """Test partial creature update"""
        creature_id = test_creature["id"]
        update_data = {
            "name": "Partially Updated Dragon"
            # Only updating name
        }
        
        response = client.put(f"/creatures/{creature_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == update_data["name"]
        # Other fields should remain unchanged
        assert data["creature_type"] == test_creature["creature_type"]
    
    def test_update_creature_not_found(self, client: TestClient, auth_headers):
        """Test updating non-existent creature"""
        fake_uuid = "12345678-1234-1234-1234-123456789012"
        update_data = {
            "name": "This won't work"
        }
        
        response = client.put(f"/creatures/{fake_uuid}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_creature_unauthorized(self, client: TestClient, test_creature):
        """Test updating creature without authentication"""
        creature_id = test_creature["id"]
        update_data = {
            "name": "Unauthorized Update"
        }
        
        response = client.put(f"/creatures/{creature_id}", json=update_data)
        
        assert response.status_code == 403
    
    def test_update_creature_wrong_user(self, client: TestClient, test_creature, faker):
        """Test updating another user's creature"""
        # Create a different user
        other_user_data = {
            "email": faker.email(),
            "password": "password123",
            "confirm_password": "password123"
        }
        
        register_response = client.post("/auth/register", json=other_user_data)
        register_data = register_response.json()
        
        if "access_token" in register_data:
            other_token = register_data["access_token"]
        else:
            login_response = client.post("/auth/login", json={
                "email": other_user_data["email"],
                "password": other_user_data["password"]
            })
            other_token = login_response.json()["access_token"]
            
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        # Try to update the first user's creature
        creature_id = test_creature["id"]
        update_data = {
            "name": "Unauthorized Update"
        }
        
        response = client.put(f"/creatures/{creature_id}", json=update_data, headers=other_headers)
        
        assert response.status_code == 404  # Should not find other user's creature
    
    def test_delete_creature_success(self, client: TestClient, auth_headers, test_creature):
        """Test successful creature deletion"""
        creature_id = test_creature["id"]
        
        response = client.delete(f"/creatures/{creature_id}", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Verify creature is deleted by trying to update it
        update_data = {"name": "Should not exist"}
        update_response = client.put(f"/creatures/{creature_id}", json=update_data, headers=auth_headers)
        assert update_response.status_code == 404
    
    def test_delete_creature_not_found(self, client: TestClient, auth_headers):
        """Test deleting non-existent creature"""
        fake_uuid = "12345678-1234-1234-1234-123456789012"
        
        response = client.delete(f"/creatures/{fake_uuid}", headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_delete_creature_unauthorized(self, client: TestClient, test_creature):
        """Test deleting creature without authentication"""
        creature_id = test_creature["id"]
        
        response = client.delete(f"/creatures/{creature_id}")
        
        assert response.status_code == 403
    
    def test_delete_creature_wrong_user(self, client: TestClient, test_creature, faker):
        """Test deleting another user's creature"""
        # Create a different user
        other_user_data = {
            "email": faker.email(),
            "password": "password123",
            "confirm_password": "password123"
        }
        
        register_response = client.post("/auth/register", json=other_user_data)
        register_data = register_response.json()
        
        if "access_token" in register_data:
            other_token = register_data["access_token"]
        else:
            login_response = client.post("/auth/login", json={
                "email": other_user_data["email"],
                "password": other_user_data["password"]
            })
            other_token = login_response.json()["access_token"]
            
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        # Try to delete the first user's creature
        creature_id = test_creature["id"]
        
        response = client.delete(f"/creatures/{creature_id}", headers=other_headers)
        
        assert response.status_code == 404  # Should not find other user's creature


class TestCreatureValidation:
    """Test creature input validation"""
    
    @pytest.mark.parametrize("invalid_initiative", [
        -5,  # Negative initiative
        101,  # Too high initiative
        "not_a_number",  # Invalid type
    ])
    def test_update_creature_invalid_initiative(self, client: TestClient, auth_headers, test_creature, invalid_initiative):
        """Test creature update with invalid initiative values"""
        creature_id = test_creature["id"]
        update_data = {
            "initiative": invalid_initiative
        }
        
        response = client.put(f"/creatures/{creature_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.parametrize("invalid_creature_type", [
        "invalid_type",  # Not in enum
        123,  # Wrong type
        "",  # Empty string
    ])
    def test_update_creature_invalid_type(self, client: TestClient, auth_headers, test_creature, invalid_creature_type):
        """Test creature update with invalid creature types"""
        creature_id = test_creature["id"]
        update_data = {
            "creature_type": invalid_creature_type
        }
        
        response = client.put(f"/creatures/{creature_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 422  # Validation error
    
    def test_update_creature_empty_name(self, client: TestClient, auth_headers, test_creature):
        """Test creature update with empty name"""
        creature_id = test_creature["id"]
        update_data = {
            "name": ""
        }
        
        response = client.put(f"/creatures/{creature_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 422  # Validation error
    
    def test_update_creature_long_name(self, client: TestClient, auth_headers, test_creature):
        """Test creature update with very long name"""
        creature_id = test_creature["id"]
        update_data = {
            "name": "A" * 1000  # Very long name
        }
        
        response = client.put(f"/creatures/{creature_id}", json=update_data, headers=auth_headers)
        
        # Depending on model validation, this might succeed or fail
        assert response.status_code in [200, 422]
    
    def test_update_creature_special_characters_name(self, client: TestClient, auth_headers, test_creature):
        """Test creature update with special characters in name"""
        creature_id = test_creature["id"]
        update_data = {
            "name": "Dragon with Special Chars !@#$%^&*()"
        }
        
        response = client.put(f"/creatures/{creature_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
    
    def test_update_creature_unicode_name(self, client: TestClient, auth_headers, test_creature):
        """Test creature update with unicode characters in name"""
        creature_id = test_creature["id"]
        update_data = {
            "name": "Dragon 🐉 with Unicode ⚔️"
        }
        
        response = client.put(f"/creatures/{creature_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]