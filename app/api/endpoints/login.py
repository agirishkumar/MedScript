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