"""Tests for creature operations within encounters to increase coverage."""

import pytest
from fastapi import status


class TestEncounterCreatureOperations:
    """Test creature operations within specific encounters."""

    def test_get_creature_by_id(self, client, authenticated_headers, sample_encounter_data, sample_creature_data):
        """Test retrieving a specific creature from an encounter."""
        # Create encounter
        encounter_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter_id = encounter_response.json()["id"]

        # Add creature to encounter
        sample_creature_data["encounter_id"] = encounter_id
        creature_response = client.post(
            "/creatures/",
            json=sample_creature_data,
            headers=authenticated_headers,
        )
        creature_id = creature_response.json()["id"]

        # Get creature from encounter
        response = client.get(
            f"/encounters/{encounter_id}/creatures/{creature_id}",
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == creature_id
        assert data["name"] == sample_creature_data["name"]

    def test_get_creature_from_wrong_encounter(self, client, authenticated_headers, sample_encounter_data, sample_creature_data):
        """Test getting a creature from wrong encounter returns 404."""
        # Create two encounters
        encounter1_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter1_id = encounter1_response.json()["id"]

        encounter2_data = sample_encounter_data.copy()
        encounter2_data["name"] = "Different Encounter"
        encounter2_response = client.post(
            "/encounters/",
            json=encounter2_data,
            headers=authenticated_headers,
        )
        encounter2_id = encounter2_response.json()["id"]

        # Add creature to encounter1
        sample_creature_data["encounter_id"] = encounter1_id
        creature_response = client.post(
            "/creatures/",
            json=sample_creature_data,
            headers=authenticated_headers,
        )
        creature_id = creature_response.json()["id"]

        # Try to get creature from encounter2 (should fail)
        response = client.get(
            f"/encounters/{encounter2_id}/creatures/{creature_id}",
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_nonexistent_creature_from_encounter(self, client, authenticated_headers, sample_encounter_data):
        """Test getting a creature that doesn't exist."""
        # Create encounter
        encounter_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter_id = encounter_response.json()["id"]

        fake_creature_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(
            f"/encounters/{encounter_id}/creatures/{fake_creature_id}",
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_creature_to_encounter(self, client, authenticated_headers, sample_encounter_data):
        """Test adding a creature to an existing encounter."""
        # Create encounter
        encounter_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter_id = encounter_response.json()["id"]

        # Add creature
        creature_data = {
            "name": "Goblin",
            "initiative": 12,
            "creature_type": "enemy",
            "image_url": None,
        }

        response = client.post(
            f"/encounters/{encounter_id}/creatures",
            json=creature_data,
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Goblin"
        assert data["encounter_id"] == encounter_id

    def test_add_creature_to_nonexistent_encounter(self, client, authenticated_headers):
        """Test adding a creature to an encounter that doesn't exist."""
        fake_encounter_id = "00000000-0000-0000-0000-000000000000"
        creature_data = {
            "name": "Goblin",
            "initiative": 12,
            "creature_type": "enemy",
            "image_url": None,
        }

        response = client.post(
            f"/encounters/{fake_encounter_id}/creatures",
            json=creature_data,
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_creature_in_encounter(self, client, authenticated_headers, sample_encounter_data, sample_creature_data):
        """Test updating a creature within an encounter."""
        # Create encounter
        encounter_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter_id = encounter_response.json()["id"]

        # Add creature
        sample_creature_data["encounter_id"] = encounter_id
        creature_response = client.post(
            "/creatures/",
            json=sample_creature_data,
            headers=authenticated_headers,
        )
        creature_id = creature_response.json()["id"]

        # Update creature
        update_data = {
            "name": "Updated Creature",
            "initiative": 25,
            "hit_points": 50,
            "max_hit_points": 50,
        }

        response = client.put(
            f"/encounters/{encounter_id}/creatures/{creature_id}",
            json=update_data,
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Creature"
        assert data["initiative"] == 25
        assert data["hit_points"] == 50

    def test_update_creature_hit_points_only(self, client, authenticated_headers, sample_encounter_data, sample_creature_data):
        """Test updating only creature hit points."""
        # Create encounter and creature
        encounter_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter_id = encounter_response.json()["id"]

        sample_creature_data["encounter_id"] = encounter_id
        creature_response = client.post(
            "/creatures/",
            json=sample_creature_data,
            headers=authenticated_headers,
        )
        creature_id = creature_response.json()["id"]

        # Update only hit points
        update_data = {"hit_points": 15}

        response = client.put(
            f"/encounters/{encounter_id}/creatures/{creature_id}",
            json=update_data,
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["hit_points"] == 15
        assert data["name"] == sample_creature_data["name"]  # Name unchanged

    def test_update_creature_from_wrong_encounter(self, client, authenticated_headers, sample_encounter_data, sample_creature_data):
        """Test updating a creature from wrong encounter returns 404."""
        # Create two encounters
        encounter1_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter1_id = encounter1_response.json()["id"]

        encounter2_data = sample_encounter_data.copy()
        encounter2_data["name"] = "Different Encounter"
        encounter2_response = client.post(
            "/encounters/",
            json=encounter2_data,
            headers=authenticated_headers,
        )
        encounter2_id = encounter2_response.json()["id"]

        # Add creature to encounter1
        sample_creature_data["encounter_id"] = encounter1_id
        creature_response = client.post(
            "/creatures/",
            json=sample_creature_data,
            headers=authenticated_headers,
        )
        creature_id = creature_response.json()["id"]

        # Try to update creature from encounter2 (should fail)
        update_data = {"name": "Updated Name"}
        response = client.put(
            f"/encounters/{encounter2_id}/creatures/{creature_id}",
            json=update_data,
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_nonexistent_creature(self, client, authenticated_headers, sample_encounter_data):
        """Test updating a creature that doesn't exist."""
        # Create encounter
        encounter_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter_id = encounter_response.json()["id"]

        fake_creature_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"name": "Updated Name"}

        response = client.put(
            f"/encounters/{encounter_id}/creatures/{fake_creature_id}",
            json=update_data,
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_creature_from_encounter(self, client, authenticated_headers, sample_encounter_data, sample_creature_data):
        """Test deleting a creature from an encounter."""
        # Create encounter
        encounter_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter_id = encounter_response.json()["id"]

        # Add creature
        sample_creature_data["encounter_id"] = encounter_id
        creature_response = client.post(
            "/creatures/",
            json=sample_creature_data,
            headers=authenticated_headers,
        )
        creature_id = creature_response.json()["id"]

        # Delete creature
        response = client.delete(
            f"/encounters/{encounter_id}/creatures/{creature_id}",
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's deleted
        get_response = client.get(
            f"/encounters/{encounter_id}/creatures/{creature_id}",
            headers=authenticated_headers,
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_creature_from_wrong_encounter(self, client, authenticated_headers, sample_encounter_data, sample_creature_data):
        """Test deleting a creature from wrong encounter returns 404."""
        # Create two encounters
        encounter1_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter1_id = encounter1_response.json()["id"]

        encounter2_data = sample_encounter_data.copy()
        encounter2_data["name"] = "Different Encounter"
        encounter2_response = client.post(
            "/encounters/",
            json=encounter2_data,
            headers=authenticated_headers,
        )
        encounter2_id = encounter2_response.json()["id"]

        # Add creature to encounter1
        sample_creature_data["encounter_id"] = encounter1_id
        creature_response = client.post(
            "/creatures/",
            json=sample_creature_data,
            headers=authenticated_headers,
        )
        creature_id = creature_response.json()["id"]

        # Try to delete creature from encounter2 (should fail)
        response = client.delete(
            f"/encounters/{encounter2_id}/creatures/{creature_id}",
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_creature_from_encounter(self, client, authenticated_headers, sample_encounter_data):
        """Test deleting a creature that doesn't exist."""
        # Create encounter
        encounter_response = client.post(
            "/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter_id = encounter_response.json()["id"]

        fake_creature_id = "00000000-0000-0000-0000-000000000000"

        response = client.delete(
            f"/encounters/{encounter_id}/creatures/{fake_creature_id}",
            headers=authenticated_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
