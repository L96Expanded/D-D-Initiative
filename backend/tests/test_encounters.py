import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import json

from app.models.models import Encounter, User


class TestEncounterCreation:
    """Test encounter creation functionality"""
    
    def test_create_encounter_success(self, client: TestClient, auth_headers):
        """Test successful encounter creation"""
        encounter_data = {
            "name": "Dragon's Lair",
            "background_image": "https://example.com/dragon_lair.jpg"
        }
        
        response = client.post("/encounters/", json=encounter_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == encounter_data["name"]
        assert data["background_image"] == encounter_data["background_image"]
        assert "id" in data
        assert "created_at" in data
        assert "user_id" in data
    
    def test_create_encounter_unauthorized(self, client: TestClient):
        """Test creating encounter without authentication"""
        encounter_data = {
            "name": "Unauthorized Encounter",
            "background_image": "https://example.com/unauthorized.jpg"
        }
        
        response = client.post("/encounters/", json=encounter_data)
        
        assert response.status_code == 403
        assert "forbidden" in response.json()["detail"].lower() or "not authenticated" in response.json()["detail"].lower()
    
    def test_create_encounter_missing_name(self, client: TestClient, auth_headers):
        """Test creating encounter without required name"""
        encounter_data = {
            "background_image": "https://example.com/missing_name.jpg"
        }
        
        response = client.post("/encounters/", json=encounter_data, headers=auth_headers)
        
        assert response.status_code == 422  # Validation error
    
    def test_create_encounter_empty_name(self, client: TestClient, auth_headers):
        """Test creating encounter with empty name"""
        encounter_data = {
            "name": "",
            "background_image": "https://example.com/empty_name.jpg"
        }
        
        response = client.post("/encounters/", json=encounter_data, headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_create_encounter_long_name(self, client: TestClient, auth_headers):
        """Test creating encounter with very long name"""
        encounter_data = {
            "name": "A" * 1000,  # Very long name
            "background_image": "https://example.com/long_name.jpg"
        }
        
        response = client.post("/encounters/", json=encounter_data, headers=auth_headers)
        
        # Depending on model validation, this might succeed or fail
        # Adjust based on actual name length limits
        assert response.status_code in [201, 422]


class TestEncounterRetrieval:
    """Test encounter retrieval functionality"""
    
    def test_get_user_encounters(self, client: TestClient, auth_headers, test_encounter):
        """Test getting user's encounters"""
        response = client.get("/encounters/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Find our test encounter
        encounter = next((e for e in data if e["id"] == test_encounter["id"]), None)
        assert encounter is not None
        assert encounter["name"] == test_encounter["name"]
    
    def test_get_encounters_unauthorized(self, client: TestClient):
        """Test getting encounters without authentication"""
        response = client.get("/encounters/")
        
        assert response.status_code == 403
    
    def test_get_encounter_by_id(self, client: TestClient, auth_headers, test_encounter):
        """Test getting specific encounter by ID"""
        encounter_id = test_encounter["id"]
        response = client.get(f"/encounters/{encounter_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == encounter_id
        assert data["name"] == test_encounter["name"]
        assert "creatures" in data  # Should include creatures list
    
    def test_get_encounter_not_found(self, client: TestClient, auth_headers):
        """Test getting non-existent encounter"""
        # Use a properly formatted UUID that doesn't exist
        fake_uuid = "12345678-1234-1234-1234-123456789012"
        response = client.get(f"/encounters/{fake_uuid}", headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_encounter_wrong_user(self, client: TestClient, test_encounter, faker):
        """Test accessing another user's encounter"""
        # Create a different user and get their auth headers
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
            # If registration doesn't return a token, login to get one
            login_response = client.post("/auth/login", json={
                "email": other_user_data["email"],
                "password": other_user_data["password"]
            })
            other_token = login_response.json()["access_token"]
            
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        # Try to access the first user's encounter
        encounter_id = test_encounter["id"]
        response = client.get(f"/encounters/{encounter_id}", headers=other_headers)
        
        assert response.status_code == 404  # Should not find other user's encounter


class TestEncounterUpdate:
    """Test encounter update functionality"""
    
    def test_update_encounter_success(self, client: TestClient, auth_headers, test_encounter):
        """Test successful encounter update"""
        encounter_id = test_encounter["id"]
        update_data = {
            "name": "Updated Dragon's Lair",
            "background_image": "https://example.com/updated_dragon.jpg"
        }
        
        response = client.put(f"/encounters/{encounter_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == update_data["name"]
        assert data["background_image"] == update_data["background_image"]
        assert data["id"] == encounter_id
    
    def test_update_encounter_partial(self, client: TestClient, auth_headers, test_encounter):
        """Test partial encounter update"""
        encounter_id = test_encounter["id"]
        update_data = {
            "name": "Partially Updated"
            # Only updating name, not background_image
        }
        
        response = client.put(f"/encounters/{encounter_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == update_data["name"]
        # Background image should remain unchanged (or be None if not set initially)
    
    def test_update_encounter_not_found(self, client: TestClient, auth_headers):
        """Test updating non-existent encounter"""
        update_data = {
            "name": "This won't work"
        }
        
        # Use a properly formatted UUID that doesn't exist
        fake_uuid = "12345678-1234-1234-1234-123456789012"
        response = client.put(f"/encounters/{fake_uuid}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_update_encounter_unauthorized(self, client: TestClient, test_encounter):
        """Test updating encounter without authentication"""
        encounter_id = test_encounter["id"]
        update_data = {
            "name": "Unauthorized Update"
        }
        
        response = client.put(f"/encounters/{encounter_id}", json=update_data)
        
        assert response.status_code == 403


class TestEncounterDeletion:
    """Test encounter deletion functionality"""
    
    def test_delete_encounter_success(self, client: TestClient, auth_headers, test_encounter):
        """Test successful encounter deletion"""
        encounter_id = test_encounter["id"]
        
        response = client.delete(f"/encounters/{encounter_id}", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Verify encounter is deleted
        get_response = client.get(f"/encounters/{encounter_id}", headers=auth_headers)
        assert get_response.status_code == 404
    
    def test_delete_encounter_not_found(self, client: TestClient, auth_headers):
        """Test deleting non-existent encounter"""
        # Use a properly formatted UUID that doesn't exist
        fake_uuid = "12345678-1234-1234-1234-123456789012"
        response = client.delete(f"/encounters/{fake_uuid}", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_delete_encounter_unauthorized(self, client: TestClient, test_encounter):
        """Test deleting encounter without authentication"""
        encounter_id = test_encounter["id"]
        
        response = client.delete(f"/encounters/{encounter_id}")
        
        assert response.status_code == 403


class TestEncounterState:
    """Test encounter state management"""
    
    @pytest.mark.skip(reason="Encounter state endpoints not implemented yet")
    def test_start_encounter(self, client: TestClient, auth_headers, test_encounter):
        """Test starting an encounter"""
        encounter_id = test_encounter["id"]
        
        response = client.post(f"/encounters/{encounter_id}/start", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["is_active"] == True
        assert "message" in data
    
    @pytest.mark.skip(reason="Encounter state endpoints not implemented yet")
    def test_start_nonexistent_encounter(self, client: TestClient, auth_headers):
        """Test starting a non-existent encounter"""
        fake_uuid = "12345678-1234-1234-1234-123456789012"
        response = client.post(f"/encounters/{fake_uuid}/start", headers=auth_headers)
        
        assert response.status_code == 404
    
    @pytest.mark.skip(reason="Encounter state endpoints not implemented yet")
    def test_end_encounter(self, client: TestClient, auth_headers, test_encounter):
        """Test ending an encounter"""
        encounter_id = test_encounter["id"]
        
        # First start the encounter
        client.post(f"/encounters/{encounter_id}/start", headers=auth_headers)
        
        # Then end it
        response = client.post(f"/encounters/{encounter_id}/end", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["is_active"] == False
        assert "message" in data
    
    @pytest.mark.skip(reason="Encounter state endpoints not implemented yet")
    def test_reset_encounter(self, client: TestClient, auth_headers, test_encounter):
        """Test resetting an encounter"""
        encounter_id = test_encounter["id"]
        
        response = client.post(f"/encounters/{encounter_id}/reset", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        # Should reset initiative order and turn tracking


class TestEncounterInitiative:
    """Test encounter initiative management"""
    
    @pytest.mark.skip(reason="Initiative management endpoints not implemented yet")
    def test_roll_initiative(self, client: TestClient, auth_headers, test_encounter_with_creatures):
        """Test rolling initiative for encounter"""
        encounter_id = test_encounter_with_creatures["id"]
        
        response = client.post(f"/encounters/{encounter_id}/roll-initiative", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "initiative_order" in data
        
        # Check that creatures have initiative values
        initiative_order = data["initiative_order"]
        assert len(initiative_order) > 0
        
        for creature in initiative_order:
            assert "initiative" in creature
            assert creature["initiative"] >= 1  # Should have rolled initiative
    
    @pytest.mark.skip(reason="Initiative management endpoints not implemented yet")
    def test_next_turn(self, client: TestClient, auth_headers, test_encounter_with_creatures):
        """Test advancing to next turn"""
        encounter_id = test_encounter_with_creatures["id"]
        
        # Start encounter and roll initiative first
        client.post(f"/encounters/{encounter_id}/start", headers=auth_headers)
        client.post(f"/encounters/{encounter_id}/roll-initiative", headers=auth_headers)
        
        response = client.post(f"/encounters/{encounter_id}/next-turn", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "current_turn" in data
        assert "message" in data
    
    @pytest.mark.skip(reason="Initiative management endpoints not implemented yet")
    def test_previous_turn(self, client: TestClient, auth_headers, test_encounter_with_creatures):
        """Test going to previous turn"""
        encounter_id = test_encounter_with_creatures["id"]
        
        # Start encounter and roll initiative first
        client.post(f"/encounters/{encounter_id}/start", headers=auth_headers)
        client.post(f"/encounters/{encounter_id}/roll-initiative", headers=auth_headers)
        
        # Go forward a turn first
        client.post(f"/encounters/{encounter_id}/next-turn", headers=auth_headers)
        
        # Then go back
        response = client.post(f"/encounters/{encounter_id}/previous-turn", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "current_turn" in data
        assert "message" in data


class TestEncounterAuthorization:
    """Test encounter authorization and user isolation"""
    
    def test_user_can_only_see_own_encounters(self, client: TestClient, faker):
        """Test that users can only see their own encounters"""
        # Create first user and encounter
        user1_data = {
            "email": faker.email(),
            "password": "password123",
            "confirm_password": "password123"
        }
        
        user1_response = client.post("/auth/register", json=user1_data)
        # Handle both possible response structures
        user1_response_data = user1_response.json()
        if "access_token" in user1_response_data:
            user1_token = user1_response_data["access_token"]
        else:
            # If registration doesn't return a token, login to get one
            login_response = client.post("/auth/login", json={
                "email": user1_data["email"],
                "password": user1_data["password"]
            })
            user1_token = login_response.json()["access_token"]
        
        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        
        encounter1_data = {
            "name": "User 1's Encounter",
            "background_image": "https://example.com/user1_encounter.jpg"
        }
        
        client.post("/encounters/", json=encounter1_data, headers=user1_headers)
        
        # Create second user and encounter
        user2_data = {
            "email": faker.email(),
            "password": "password123",
            "confirm_password": "password123"
        }
        
        user2_response = client.post("/auth/register", json=user2_data)
        # Handle both possible response structures
        user2_response_data = user2_response.json()
        if "access_token" in user2_response_data:
            user2_token = user2_response_data["access_token"]
        else:
            # If registration doesn't return a token, login to get one
            login_response = client.post("/auth/login", json={
                "email": user2_data["email"],
                "password": user2_data["password"]
            })
            user2_token = login_response.json()["access_token"]
        
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        encounter2_data = {
            "name": "User 2's Encounter",
            "background_image": "https://example.com/user2_encounter.jpg"
        }
        
        client.post("/encounters/", json=encounter2_data, headers=user2_headers)
        
        # Check that each user only sees their own encounters
        user1_encounters = client.get("/encounters/", headers=user1_headers).json()
        user2_encounters = client.get("/encounters/", headers=user2_headers).json()
        
        # User 1 should only see their encounter
        assert len(user1_encounters) == 1
        assert user1_encounters[0]["name"] == "User 1's Encounter"
        
        # User 2 should only see their encounter
        assert len(user2_encounters) == 1
        assert user2_encounters[0]["name"] == "User 2's Encounter"


class TestEncounterValidation:
    """Test encounter input validation"""
    
    @pytest.mark.parametrize("invalid_data", [
        {},  # Empty data
        {"description": "Missing name"},  # Missing name
        {"name": ""},  # Empty name
        {"name": None},  # Null name
    ])
    def test_create_encounter_validation_errors(self, client: TestClient, auth_headers, invalid_data):
        """Test encounter creation with invalid data"""
        response = client.post("/encounters/", json=invalid_data, headers=auth_headers)
        assert response.status_code == 422
    
    def test_create_encounter_with_special_characters(self, client: TestClient, auth_headers):
        """Test encounter creation with special characters in name"""
        encounter_data = {
            "name": "Encounter with Special Characters !@#$%^&*()",
            "background_image": "https://example.com/special_chars.jpg"
        }
        
        response = client.post("/encounters/", json=encounter_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == encounter_data["name"]
    
    def test_create_encounter_with_unicode(self, client: TestClient, auth_headers):
        """Test encounter creation with unicode characters"""
        encounter_data = {
            "name": "Encounter with Unicode 🐉 ⚔️ 🏰",
            "background_image": "https://example.com/unicode.jpg"
        }
        
        response = client.post("/encounters/", json=encounter_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == encounter_data["name"]