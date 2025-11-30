"""Test preset endpoints."""
import pytest
from fastapi import status


class TestPresetEndpoints:
    """Test preset CRUD operations."""
    
    def test_create_preset(self, client, authenticated_headers):
        """Test creating a new preset."""
        preset_data = {
            "name": "Test Preset",
            "description": "Test description"
        }
        
        response = client.post(
            "/presets/",
            json=preset_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test Preset"
        assert data["description"] == "Test description"
        assert "id" in data
        
    def test_get_presets_list(self, client, authenticated_headers):
        """Test getting list of presets."""
        # Create a preset first
        preset_data = {
            "name": "Test Preset",
            "description": "Test description"
        }
        client.post(
            "/presets/",
            json=preset_data,
            headers=authenticated_headers
        )
        
        response = client.get("/presets/", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
    def test_get_preset_by_id(self, client, authenticated_headers):
        """Test getting a specific preset by ID."""
        # Create a preset
        preset_data = {
            "name": "Test Preset",
            "description": "Test description"
        }
        create_response = client.post(
            "/presets/",
            json=preset_data,
            headers=authenticated_headers
        )
        preset_id = create_response.json()["id"]
        
        # Get the preset
        response = client.get(f"/presets/{preset_id}", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == preset_id
        assert data["name"] == "Test Preset"
        
    def test_delete_preset(self, client, authenticated_headers):
        """Test deleting a preset."""
        # Create a preset
        preset_data = {
            "name": "Test Preset",
            "description": "Test description"
        }
        create_response = client.post(
            "/presets/",
            json=preset_data,
            headers=authenticated_headers
        )
        preset_id = create_response.json()["id"]
        
        # Delete the preset
        response = client.delete(f"/presets/{preset_id}", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's deleted
        get_response = client.get(f"/presets/{preset_id}", headers=authenticated_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_get_nonexistent_preset(self, client, authenticated_headers):
        """Test getting a preset that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/presets/{fake_id}", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_delete_nonexistent_preset(self, client, authenticated_headers):
        """Test deleting a preset that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f"/presets/{fake_id}", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_create_preset_unauthorized(self, client):
        """Test creating a preset without authentication."""
        preset_data = {
            "name": "Test Preset",
            "description": "Test description"
        }
        
        response = client.post("/presets/", json=preset_data)
        
        # Accept both 401 and 403 (varies between environments)
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_update_preset(self, client, authenticated_headers):
        """Test updating a preset."""
        # Create a preset
        preset_data = {
            "name": "Original Preset",
            "description": "Original description"
        }
        create_response = client.post(
            "/presets/",
            json=preset_data,
            headers=authenticated_headers
        )
        preset_id = create_response.json()["id"]
        
        # Update the preset
        update_data = {
            "name": "Updated Preset",
            "description": "Updated description"
        }
        response = client.put(
            f"/presets/{preset_id}",
            json=update_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Preset"
        assert data["description"] == "Updated description"
        
    def test_update_preset_with_creatures(self, client, authenticated_headers):
        """Test updating a preset with creatures."""
        # Create a preset with creatures
        preset_data = {
            "name": "Battle Preset",
            "description": "Pre-configured battle",
            "creatures": [
                {
                    "name": "Goblin",
                    "initiative": 12,
                    "creature_type": "enemy"
                }
            ]
        }
        create_response = client.post(
            "/presets/",
            json=preset_data,
            headers=authenticated_headers
        )
        preset_id = create_response.json()["id"]
        
        # Update with new creatures
        update_data = {
            "name": "Updated Battle",
            "description": "Updated battle",
            "creatures": [
                {
                    "name": "Orc",
                    "initiative": 15,
                    "creature_type": "enemy"
                },
                {
                    "name": "Knight",
                    "initiative": 18,
                    "creature_type": "player"
                }
            ]
        }
        response = client.put(
            f"/presets/{preset_id}",
            json=update_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Battle"
        assert len(data["creatures"]) == 2
        assert data["creatures"][0]["name"] == "Orc"
        assert data["creatures"][1]["name"] == "Knight"
        
    def test_update_nonexistent_preset(self, client, authenticated_headers):
        """Test updating a preset that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {
            "name": "Updated Preset",
            "description": "Updated description"
        }
        response = client.put(
            f"/presets/{fake_id}",
            json=update_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
