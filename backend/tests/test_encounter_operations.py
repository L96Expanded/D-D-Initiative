"""Extended tests for encounter operations to increase coverage."""

import pytest
from fastapi import status


class TestEncounterOperations:
    """Test additional encounter operations."""

    def test_get_encounter_by_id(self, client, authenticated_headers, sample_encounter_data):
        """Test retrieving a specific encounter."""
        # Create encounter
        create_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter_id = create_response.json()["id"]

        # Get encounter by ID
        response = client.get(
            f"/encounters/{encounter_id}",
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == encounter_id
        assert data["name"] == sample_encounter_data["name"]

    def test_get_nonexistent_encounter(self, client, authenticated_headers):
        """Test getting an encounter that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(
            f"/encounters/{fake_id}",
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_encounter_name(self, client, authenticated_headers, sample_encounter_data):
        """Test updating encounter name."""
        # Create encounter
        create_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter_id = create_response.json()["id"]

        # Update encounter
        update_data = {"name": "Updated Encounter Name"}
        response = client.put(
            f"/encounters/{encounter_id}",
            json=update_data,
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Encounter Name"

    def test_update_encounter_background_image(self, client, authenticated_headers, sample_encounter_data):
        """Test updating encounter background image."""
        # Create encounter
        create_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter_id = create_response.json()["id"]

        # Update background
        update_data = {"background_image": "https://example.com/bg.jpg"}
        response = client.put(
            f"/encounters/{encounter_id}",
            json=update_data,
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["background_image"] == "https://example.com/bg.jpg"

    def test_update_nonexistent_encounter(self, client, authenticated_headers):
        """Test updating an encounter that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"name": "New Name"}
        response = client.put(
            f"/encounters/{fake_id}",
            json=update_data,
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_encounter_round_validation(self, client, authenticated_headers, sample_encounter_data):
        """Test round number validation (must be >= 1)."""
        # Create encounter
        create_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter_id = create_response.json()["id"]

        # Try to set round to 0 (should fail validation)
        response = client.patch(
            f"/encounters/{encounter_id}/round",
            json={"round_number": 0},
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_round_nonexistent_encounter(self, client, authenticated_headers):
        """Test updating round for non-existent encounter."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.patch(
            f"/encounters/{fake_id}/round",
            json={"round_number": 5},
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_encounter_with_nested_creatures(self, client, authenticated_headers):
        """Test creating encounter with creatures in the same request."""
        encounter_data = {
            "name": "Battle Arena",
            "background_image": None,
            "creatures": [
                {
                    "name": "Dragon",
                    "initiative": 20,
                    "creature_type": "enemy",
                    "image_url": None,
                },
                {
                    "name": "Knight",
                    "initiative": 15,
                    "creature_type": "player",
                    "image_url": None,
                },
            ],
        }

        response = client.post(
            "/encounters/",
            json=encounter_data,
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Battle Arena"
        assert len(data["creatures"]) == 2
        assert data["creatures"][0]["name"] == "Dragon"
        assert data["creatures"][1]["name"] == "Knight"


class TestCreatureOperations:
    """Test additional creature operations."""

    def test_get_creature_nonexistent(self, client, authenticated_headers):
        """Test getting a creature that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(
            f"/creatures/{fake_id}",
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_creature_nonexistent(self, client, authenticated_headers):
        """Test deleting a creature that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(
            f"/creatures/{fake_id}",
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_creature_nonexistent_encounter(self, client, authenticated_headers, sample_creature_data):
        """Test creating creature with non-existent encounter."""
        sample_creature_data["encounter_id"] = "00000000-0000-0000-0000-000000000000"

        response = client.post(
            "/creatures/",
            json=sample_creature_data,
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Encounter not found" in response.json()["detail"]


class TestHealthEndpointExtended:
    """Extended health endpoint tests."""

    def test_health_check_database_status(self, client):
        """Test health check includes database status."""
        response = client.get("/api/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "timestamp" in data

    def test_health_check_metrics_endpoint(self, client):
        """Test health endpoint exists and returns valid data."""
        response = client.get("/api/health")
        
        # Should return health status
        assert response.status_code == status.HTTP_200_OK
        
    def test_health_check_readiness(self, client):
        """Test readiness endpoint."""
        response = client.get("/api/health/ready")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        
    def test_health_check_liveness(self, client):
        """Test liveness endpoint."""
        response = client.get("/api/health/live")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "alive"


class TestEncounterAdvancedOperations:
    """Test advanced encounter operations."""
    
    def test_delete_encounter(self, client, authenticated_headers, sample_encounter_data):
        """Test deleting an encounter."""
        # Create an encounter
        create_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers
        )
        encounter_id = create_response.json()["id"]
        
        # Delete the encounter
        response = client.delete(
            f"/encounters/{encounter_id}",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's deleted
        get_response = client.get(
            f"/encounters/{encounter_id}",
            headers=authenticated_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_get_encounter_creatures(self, client, authenticated_headers, sample_encounter_data, sample_creature_data):
        """Test getting creatures for a specific encounter."""
        # Create an encounter
        create_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers
        )
        encounter_id = create_response.json()["id"]
        
        # Add a creature to the encounter
        sample_creature_data["encounter_id"] = encounter_id
        client.post(
            "/creatures/",
            json=sample_creature_data,
            headers=authenticated_headers
        )
        
        # Get the encounter's creatures
        response = client.get(
            f"/encounters/{encounter_id}/creatures",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["name"] == sample_creature_data["name"]
        
    def test_get_creatures_for_nonexistent_encounter(self, client, authenticated_headers):
        """Test getting creatures for an encounter that doesn't exist."""
        fake_encounter_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(
            f"/encounters/{fake_encounter_id}/creatures",
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_create_encounter_with_background_image(self, client, authenticated_headers):
        """Test creating encounter with background image."""
        encounter_data = {
            "name": "Visual Battle",
            "background_image": "https://example.com/image.jpg"
        }
        
        response = client.post(
            "/encounters/",
            json=encounter_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["background_image"] == "https://example.com/image.jpg"
        
    def test_update_encounter_name_only(self, client, authenticated_headers, sample_encounter_data):
        """Test updating only the encounter name."""
        # Create encounter
        create_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers
        )
        encounter_id = create_response.json()["id"]
        original_data = create_response.json()
        
        # Update name only
        update_data = {
            "name": "Updated Name",
            "background_image": original_data.get("background_image"),
            "round_number": original_data["round_number"]
        }
        
        response = client.put(
            f"/encounters/{encounter_id}",
            json=update_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
