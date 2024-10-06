# app/api/deps.py

from typing import Generator
from app.db.session import SessionLocal

def get_db() -> Generator:
    """
    Dependency to get a database session.

    Yields a database session.
    Closes the session at the end of the context.
    """
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()