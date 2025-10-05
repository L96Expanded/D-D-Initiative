import pytest
import asyncio
from typing import Generator, AsyncGenerator
import uuid
from uuid import UUID
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile

from main import app
from app.models.database import Base, get_db
from app.models.models import User, Encounter, Creature
from app.models.enums import CreatureType
from app.utils.auth import hash_password
from app.config import settings


# Database Setup for Testing
@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture
def db_session(test_engine):
    """Create a database session for testing."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    
    # Override the get_db dependency
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        app.dependency_overrides.clear()

@pytest.fixture
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
async def async_client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as async_test_client:
        yield async_test_client

@pytest.fixture
def test_user_data():
    """Test user data for registration"""
    import time
    import random
    timestamp = int(time.time() * 1000)  # Get current timestamp in milliseconds
    random_suffix = random.randint(1000, 9999)
    return {
        "email": f"test-{timestamp}-{random_suffix}@example.com",  # More unique email
        "password": "testpassword123",
        "confirm_password": "testpassword123"
    }

@pytest.fixture
def test_user(db_session, test_user_data):
    """Create a test user in the database"""
    hashed_password = hash_password(test_user_data["password"])
    user = User(
        email=test_user_data["email"],
        password_hash=hashed_password  # Correct field name
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(client, test_user_data):
    """Get authentication headers for a test user"""
    # Register the user first
    response = client.post("/auth/register", json=test_user_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_encounter_data():
    """Test encounter data"""
    return {
        "name": "Test Encounter",
        "background_image": "https://example.com/test_encounter.jpg"
    }

@pytest.fixture
def test_encounter(client, auth_headers, test_encounter_data):
    """Create a test encounter"""
    response = client.post("/encounters/", json=test_encounter_data, headers=auth_headers)
    return response.json()

@pytest.fixture
def test_creature(db_session, test_encounter):
    """Create a test creature"""
    creature = Creature(
        name="Test Dragon",
        initiative=15,
        creature_type=CreatureType.ENEMY,
        image_url="https://example.com/dragon.jpg",
        encounter_id=UUID(test_encounter["id"])  # Convert string UUID to UUID object
    )
    db_session.add(creature)
    db_session.commit()
    db_session.refresh(creature)
    
    # Return as dict for consistency with other fixtures
    return {
        "id": creature.id,
        "name": creature.name,
        "initiative": creature.initiative,
        "creature_type": creature.creature_type.value,
        "image_url": creature.image_url,
        "encounter_id": creature.encounter_id,
        "created_at": creature.created_at
    }

@pytest.fixture
def test_encounter_with_creatures(db_session, test_user):
    """Create a test encounter with multiple creatures"""
    # Create encounter
    encounter = Encounter(
        name="Test Encounter with Creatures",
        background_image="https://example.com/test_encounter_bg.jpg",
        user_id=test_user.id
    )
    db_session.add(encounter)
    db_session.flush()  # Get the encounter ID
    
    # Create creatures
    creatures_data = [
        {
            "name": "Dragon",
            "initiative": 20,
            "creature_type": CreatureType.ENEMY,
            "image_url": "https://example.com/dragon.jpg"
        },
        {
            "name": "Knight",
            "initiative": 15,
            "creature_type": CreatureType.PLAYER,
            "image_url": "https://example.com/knight.jpg"
        }
    ]
    
    for creature_data in creatures_data:
        creature = Creature(
            name=creature_data["name"],
            initiative=creature_data["initiative"],
            creature_type=creature_data["creature_type"],
            image_url=creature_data["image_url"],
            encounter_id=encounter.id
        )
        db_session.add(creature)
    
    db_session.commit()
    db_session.refresh(encounter)
    
    return {
        "id": encounter.id,
        "name": encounter.name,
        "background_image": encounter.background_image,
        "user_id": encounter.user_id,
        "created_at": encounter.created_at
    }

@pytest.fixture
def temp_upload_dir():
    """Create a temporary directory for file uploads during testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_upload_dir = settings.UPLOAD_DIR
        settings.UPLOAD_DIR = temp_dir
        yield temp_dir
        settings.UPLOAD_DIR = original_upload_dir

@pytest.fixture
def sample_image_file():
    """Create a sample image file for upload testing"""
    from PIL import Image
    import io
    
    # Create a simple test image
    image = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return ("test_image.png", img_bytes, "image/png")