# app/api/deps.py

from typing import Generator
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
import app.utils.auth_util as util
from app.utils.auth_util import JWTTokenHelper
from app.utils.http_errors import UnauthorizedError
from fastapi import Request, HTTPException, Depends

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


def authorize(request: Request, helper = JWTTokenHelper(), db: Session = Depends(get_db)) -> dict[str:str]:
    """
    Verifies the authorization token sent as part of the request and returns the user_id and the user role if valid.
    
    Validates the bearer token and adds user details to the request if the token is valid. If there is no bearer token in the request or the bearer token has expired, raises a HTTP 401 error.

    Returns:
    - dict[str:str] with the user id and role
    """
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code = 401,
            detail = "Bearer Token has to be specified")
    
    try:
        token = token.split(" ")[1]
        # verify token and validate the user
        payload = helper.verify_token(token)
        user_id = payload.get("sub")
        role = payload.get("role")
        util.validate_user(id = user_id, db=db)
        return {"user_id": user_id, "role": role}
    except UnauthorizedError as e:
        raise HTTPException(status_code = 401,
            detail = e.message)

    