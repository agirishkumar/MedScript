# tests/unit/test_login_endpoint.py

'''
Tests user registration, login functionality, and error handling for existing, incorrect, and unregistered users.
'''

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.api.deps import get_db
from app.db.models.user import User
from app.core.config import settings
from fastapi import HTTPException
from app.utils.http_errors import BadRequestError, NotFoundError

@pytest.fixture(scope="module")
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

@pytest.fixture(scope="module")
def test_client(mock_db_session):
    """
    Creates a FastAPI test client with a test database session.

    Uses the `test_db` fixture to create a database session, and overrides the
    `get_db` dependency to use the test session. This allows the test client to
    interact with the test database.

    Yields the test client.
    """
    def override_get_db():
        """
        Overrides the get_db dependency to use the test database session.

        Yields the test session, and rolls back the session at the end of the
        context.
        """
        try:
            yield mock_db_session
        finally:
            mock_db_session.rollback()
    
    with patch("app.db.base.init"):
        from app.main import app
        app.dependency_overrides[get_db] = override_get_db
        with TestClient(app) as client:
            yield client
        app.dependency_overrides.clear()

def test_register(test_client):
    """
    Tests that a user can register successfully with valid data.

    Creates a new user with valid data and asserts that the HTTP 201 response is returned, with user data.
    """

    with patch("app.utils.auth_util.Encrypt") as mock_encrypt, patch("app.db.crud.user_crud.create_user")as mock_create_user:
        user_data = {
        "email": "test@test.com",
        "password": "Test123",
        "role": "1"
        }
        mock_encrypt.return_value = "Test123"
        mock_user = MagicMock(spec=User)
        mock_user.email = "test@test.com"
        mock_user.password = "Test123"
        mock_user.role = "1"
        mock_create_user.return_value = mock_user
        

        response = test_client.post(f"{settings.API_V1_STR}/user/register", json = user_data)
        assert response.status_code == 201
        assert response.json()["email"] == user_data["email"]
        assert response.json()["role"] == user_data["role"]

def test_register_existing_user(test_client):
    """
    Tests that HTTP 400 is returned when an existing user registers.
    """
    with patch("app.utils.auth_util.Encrypt") as mock_encrypt, patch("app.db.crud.user_crud.create_user")as mock_create_user:
        user_data = {
        "email": "test@test.com",
        "password": "Test123",
        "role": "1"
        }
        mock_encrypt.return_value = "Test123"
        mock_create_user.side_effect = HTTPException(status_code=400, detail="Email already registered")
        response = test_client.post(f"{settings.API_V1_STR}/user/register", json = user_data)
        assert response.status_code == 400
        assert response.json() == {"detail": "Email already registered"}

def test_login(test_client):
    """
    Verify that a user can log in successfully and receive an access token
    """

    with patch("app.utils.auth_util.JWTTokenHelper.generate_token") as mock_generate_token, patch("app.utils.auth_util.authenticate_user")as mock_authenticate_user:
        mock_user = MagicMock(spec=User)
        mock_user.email = "test@test.com"
        mock_role = MagicMock()
        mock_role.name = "PATIENT"
        mock_user.role = mock_role
        mock_authenticate_user.return_value = mock_user
        mock_generate_token.return_value = "Bearer token"

        response = test_client.post(f"{settings.API_V1_STR}/user/login", data = {'username': 'test@test.com', 'password': 'Test123'})
        assert response.status_code == 200
        assert response.json()["access_token"] == "Bearer token"
    
def test_login_incorrect_credentials(test_client):
    """
    Validates that the application raises a 400 Bad Request error when incorrect credentials are provided.
    """

    with patch("app.utils.auth_util.authenticate_user")as mock_authenticate_user:
        mock_authenticate_user.side_effect = BadRequestError("User details are incorrect")

        response = test_client.post(f"{settings.API_V1_STR}/user/login", data = {'username': 'test@test.com', 'password': ''})
        assert response.status_code == 400
        assert response.json() == {"detail": "Incorrect email or password"}

def test_login_invalid_user(test_client):
    """
    Validates that the application raises a 403 Forbidden error when the user is not a registered user.
    """

    with patch("app.utils.auth_util.authenticate_user")as mock_authenticate_user:
        mock_authenticate_user.side_effect = NotFoundError("User not found")

        response = test_client.post(f"{settings.API_V1_STR}/user/login", data = {'username': 'test@test.com', 'password': ''})
        assert response.status_code == 403
        assert response.json() == {"detail": "User not found"}

