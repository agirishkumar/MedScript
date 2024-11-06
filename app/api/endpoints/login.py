# app/api/endpoints/login.py

'''
this file contains all the endpoints for the login resource
'''

from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.schemas.user import UserCreate
from app.utils.http_errors import BadRequestError, NotFoundError
import app.utils.auth_util as util
from app.utils.auth_util import JWTTokenHelper
from app.api.deps import get_db
import app.db.crud.user as user_crud
from app.utils.auth_util import Encrypt

router = APIRouter(prefix="/user")

# login route 
@router.post("/login", status_code=200)
def login(form_data: OAuth2PasswordRequestForm = Depends(), helper = JWTTokenHelper(), db: Session = Depends(get_db)):
    """
    This endpoint is used to authenticate a user and obtain a JWT access token.

    It takes in a username and a password and returns a JWT access token which can be used to access protected endpoints.

    Args:
    - form_data (OAuth2PasswordRequestForm): The form data containing the username and password of the user.
    - helper (JWTTokenHelper): An instance of the JWTTokenHelper class used to generate a JWT access token.
    - db (Session): The database session.

    Returns:
    - A dictionary containing the JWT access token.

    Raises:
    - HTTPException (400): If the username or password is incorrect.
    - HTTPException (403): If the user is not found.
    """
    try:
        user = util.authenticate_user(form_data.username, form_data.password, db=db)
        access_token = helper.generate_token({"email": user.email, "id": user.user_id, "role": user.role.name})
        return {
            "access_token": access_token
        }
        
    except BadRequestError as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail= "Incorrect email or password"
        )
    
    except NotFoundError as e:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail= "User not found"
        )

@router.post("/register", status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    """
    user.password = Encrypt.hash(user.password)
    db_user = user_crud.create_user(db=db, user=user)
    return {"email": db_user.email, "role": db_user.role}