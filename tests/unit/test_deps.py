# tests/unit/test_deps.py

from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from app.api.deps import get_db

def test_get_db():
    """
    Test that get_db yields a session and closes it correctly.
    """

    # Mock SessionLocal to return a mock session
    with patch("app.api.deps.SessionLocal") as mock_session_local:
        mock_session = MagicMock(spec=Session)
        mock_session_local.return_value = mock_session

        # Use the get_db generator
        generator = get_db()
        db_session = next(generator)

        # Check if we get a session and it's an instance of the mocked Session
        assert db_session == mock_session
        assert isinstance(db_session, Session)
        
        # Close the generator to trigger the finally block
        try:
            next(generator)  # Exhaust the generator to trigger the finally block
        except StopIteration:
            pass

        # Verify that the session's close method was called exactly once
        mock_session.close.assert_called_once()
