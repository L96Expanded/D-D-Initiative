import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import json

from app.models.models import Creature, Encounter
from app.models.enums import CreatureType


class TestCreatureCreation:
    """Test creature creation functionality"""
    
    def test_create_creature_success(self, client: TestClient, auth_headers, test_encounter):
        """Test successful creature creation"""
        encounter_id = test_encounter["id"]
        creature_data = {
            "name": "Red Dragon",
            "initiative": 15,
            "creature_type": "enemy",
            "image_url": "https://example.com/dragon.jpg"
        }
        
        response = client.post(
            f"/encounters/{encounter_id}/creatures/", 
            json=creature_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == creature_data["name"]
        assert data["initiative"] == creature_data["initiative"]
        assert data["creature_type"] == creature_data["creature_type"]
        assert data["image_url"] == creature_data["image_url"]
        assert "id" in data
        assert "created_at" in data
        assert data["encounter_id"] == encounter_id
    
    def test_create_creature_minimal_data(self, client: TestClient, auth_headers, test_encounter):
        """Test creating creature with minimal required data"""
        encounter_id = test_encounter["id"]
        creature_data = {
            "name": "Goblin",
            "initiative": 10,
            "creature_type": "enemy"
            # No image_url (optional field)
        }
        
        response = client.post(
            f"/encounters/{encounter_id}/creatures/", 
            json=creature_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == creature_data["name"]
        assert data["initiative"] == creature_data["initiative"]
        assert data["creature_type"] == creature_data["creature_type"]
        assert data["image_url"] is None
    
    def test_create_creature_unauthorized(self, client: TestClient, test_encounter):
        """Test creating creature without authentication"""
        encounter_id = test_encounter["id"]
        creature_data = {
            "name": "Unauthorized Creature",
            "initiative": 5,
            "creature_type": "ally"
        }
        
        response = client.post(f"/encounters/{encounter_id}/creatures/", json=creature_data)
        
        assert response.status_code == 403
    
    def test_create_creature_nonexistent_encounter(self, client: TestClient, auth_headers):
        """Test creating creature for non-existent encounter"""
        creature_data = {
            "name": "Lost Creature",
            "initiative": 5,
            "creature_type": "ally"
        }

        # Use a valid UUID format that doesn't exist in the database
        fake_encounter_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            f"/encounters/{fake_encounter_id}/creatures/", 
            json=creature_data, 
            headers=auth_headers
        )

        assert response.status_code == 404
    
    def test_create_creature_other_users_encounter(self, client: TestClient, test_encounter):
        """Test creating creature in another user's encounter"""
        # Create a different user
        other_user_data = {
            "email": "other@example.com",
            "password": "password123",
            "confirm_password": "password123"
        }
        
        register_response = client.post("/auth/register", json=other_user_data)
        other_token = register_response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        # Try to add creature to first user's encounter
        encounter_id = test_encounter["id"]
        creature_data = {
            "name": "Unauthorized Creature",
            "initiative": 5,
            "creature_type": "ally"
        }
        
        response = client.post(
            f"/encounters/{encounter_id}/creatures/", 
            json=creature_data, 
            headers=other_headers
        )
        
        assert response.status_code == 404  # Should not find other user's encounter


class TestCreatureRetrieval:
    """Test creature retrieval functionality"""
    
    def test_get_encounter_creatures(self, client: TestClient, auth_headers, test_encounter_with_creatures):
        """Test getting all creatures for an encounter"""
        encounter_id = test_encounter_with_creatures["id"]
        
        response = client.get(f"/encounters/{encounter_id}/creatures/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 2  # Should have test creatures
        
        # Verify creature data structure
        for creature in data:
            assert "id" in creature
            assert "name" in creature
            assert "initiative" in creature
            assert "creature_type" in creature
            assert "encounter_id" in creature
            assert creature["encounter_id"] == encounter_id
    
    def test_get_creature_by_id(self, client: TestClient, auth_headers, test_creature):
        """Test getting specific creature by ID"""
        creature_id = test_creature["id"]
        encounter_id = test_creature["encounter_id"]
        
        response = client.get(
            f"/encounters/{encounter_id}/creatures/{creature_id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == str(creature_id)
        assert data["name"] == test_creature["name"]
        assert data["initiative"] == test_creature["initiative"]
        assert data["creature_type"] == test_creature["creature_type"]
    
    def test_get_creature_not_found(self, client: TestClient, auth_headers, test_encounter):
        """Test getting non-existent creature"""
        encounter_id = test_encounter["id"]
        
        # Use a valid UUID format that doesn't exist in the database
        fake_creature_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(
            f"/encounters/{encounter_id}/creatures/{fake_creature_id}", 
            headers=auth_headers
        )

        assert response.status_code == 404
    
    def test_get_creatures_unauthorized(self, client: TestClient, test_encounter):
        """Test getting creatures without authentication"""
        encounter_id = test_encounter["id"]
        
        response = client.get(f"/encounters/{encounter_id}/creatures/")

        assert response.status_code == 403
class TestCreatureUpdate:
    """Test creature update functionality"""
    
    def test_update_creature_success(self, client: TestClient, auth_headers, test_creature):
        """Test successful creature update"""
        creature_id = test_creature["id"]
        encounter_id = test_creature["encounter_id"]
        
        update_data = {
            "name": "Updated Dragon",
            "initiative": 20,
            "creature_type": "other",  # Changed from "boss" to valid enum value
            "image_url": "https://example.com/updated-dragon.jpg"
        }
        
        response = client.put(
            f"/encounters/{encounter_id}/creatures/{creature_id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == update_data["name"]
        assert data["initiative"] == update_data["initiative"]
        assert data["creature_type"] == update_data["creature_type"]
        assert data["image_url"] == update_data["image_url"]
        assert data["id"] == str(creature_id)
    
    def test_update_creature_partial(self, client: TestClient, auth_headers, test_creature):
        """Test partial creature update"""
        creature_id = test_creature["id"]
        encounter_id = test_creature["encounter_id"]
        
        update_data = {
            "initiative": 25  # Only updating initiative
        }
        
        response = client.put(
            f"/encounters/{encounter_id}/creatures/{creature_id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["initiative"] == update_data["initiative"]
        assert data["name"] == test_creature["name"]  # Should remain unchanged
        assert data["creature_type"] == test_creature["creature_type"]  # Should remain unchanged
    
    def test_update_creature_not_found(self, client: TestClient, auth_headers, test_encounter):
        """Test updating non-existent creature"""
        encounter_id = test_encounter["id"]
        update_data = {
            "name": "Non-existent Creature"
        }
        
        # Use a valid UUID format that doesn't exist in the database
        fake_creature_id = "00000000-0000-0000-0000-000000000000"
        response = client.put(
            f"/encounters/{encounter_id}/creatures/{fake_creature_id}", 
            json=update_data, 
            headers=auth_headers
        )

        assert response.status_code == 404
    
    def test_update_creature_unauthorized(self, client: TestClient, test_creature):
        """Test updating creature without authentication"""
        creature_id = test_creature["id"]
        encounter_id = test_creature["encounter_id"]
        
        update_data = {
            "name": "Unauthorized Update"
        }
        
        response = client.put(
            f"/encounters/{encounter_id}/creatures/{creature_id}", 
            json=update_data
        )

        assert response.status_code == 403
class TestCreatureDeletion:
    """Test creature deletion functionality"""
    
    def test_delete_creature_success(self, client: TestClient, auth_headers, test_creature):
        """Test successful creature deletion"""
        creature_id = test_creature["id"]
        encounter_id = test_creature["encounter_id"]
        
        response = client.delete(
            f"/encounters/{encounter_id}/creatures/{creature_id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify creature is deleted
        get_response = client.get(
            f"/encounters/{encounter_id}/creatures/{creature_id}", 
            headers=auth_headers
        )
        assert get_response.status_code == 404
    
    def test_delete_creature_not_found(self, client: TestClient, auth_headers, test_encounter):
        """Test deleting non-existent creature"""
        encounter_id = test_encounter["id"]
        
        # Use a valid UUID format that doesn't exist in the database
        fake_creature_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(
            f"/encounters/{encounter_id}/creatures/{fake_creature_id}", 
            headers=auth_headers
        )

        assert response.status_code == 404
    
    def test_delete_creature_unauthorized(self, client: TestClient, test_creature):
        """Test deleting creature without authentication"""
        creature_id = test_creature["id"]
        encounter_id = test_creature["encounter_id"]
        
        response = client.delete(f"/encounters/{encounter_id}/creatures/{creature_id}")

        assert response.status_code == 403
class TestCreatureTypes:
    """Test creature type functionality"""
    
    @pytest.mark.parametrize("creature_type", ["player", "ally", "enemy", "other"])
    def test_valid_creature_types(self, client: TestClient, auth_headers, test_encounter, creature_type):
        """Test all valid creature types"""
        encounter_id = test_encounter["id"]
        creature_data = {
            "name": f"Test {creature_type.title()}",
            "initiative": 10,
            "creature_type": creature_type
        }
        
        response = client.post(
            f"/encounters/{encounter_id}/creatures/", 
            json=creature_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["creature_type"] == creature_type
    
    def test_invalid_creature_type(self, client: TestClient, auth_headers, test_encounter):
        """Test invalid creature type"""
        encounter_id = test_encounter["id"]
        creature_data = {
            "name": "Invalid Type Creature",
            "initiative": 10,
            "creature_type": "invalid_type"
        }
        
        response = client.post(
            f"/encounters/{encounter_id}/creatures/", 
            json=creature_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error


class TestCreatureInitiative:
    """Test creature initiative functionality"""
    
    def test_set_creature_initiative(self, client: TestClient, auth_headers, test_creature):
        """Test setting creature initiative"""
        creature_id = test_creature["id"]
        encounter_id = test_creature["encounter_id"]
        
        new_initiative = 25
        update_data = {"initiative": new_initiative}
        
        response = client.put(
            f"/encounters/{encounter_id}/creatures/{creature_id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["initiative"] == new_initiative
    
    @pytest.mark.parametrize("initiative_value", [1, 10, 20, 30])
    def test_valid_initiative_values(self, client: TestClient, auth_headers, test_encounter, initiative_value):
        """Test various valid initiative values"""
        encounter_id = test_encounter["id"]
        creature_data = {
            "name": f"Creature Initiative {initiative_value}",
            "initiative": initiative_value,
            "creature_type": "enemy"
        }
        
        response = client.post(
            f"/encounters/{encounter_id}/creatures/", 
            json=creature_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["initiative"] == initiative_value
    
    @pytest.mark.parametrize("invalid_initiative", [-1, "invalid", None])
    def test_invalid_initiative_values(self, client: TestClient, auth_headers, test_encounter, invalid_initiative):
        """Test invalid initiative values"""
        encounter_id = test_encounter["id"]
        creature_data = {
            "name": "Invalid Initiative Creature",
            "initiative": invalid_initiative,
            "creature_type": "enemy"
        }
        
        response = client.post(
            f"/encounters/{encounter_id}/creatures/", 
            json=creature_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error


class TestCreatureImageURL:
    """Test creature image URL functionality"""
    
    def test_creature_with_image_url(self, client: TestClient, auth_headers, test_encounter):
        """Test creating creature with image URL"""
        encounter_id = test_encounter["id"]
        image_url = "https://example.com/creature.jpg"
        creature_data = {
            "name": "Creature with Image",
            "initiative": 10,
            "creature_type": "enemy",
            "image_url": image_url
        }
        
        response = client.post(
            f"/encounters/{encounter_id}/creatures/", 
            json=creature_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["image_url"] == image_url
    
    def test_creature_without_image_url(self, client: TestClient, auth_headers, test_encounter):
        """Test creating creature without image URL"""
        encounter_id = test_encounter["id"]
        creature_data = {
            "name": "Creature without Image",
            "initiative": 10,
            "creature_type": "enemy"
            # No image_url
        }
        
        response = client.post(
            f"/encounters/{encounter_id}/creatures/", 
            json=creature_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["image_url"] is None
    
    def test_update_creature_image_url(self, client: TestClient, auth_headers, test_creature):
        """Test updating creature image URL"""
        creature_id = test_creature["id"]
        encounter_id = test_creature["encounter_id"]
        
        new_image_url = "https://example.com/updated-creature.jpg"
        update_data = {"image_url": new_image_url}
        
        response = client.put(
            f"/encounters/{encounter_id}/creatures/{creature_id}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["image_url"] == new_image_url


class TestCreatureValidation:
    """Test creature input validation"""
    
    @pytest.mark.parametrize("invalid_data", [
        {},  # Empty data
        {"initiative": 10, "creature_type": "enemy"},  # Missing name
        {"name": "Test", "creature_type": "enemy"},  # Missing initiative
        {"name": "Test", "initiative": 10},  # Missing creature_type
        {"name": "", "initiative": 10, "creature_type": "enemy"},  # Empty name
        {"name": None, "initiative": 10, "creature_type": "enemy"},  # Null name
    ])
    def test_create_creature_validation_errors(self, client: TestClient, auth_headers, test_encounter, invalid_data):
        """Test creature creation with invalid data"""
        encounter_id = test_encounter["id"]
        
        response = client.post(
            f"/encounters/{encounter_id}/creatures/", 
            json=invalid_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_create_creature_with_special_characters(self, client: TestClient, auth_headers, test_encounter):
        """Test creature creation with special characters in name"""
        encounter_id = test_encounter["id"]
        creature_data = {
            "name": "Creature with Special Characters !@#$%^&*()",
            "initiative": 10,
            "creature_type": "enemy"
        }
        
        response = client.post(
            f"/encounters/{encounter_id}/creatures/", 
            json=creature_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == creature_data["name"]
    
    def test_create_creature_with_unicode(self, client: TestClient, auth_headers, test_encounter):
        """Test creature creation with unicode characters"""
        encounter_id = test_encounter["id"]
        creature_data = {
            "name": "Creature with Unicode 🐉 ⚔️ 🏰",
            "initiative": 10,
            "creature_type": "enemy"
        }
        
        response = client.post(
            f"/encounters/{encounter_id}/creatures/", 
            json=creature_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == creature_data["name"]
    
    def test_long_creature_name(self, client: TestClient, auth_headers, test_encounter):
        """Test creature creation with very long name"""
        encounter_id = test_encounter["id"]
        creature_data = {
            "name": "A" * 1000,  # Very long name
            "initiative": 10,
            "creature_type": "enemy"
        }
        
        response = client.post(
            f"/encounters/{encounter_id}/creatures/", 
            json=creature_data, 
            headers=auth_headers
        )
        
        # Depending on model validation, this might succeed or fail
        assert response.status_code in [200, 422]


class TestCreatureEncounterRelationship:
    """Test creature-encounter relationship functionality"""
    
    def test_delete_encounter_deletes_creatures(self, client: TestClient, auth_headers, test_encounter_with_creatures):
        """Test that deleting an encounter also deletes its creatures"""
        encounter_id = test_encounter_with_creatures["id"]
        
        # Get creatures before deletion
        creatures_response = client.get(f"/encounters/{encounter_id}/creatures/", headers=auth_headers)
        assert creatures_response.status_code == 200
        creatures = creatures_response.json()
        assert len(creatures) >= 2
        
        # Delete the encounter
        delete_response = client.delete(f"/encounters/{encounter_id}", headers=auth_headers)
        assert delete_response.status_code == 200
        
        # Verify creatures are also deleted (encounter not found)
        creatures_response = client.get(f"/encounters/{encounter_id}/creatures/", headers=auth_headers)
        assert creatures_response.status_code == 404
    
    def test_creature_belongs_to_correct_encounter(self, client: TestClient, auth_headers):
        """Test that creatures belong to the correct encounter"""
        # Create two encounters
        encounter1_data = {"name": "Encounter 1", "description": "First encounter"}
        encounter2_data = {"name": "Encounter 2", "description": "Second encounter"}
        
        enc1_response = client.post("/encounters/", json=encounter1_data, headers=auth_headers)
        enc2_response = client.post("/encounters/", json=encounter2_data, headers=auth_headers)
        
        encounter1_id = enc1_response.json()["id"]
        encounter2_id = enc2_response.json()["id"]
        
        # Create creatures in each encounter
        creature1_data = {"name": "Creature 1", "initiative": 10, "creature_type": "enemy"}
        creature2_data = {"name": "Creature 2", "initiative": 15, "creature_type": "ally"}
        
        client.post(f"/encounters/{encounter1_id}/creatures/", json=creature1_data, headers=auth_headers)
        client.post(f"/encounters/{encounter2_id}/creatures/", json=creature2_data, headers=auth_headers)
        
        # Verify creatures are in correct encounters
        enc1_creatures = client.get(f"/encounters/{encounter1_id}/creatures/", headers=auth_headers).json()
        enc2_creatures = client.get(f"/encounters/{encounter2_id}/creatures/", headers=auth_headers).json()
        
        assert len(enc1_creatures) == 1
        assert len(enc2_creatures) == 1
        assert enc1_creatures[0]["name"] == "Creature 1"
        assert enc2_creatures[0]["name"] == "Creature 2"
        assert enc1_creatures[0]["encounter_id"] == encounter1_id
        assert enc2_creatures[0]["encounter_id"] == encounter2_id