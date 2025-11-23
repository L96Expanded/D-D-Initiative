"""Integration tests for API endpoints."""
import pytest
from fastapi import status


@pytest.mark.integration
class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    def test_health_check(self, client):
        """Test the health endpoint returns 200."""
        response = client.get("/api/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "database" in data


@pytest.mark.integration
class TestUserRegistration:
    """Tests for user registration endpoint."""
    
    def test_register_user_success(self, client, sample_user_data):
        """Test successful user registration."""
        response = client.post("/api/users/register", json=sample_user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
        assert "id" in data
        assert "password" not in data
        assert "hashed_password" not in data
    
    def test_register_duplicate_username(self, client, sample_user_data):
        """Test that duplicate username registration fails."""
        # Register first user
        client.post("/api/users/register", json=sample_user_data)
        
        # Try to register with same username
        response = client.post("/api/users/register", json=sample_user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_invalid_email(self, client, sample_user_data):
        """Test registration with invalid email."""
        sample_user_data["email"] = "invalid-email"
        response = client.post("/api/users/register", json=sample_user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_weak_password(self, client, sample_user_data):
        """Test registration with weak password."""
        sample_user_data["password"] = "weak"
        response = client.post("/api/users/register", json=sample_user_data)
        
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]


@pytest.mark.integration
class TestAuthentication:
    """Tests for authentication endpoints."""
    
    def test_login_success(self, client, sample_user_data):
        """Test successful login."""
        # Register user first
        client.post("/api/users/register", json=sample_user_data)
        
        # Login
        response = client.post(
            "/api/auth/token",
            data={
                "username": sample_user_data["username"],
                "password": sample_user_data["password"],
            },
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, sample_user_data):
        """Test login with wrong password."""
        # Register user first
        client.post("/api/users/register", json=sample_user_data)
        
        # Try login with wrong password
        response = client.post(
            "/api/auth/token",
            data={
                "username": sample_user_data["username"],
                "password": "WrongPassword123!",
            },
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post(
            "/api/auth/token",
            data={
                "username": "nonexistent",
                "password": "Password123!",
            },
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestCreatureEndpoints:
    """Tests for creature management endpoints."""
    
    def test_create_creature(self, client, authenticated_headers, sample_creature_data):
        """Test creating a creature."""
        response = client.post(
            "/api/creatures/",
            json=sample_creature_data,
            headers=authenticated_headers,
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == sample_creature_data["name"]
        assert data["initiative"] == sample_creature_data["initiative"]
        assert "id" in data
    
    def test_get_creatures_list(self, client, authenticated_headers, sample_creature_data):
        """Test retrieving list of creatures."""
        # Create a creature first
        client.post(
            "/api/creatures/",
            json=sample_creature_data,
            headers=authenticated_headers,
        )
        
        # Get list
        response = client.get("/api/creatures/", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_creature_by_id(self, client, authenticated_headers, sample_creature_data):
        """Test retrieving a specific creature."""
        # Create creature
        create_response = client.post(
            "/api/creatures/",
            json=sample_creature_data,
            headers=authenticated_headers,
        )
        creature_id = create_response.json()["id"]
        
        # Get creature
        response = client.get(
            f"/api/creatures/{creature_id}",
            headers=authenticated_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == creature_id
        assert data["name"] == sample_creature_data["name"]
    
    def test_update_creature(self, client, authenticated_headers, sample_creature_data):
        """Test updating a creature."""
        # Create creature
        create_response = client.post(
            "/api/creatures/",
            json=sample_creature_data,
            headers=authenticated_headers,
        )
        creature_id = create_response.json()["id"]
        
        # Update creature
        updated_data = sample_creature_data.copy()
        updated_data["hp"] = 10
        response = client.put(
            f"/api/creatures/{creature_id}",
            json=updated_data,
            headers=authenticated_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["hp"] == 10
    
    def test_delete_creature(self, client, authenticated_headers, sample_creature_data):
        """Test deleting a creature."""
        # Create creature
        create_response = client.post(
            "/api/creatures/",
            json=sample_creature_data,
            headers=authenticated_headers,
        )
        creature_id = create_response.json()["id"]
        
        # Delete creature
        response = client.delete(
            f"/api/creatures/{creature_id}",
            headers=authenticated_headers,
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's deleted
        get_response = client.get(
            f"/api/creatures/{creature_id}",
            headers=authenticated_headers,
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_creature_unauthorized(self, client, sample_creature_data):
        """Test that creating creature without auth fails."""
        response = client.post("/api/creatures/", json=sample_creature_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestEncounterEndpoints:
    """Tests for encounter management endpoints."""
    
    def test_create_encounter(self, client, authenticated_headers, sample_encounter_data):
        """Test creating an encounter."""
        response = client.post(
            "/api/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == sample_encounter_data["name"]
        assert "id" in data
    
    def test_get_encounters_list(self, client, authenticated_headers, sample_encounter_data):
        """Test retrieving list of encounters."""
        # Create an encounter first
        client.post(
            "/api/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        
        # Get list
        response = client.get("/api/encounters/", headers=authenticated_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_add_creature_to_encounter(
        self, client, authenticated_headers, sample_encounter_data, sample_creature_data
    ):
        """Test adding a creature to an encounter."""
        # Create encounter
        encounter_response = client.post(
            "/api/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter_id = encounter_response.json()["id"]
        
        # Create creature with encounter_id
        sample_creature_data["encounter_id"] = encounter_id
        creature_response = client.post(
            "/api/creatures/",
            json=sample_creature_data,
            headers=authenticated_headers,
        )
        
        assert creature_response.status_code == status.HTTP_201_CREATED
        
        # Get encounter and verify creature is in it
        response = client.get(
            f"/api/encounters/{encounter_id}",
            headers=authenticated_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "creatures" in data
        assert len(data["creatures"]) > 0
    
    def test_update_encounter_round(
        self, client, authenticated_headers, sample_encounter_data
    ):
        """Test updating encounter round number."""
        # Create encounter
        create_response = client.post(
            "/api/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter_id = create_response.json()["id"]
        
        # Update round number
        response = client.patch(
            f"/api/encounters/{encounter_id}/round",
            json={"round_number": 5},
            headers=authenticated_headers,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["round_number"] == 5
    
    def test_delete_encounter(self, client, authenticated_headers, sample_encounter_data):
        """Test deleting an encounter."""
        # Create encounter
        create_response = client.post(
            "/api/encounters/",
            json=sample_encounter_data,
            headers=authenticated_headers,
        )
        encounter_id = create_response.json()["id"]
        
        # Delete encounter
        response = client.delete(
            f"/api/encounters/{encounter_id}",
            headers=authenticated_headers,
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
