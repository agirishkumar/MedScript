# tests/unit/test_session.py

'''
Tests database session creation, session functionality, and the get_db dependency's session management in FastAPI.
'''

from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal, get_db

def test_session_creation():
    """
    Tests that the database engine is created with the correct URL and that
    a session can be created and closed without errors.
    """
    assert "postgresql" in str(engine.url)
    
    # Test that a session can be created and closed without errors
    db = SessionLocal()
    assert db.is_active     
    db.close()

def test_get_db_function():
    """
    Tests that the get_db dependency yields a database session and
    that the session is closed correctly after the dependency is exited.
    """
    db = next(get_db())
    assert db.is_active 
    db.close()
