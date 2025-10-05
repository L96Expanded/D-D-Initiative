import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from app.models.database import get_db, SessionLocal


class TestDatabaseSession:
    """Test database session management."""

    def test_get_db_success(self):
        """Test successful database session creation and cleanup."""
        # Test the get_db generator function
        db_gen = get_db()
        db = next(db_gen)
        
        # Verify we get a valid session
        assert db is not None
        assert hasattr(db, 'query')
        assert hasattr(db, 'commit')
        assert hasattr(db, 'close')
        
        # Complete the generator to trigger finally block
        try:
            next(db_gen)
        except StopIteration:
            pass  # Expected behavior

    def test_get_db_with_exception(self):
        """Test database session cleanup when exception occurs."""
        db_gen = get_db()
        db = next(db_gen)
        
        # Verify we get a valid session
        assert db is not None
        
        # Simulate an exception and verify cleanup
        try:
            # Throw an exception into the generator
            db_gen.throw(Exception("Test exception"))
        except Exception:
            pass  # Expected behavior - generator should handle cleanup

    def test_get_db_session_close_on_exception(self):
        """Test that database session is properly closed even when exception occurs."""
        with patch('app.models.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            db_gen = get_db()
            db = next(db_gen)
            
            # Verify session was created
            mock_session_local.assert_called_once()
            assert db == mock_session
            
            # Simulate an exception
            try:
                db_gen.throw(SQLAlchemyError("Database error"))
            except SQLAlchemyError:
                pass
            
            # Verify session.close() was called in finally block
            mock_session.close.assert_called_once()

    def test_get_db_session_close_on_normal_completion(self):
        """Test that database session is properly closed on normal completion."""
        with patch('app.models.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            db_gen = get_db()
            db = next(db_gen)
            
            # Verify session was created
            mock_session_local.assert_called_once()
            assert db == mock_session
            
            # Complete generator normally
            try:
                next(db_gen)
            except StopIteration:
                pass
            
            # Verify session.close() was called in finally block
            mock_session.close.assert_called_once()

    def test_database_session_factory(self):
        """Test database session factory configuration."""
        # Test that SessionLocal creates valid sessions
        session = SessionLocal()
        
        # Verify session properties
        assert session is not None
        assert hasattr(session, 'query')
        assert hasattr(session, 'commit')
        assert hasattr(session, 'rollback')
        assert hasattr(session, 'close')
        
        # Clean up
        session.close()

    def test_get_db_multiple_sessions(self):
        """Test that get_db creates independent sessions."""
        # Create two separate sessions
        db_gen1 = get_db()
        db_gen2 = get_db()
        
        db1 = next(db_gen1)
        db2 = next(db_gen2)
        
        # Verify they are different session instances
        assert db1 is not db2
        
        # Clean up both generators
        for gen in [db_gen1, db_gen2]:
            try:
                next(gen)
            except StopIteration:
                pass

    def test_database_session_properties(self):
        """Test database session configuration properties."""
        with patch('app.models.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            # Test get_db creates session with correct factory
            db_gen = get_db()
            db = next(db_gen)
            
            # Verify SessionLocal was called (session factory)
            mock_session_local.assert_called_once()
            
            # Complete generator
            try:
                next(db_gen)
            except StopIteration:
                pass
            
            # Verify cleanup
            mock_session.close.assert_called_once()


class TestDatabaseConfiguration:
    """Test database configuration and setup."""

    def test_database_engine_configuration(self):
        """Test database engine configuration."""
        from app.models.database import engine
        
        # Verify engine exists and has expected properties
        assert engine is not None
        assert hasattr(engine, 'connect')  # Changed from execute to connect

    def test_database_base_configuration(self):
        """Test database base class configuration."""
        from app.models.database import Base
        
        # Verify Base class exists and has expected properties
        assert Base is not None
        assert hasattr(Base, 'metadata')
        assert hasattr(Base, 'registry')

    def test_session_local_configuration(self):
        """Test SessionLocal configuration."""
        from app.models.database import SessionLocal
        
        # Verify SessionLocal exists and is callable
        assert SessionLocal is not None
        assert callable(SessionLocal)
        
        # Test creating a session
        session = SessionLocal()
        assert session is not None
        session.close()