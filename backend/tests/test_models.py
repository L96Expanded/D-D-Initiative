"""Unit tests for database models."""
import pytest
from datetime import datetime
from app.models import models, enums


@pytest.mark.unit
class TestUserModel:
    """Tests for the User model."""
    
    def test_user_creation(self, test_db_session):
        """Test creating a user."""
        user = models.User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpass123",
        )
        test_db_session.add(user)
        test_db_session.commit()
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert isinstance(user.created_at, datetime)
    
    def test_user_unique_username(self, test_db_session):
        """Test that usernames must be unique."""
        user1 = models.User(
            username="testuser",
            email="test1@example.com",
            hashed_password="hashedpass123",
        )
        user2 = models.User(
            username="testuser",
            email="test2@example.com",
            hashed_password="hashedpass456",
        )
        
        test_db_session.add(user1)
        test_db_session.commit()
        
        test_db_session.add(user2)
        with pytest.raises(Exception):  # Should raise IntegrityError
            test_db_session.commit()


@pytest.mark.unit
class TestCreatureModel:
    """Tests for the Creature model."""
    
    def test_creature_creation(self, test_db_session):
        """Test creating a creature."""
        creature = models.Creature(
            name="Goblin",
            initiative=15,
            hp=20,
            max_hp=20,
            ac=13,
            creature_type=enums.CreatureType.MONSTER,
        )
        test_db_session.add(creature)
        test_db_session.commit()
        
        assert creature.id is not None
        assert creature.name == "Goblin"
        assert creature.initiative == 15
        assert creature.hp == 20
        assert creature.max_hp == 20
        assert creature.ac == 13
    
    def test_creature_with_owner(self, test_db_session):
        """Test creating a creature with an owner."""
        user = models.User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpass123",
        )
        test_db_session.add(user)
        test_db_session.commit()
        
        creature = models.Creature(
            name="Fighter",
            initiative=18,
            hp=30,
            max_hp=30,
            ac=16,
            creature_type=enums.CreatureType.PLAYER_CHARACTER,
            owner_id=user.id,
        )
        test_db_session.add(creature)
        test_db_session.commit()
        
        assert creature.owner_id == user.id
        assert creature.owner.username == "testuser"


@pytest.mark.unit
class TestEncounterModel:
    """Tests for the Encounter model."""
    
    def test_encounter_creation(self, test_db_session):
        """Test creating an encounter."""
        user = models.User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpass123",
        )
        test_db_session.add(user)
        test_db_session.commit()
        
        encounter = models.Encounter(
            name="Goblin Ambush",
            description="A surprise attack",
            owner_id=user.id,
            round_number=1,
        )
        test_db_session.add(encounter)
        test_db_session.commit()
        
        assert encounter.id is not None
        assert encounter.name == "Goblin Ambush"
        assert encounter.round_number == 1
        assert encounter.is_active is True
    
    def test_encounter_with_creatures(self, test_db_session):
        """Test encounter with multiple creatures."""
        user = models.User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpass123",
        )
        test_db_session.add(user)
        test_db_session.commit()
        
        encounter = models.Encounter(
            name="Battle",
            owner_id=user.id,
        )
        test_db_session.add(encounter)
        test_db_session.commit()
        
        creature1 = models.Creature(
            name="Goblin 1",
            initiative=12,
            hp=20,
            max_hp=20,
            ac=13,
            creature_type=enums.CreatureType.MONSTER,
            encounter_id=encounter.id,
        )
        creature2 = models.Creature(
            name="Goblin 2",
            initiative=8,
            hp=20,
            max_hp=20,
            ac=13,
            creature_type=enums.CreatureType.MONSTER,
            encounter_id=encounter.id,
        )
        
        test_db_session.add_all([creature1, creature2])
        test_db_session.commit()
        
        assert len(encounter.creatures) == 2
        assert encounter.creatures[0].name in ["Goblin 1", "Goblin 2"]
