import unittest
from app import *
from app.utils.auth_util import Encrypt, JWTTokenHelper, authenticate_user, validate_user
from datetime import datetime, timedelta
from app.utils.http_errors import UnauthorizedError, ForbiddenError, BadRequestError
import jwt
from unittest.mock import patch, MagicMock
from app.db.crud.user import get_user, get_user_by_email
from sqlalchemy.orm import Session, sessionmaker
import pytest


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

class TestEncrypt(unittest.TestCase):

    def setUp(self):
        """
        Set up any necessary test dependencies before each test.
        """
        self.encrypt = Encrypt()
        self.value = "test123"
        self.hashed_value = self.encrypt.hash(self.value)

    def test_hash(self):
        """
        Test that the hash method returns a hashed value that is not equal to the plain text.
        """
        hashed_value = self.encrypt.hash(self.value)
        self.assertNotEqual(self.value, hashed_value)
        self.assertTrue(isinstance(hashed_value, str))
        self.assertGreater(len(hashed_value), 0) 

    def test_verify_correct(self):
        """
        Test that the verify method returns True when the plain text matches the hashed value.
        """
        result = self.encrypt.verify(self.value, self.hashed_value)
        self.assertTrue(result)

    def test_verify_incorrect(self):
        """
        Test that the verify method returns False when the plain text does not match the hashed value.
        """
        wrong_value = "test"
        result = self.encrypt.verify(wrong_value, self.hashed_value)
        self.assertFalse(result)

# Mock settings for testing purposes
class MockSettings:
    JWT_SECRET_KEY = "test_secret"
    JWT_REFRESH_SECRET_KEY = "test_refresh_secret"
    ACCESS_TOKEN_EXPIRY_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_MINUTES = 30
    ENCODE_ALGORITHM = "HS256"

mock_settings = MockSettings()

class TestJWTTokenHelper(unittest.TestCase):

    def setUp(self):
        self.jwt_helper = JWTTokenHelper(config = mock_settings)
        self.data = {"email": "test@test.com", "role": "1"}

    def test_generate_token(self):
        """
        Test that a valid JWT token is generated with the correct structure.
        """
        token = self.jwt_helper.generate_token(self.data)
        self.assertTrue(isinstance(token, str))
        decoded_payload = jwt.decode(token, mock_settings.JWT_SECRET_KEY, algorithms=[mock_settings.ENCODE_ALGORITHM])
        self.assertEqual(decoded_payload["sub"], self.data["email"])
        self.assertEqual(decoded_payload["role"], self.data["role"])

    def test_refresh_token(self):
        """
        Test that a valid JWT refresh token is generated with the correct structure.
        """
        token = self.jwt_helper.refresh_token(self.data)
        self.assertTrue(isinstance(token, str))
        decoded_payload = jwt.decode(token, mock_settings.JWT_REFRESH_SECRET_KEY, algorithms=[mock_settings.ENCODE_ALGORITHM])
        self.assertEqual(decoded_payload["sub"], self.data["email"])
        self.assertEqual(decoded_payload["role"], self.data["role"])

    def test_verify_token_valid(self):
        """
        Test that a valid JWT token is correctly verified and decoded.
        """
        token = self.jwt_helper.generate_token(self.data)
        payload = self.jwt_helper.verify_token(token)
        self.assertEqual(payload["sub"], self.data["email"])
        self.assertEqual(payload["role"], self.data["role"])

    def test_verify_token_expired(self):
        """
        Test that an expired JWT token raises an UnauthorizedError.
        """
        expired_token = jwt.encode(
            {"sub": self.data["email"], "role": self.data["role"], "exp": datetime.utcnow() - timedelta(minutes=1)},
            mock_settings.JWT_SECRET_KEY, 
            algorithm=mock_settings.ENCODE_ALGORITHM
        )
        with self.assertRaises(UnauthorizedError) as context:
            self.jwt_helper.verify_token(expired_token)
        print(str(context.exception.message))
        self.assertEqual(str(context.exception.message), "Token expired")

    def test_verify_token_invalid(self):
        """
        Test that an invalid JWT token raises an UnauthorizedError.
        """
        invalid_token = "invalid.token.here"
        with self.assertRaises(UnauthorizedError) as context:
            self.jwt_helper.verify_token(invalid_token)
        self.assertEqual(str(context.exception.message), "Invalid token")

@pytest.mark.usefixtures("mock_db_session")
class TestUserValidation(unittest.TestCase):

    def test_validate_user(self):
        with patch("app.db.crud.user.get_user") as mock_get_user:
            mock_get_user.return_value = MagicMock(spec=get_user)
            result = validate_user(id=1, db=mock_db_session)
            self.assertTrue(result)
        
    def test_validate_user_invalid(self):
        with patch("app.db.crud.user.get_user") as mock_get_user:
            mock_get_user.side_effect = Exception("Invalid")
            with self.assertRaises(UnauthorizedError) as context:
                result = validate_user(id=1, db=mock_db_session)    
            self.assertEqual(str(context.exception.message), "Not a registered user")

class TestAuthenticateUser(unittest.TestCase):

    def test_authenticate_user(self):
        with patch("app.db.crud.user.get_user_by_email") as mock_get_user_by_email, patch("app.utils.auth_util.Encrypt.verify") as mock_verify:
            mock_user = MagicMock(spec=get_user_by_email)
            mock_user.password = ""
            mock_get_user_by_email.return_value = mock_user
            mock_verify.return_value = True

            result = authenticate_user(email="test@test.com", password="Test123", db=MagicMock())
            mock_verify.assert_called_once()
            self.assertEqual(result, mock_user)
        
    def test_authenticate_user_incorrect_details(self):
        with patch("app.db.crud.user.get_user_by_email") as mock_get_user_by_email, patch("app.utils.auth_util.Encrypt.verify") as mock_verify:
            mock_user = MagicMock(spec=get_user_by_email)
            mock_user.password = ""
            mock_get_user_by_email.return_value = mock_user
            mock_verify.return_value = False
            with self.assertRaises(BadRequestError) as context:
                authenticate_user(email="test@test.com", password="wrong_password", db=MagicMock())
            mock_verify.assert_called_once()
            self.assertEqual(str(context.exception.message), "User details are incorrect")



if __name__ == '__main__':
    unittest.main()
