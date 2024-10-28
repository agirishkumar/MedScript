# tests/unit/test_deps.py
import unittest
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from app.api.deps import get_db, authorize
from fastapi import HTTPException
from app.utils.http_errors import UnauthorizedError

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

@pytest.fixture
def mock_db_session():
    """
    A pytest fixture that creates a temporary in-memory database session
    for testing purposes.  The session is created using the SQLite in-memory
    database engine, and the tables are created using the Base.metadata.create_all()
    method. The fixture yields the session object, and then closes it after the
    test is finished.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    # Create tables in the in-memory database
    from app.db.base import Base
    Base.metadata.create_all(bind=engine)
    yield db
    db.close()

@pytest.mark.usefixtures("mock_db_session")
class TestAuthorize(unittest.TestCase):
    def test_authorize(self):
        with patch("app.utils.auth_util.JWTTokenHelper.verify_token") as mock_verify, patch("app.utils.auth_util.validate_user") as mock_validate_user:
            # set up
            mock_request = MagicMock()
            mock_request.headers.get.return_value = "Bearer token"
            mock_verify.return_value = {"sub": "test@test.com", "role": "1"}
            mock_validate_user.return_value = True

            result = authorize(mock_request, db=mock_db_session)
            self.assertEqual(result, {"user_id": "test@test.com", "role": "1"})
            mock_validate_user.assert_called_once_with(id="test@test.com", db=mock_db_session)

    def test_authorize_missing_bearer_token(self):
        with patch("app.utils.auth_util.JWTTokenHelper.verify_token") as mock_verify, patch("app.utils.auth_util.validate_user") as mock_validate_user:
            # set up
            mock_request = MagicMock()
            mock_request.headers.get.return_value = None

            # Expect an HTTP 401 error
            with self.assertRaises(HTTPException) as context:
                authorize(mock_request, db=mock_db_session)
            
            self.assertEqual(context.exception.status_code, 401)
            self.assertEqual(context.exception.detail, "Bearer Token has to be specified")
            mock_verify.assert_not_called()
            mock_validate_user.assert_not_called()

    def test_authorize_invalid_token(self):
        with patch("app.utils.auth_util.JWTTokenHelper.verify_token") as mock_verify, patch("app.utils.auth_util.validate_user") as mock_validate_user:
            # set up
            mock_request = MagicMock()
            mock_request.headers.get.return_value = "Bearer token"
            mock_verify.side_effect = UnauthorizedError("Invalid token")

            # Expect an HTTP 401 error
            with self.assertRaises(HTTPException) as context:
                authorize(mock_request, db=mock_db_session)
            
            self.assertEqual(context.exception.status_code, 401)
            self.assertEqual(context.exception.detail, "Invalid token")
            mock_verify.assert_called_once_with("token")
            mock_validate_user.assert_not_called()

    def test_authorize_invalid_user(self):
        with patch("app.utils.auth_util.JWTTokenHelper.verify_token") as mock_verify, patch("app.utils.auth_util.validate_user") as mock_validate_user:
            # set up
            mock_request = MagicMock()
            mock_request.headers.get.return_value = "Bearer token"
            mock_verify.return_value = {"sub": "test@test.com", "role": "1"}
            mock_validate_user.side_effect = UnauthorizedError("Not a registered user")

            # Expect an HTTP 401 error
            with self.assertRaises(HTTPException) as context:
                authorize(mock_request, db=mock_db_session)
            
            self.assertEqual(context.exception.status_code, 401)
            self.assertEqual(context.exception.detail, "Not a registered user")
            mock_verify.assert_called_once_with("token")
            mock_validate_user.assert_called_once_with(id="test@test.com",db=mock_db_session)