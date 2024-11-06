# app/utils/auth_util.py

'''
Provides methods for user authentication, JWT token generation, verification, and encryption utilities for secure password handling.
'''

from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.utils.http_errors import BadRequestError, UnauthorizedError, ForbiddenError,NotFoundError
from sqlalchemy.orm import Session
from app.core.config import Settings
import app.db.crud.user as user_crud
from app.db.models.user import User
import jwt
from jwt import ExpiredSignatureError

# config
ACCESS_TOKEN_EXPIRY_MINUTES = 100
REFRESH_TOKEN_EXPIRE_MINUTES = 100
ENCODE_ALGORITHM = "HS256"

class Encrypt:
    """
    Provides methods to securely hash a value using bcrypt and verify it against a hashed value.
    """

    context = CryptContext(schemes = ['bcrypt'])

    @staticmethod
    def hash(value: str) -> str:
        """
        Hashes a given string value.

        Parameters:
        - value: The plain text string to be hashed

        Returns:
        - A hashed representation of the input value
        """
        return Encrypt.context.hash(value)

    @staticmethod
    def verify(value: str, hashed_value: str) -> bool:
        """
        Verifies if the given plain text value matches the provided hashed value.

        Parameters:
        - value: The plain text string to verify.
        - hashed_value: The hashed string to compare against.

        Returns:
        - True if the plain text matches the hashed value; False otherwise.
        """   
        return Encrypt.context.verify(value, hashed_value)
    

class JWTTokenHelper:
    """
    Handles JWT token operations for authentication and authorization.
    """

    def __init__(self, config = Settings()):
        self.config = config
    
    def generate_token(self, data: dict[str: str], expire_minutes: int = None) -> str:
        """
        Generates a JWT access token with given data and an expiration time.

        Parameters:
        - data: A dictionary containing user information
        - expire_minutes: Optional integer specifying the token's expiration time in minutes. Defaults to a pre-configured value if not provided.

        Returns:
        - A JWT access token as a string.
        """

        expire_minutes = datetime.now(tz=timezone.utc) + (timedelta(minutes=expire_minutes) if expire_minutes else timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES))
        encode_dict = {"sub": data["email"], 
                       "role": data["role"],
                       "exp": int(expire_minutes.timestamp())}
        jwt_token = jwt.encode(encode_dict,  self.config.JWT_SECRET_KEY, ENCODE_ALGORITHM)
        return jwt_token

    
    def refresh_token(self, data: dict[str: str], expire_minutes: int = None) -> str:
        """
        Generates a new JWT refresh token.

        Parameters:
        - data: A dictionary containing user information
        - expire_minutes: Optional integer specifying the refresh token's expiration time. Defaults to a pre-configured value if not provided.

        Returns:
        - A JWT refresh token as a string.
        """
        expire_minutes = datetime.now(tz=timezone.utc) + (timedelta(minutes = expire_minutes) if expire_minutes else timedelta(minutes = REFRESH_TOKEN_EXPIRE_MINUTES))

        encode_dict = {"sub": data["email"], 
                       "role": data["role"],
                       "exp": expire_minutes}
        jwt_token = jwt.encode(encode_dict,  self.config.JWT_REFRESH_SECRET_KEY, ENCODE_ALGORITHM)
        return jwt_token

   
    def verify_token(self, token: str):
        """
        Verifies the given JWT access token and returns the payload.

        Parameters:
        - token: The JWT token as a string

        Returns:
        - The decoded payload if the token is valid.
        
        Raises:
        - UnauthorizedError: If the token is expired or invalid.
        """
        try:
            payload = jwt.decode(
                token, self.config.JWT_SECRET_KEY, algorithms=[ENCODE_ALGORITHM]
            ) 
        except ExpiredSignatureError:
            raise UnauthorizedError(message = "Token expired")
    
        except Exception as e: 
            raise UnauthorizedError(message = "Invalid token")
        
        # token_expiry = payload.get("exp")

        # if datetime.fromtimestamp(token_expiry) < datetime.now():
        #     raise UnauthorizedError(message = "Token expired")

        print("Payload: ", payload)
        
        return payload
    

def validate_user(id: int, db: Session) -> bool:
    """
    Validates that the user exists, given the user id. Else, returns a Forbidden error.

    Args:
    id (int): The id of the user.
    """
    try:
        user_crud.get_user(db=db, user_id=id)
        return True
    except Exception as e:
        raise UnauthorizedError("Not a registered user")
    
def authenticate_user(email: str, password: str, db: Session) -> User:
    """
    Validates that the user exists, given the email and role and returns the user id. Else, returns a Forbidden error.

    Args:
    email (str): The email of the user.
    password(str): The user password.
    role (int): The user role.
    """
    try:
        db_user = user_crud.get_user_by_email(db=db, email=email)
    except Exception as e:
        raise NotFoundError("User not found")
    
    if not Encrypt.verify(password, db_user.password):
        raise BadRequestError("User details are incorrect")
    
    return db_user