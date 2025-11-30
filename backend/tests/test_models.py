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
            email="test@example.com",
            password_hash="hashedpass123",
        )
        test_db_session.add(user)
        test_db_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert isinstance(user.created_at, datetime)
    
    def test_user_unique_email(self, test_db_session):
        """Test that emails must be unique."""
        user1 = models.User(
            email="test@example.com",
            password_hash="hashedpass123",
        )
        user2 = models.User(
            email="test@example.com",
            password_hash="hashedpass456",
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
        """Test creating a creature with encounter."""
        # Create user and encounter first
        user = models.User(
            email="test@example.com",
            password_hash="hashedpass123",
        )
        test_db_session.add(user)
        test_db_session.commit()
        
        encounter = models.Encounter(
            name="Test Encounter",
            user_id=user.id,
        )
        test_db_session.add(encounter)
        test_db_session.commit()
        
        creature = models.Creature(
            name="Goblin",
            initiative=15,
            creature_type=enums.CreatureType.ENEMY,
            encounter_id=encounter.id,
        )
        test_db_session.add(creature)
        test_db_session.commit()
        
        assert creature.id is not None
        assert creature.name == "Goblin"
        assert creature.initiative == 15
        assert creature.creature_type == enums.CreatureType.ENEMY
    
    def test_creature_with_encounter(self, test_db_session):
        """Test creating a creature linked to encounter."""
        user = models.User(
            email="test@example.com",
            password_hash="hashedpass123",
        )
        test_db_session.add(user)
        test_db_session.commit()
        
        encounter = models.Encounter(
            name="Battle",
            user_id=user.id,
        )
        test_db_session.add(encounter)
        test_db_session.commit()
        
        creature = models.Creature(
            name="Fighter",
            initiative=18,
            creature_type=enums.CreatureType.PLAYER,
            encounter_id=encounter.id,
        )
        test_db_session.add(creature)
        test_db_session.commit()
        
        assert creature.encounter_id == encounter.id
        assert creature.encounter.user.email == "test@example.com"


@pytest.mark.unit
class TestEncounterModel:
    """Tests for the Encounter model."""
    
    def test_encounter_creation(self, test_db_session):
        """Test creating an encounter."""
        user = models.User(
            email="test@example.com",
            password_hash="hashedpass123",
        )
        test_db_session.add(user)
        test_db_session.commit()
        
        encounter = models.Encounter(
            name="Goblin Ambush",
            user_id=user.id,
        )
        test_db_session.add(encounter)
        test_db_session.commit()
        
        assert encounter.id is not None
        assert encounter.name == "Goblin Ambush"
        assert encounter.user_id == user.id
    
    def test_encounter_with_creatures(self, test_db_session):
        """Test encounter with multiple creatures."""
        user = models.User(
            email="test@example.com",
            password_hash="hashedpass123",
        )
        test_db_session.add(user)
        test_db_session.commit()
        
        encounter = models.Encounter(
            name="Battle",
            user_id=user.id,
        )
        test_db_session.add(encounter)
        test_db_session.commit()
        
        creature1 = models.Creature(
            name="Goblin 1",
            initiative=12,
            creature_type=enums.CreatureType.ENEMY,
            encounter_id=encounter.id,
        )
        creature2 = models.Creature(
            name="Goblin 2",
            initiative=8,
            creature_type=enums.CreatureType.ENEMY,
            encounter_id=encounter.id,
        )
        
        test_db_session.add_all([creature1, creature2])
        test_db_session.commit()
        
        assert len(encounter.creatures) == 2
        assert encounter.creatures[0].name in ["Goblin 1", "Goblin 2"]
