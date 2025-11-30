"""Pytest configuration and shared fixtures for all tests."""
import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add the parent directory to the path so we can import the app
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.models.database import Base, get_db
from main import app


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(test_db_session) -> TestClient:
    """Create a test client with a test database session."""
    
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
    }


@pytest.fixture
def sample_creature_data():
    """Provides sample creature data for testing."""
    return {
        "name": "Goblin",
        "initiative": 15,
        "creature_type": "enemy",
        "image_url": None,
    }


@pytest.fixture
def sample_encounter_data():
    """Sample encounter data for testing."""
    return {
        "name": "Goblin Ambush",
        "background_image": None,
    }


@pytest.fixture
def authenticated_headers(client, sample_user_data):
    """Create an authenticated user and return authorization headers."""
    # Register user
    sample_user_data["confirm_password"] = sample_user_data["password"]
    response = client.post("/auth/register", json=sample_user_data)
    
    # Get token from registration response
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}
