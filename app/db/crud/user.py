# app/db/crud/user.py

'''
This file contains all the CRUD operations for the user table.
'''

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models.user import User, Role
from ..schemas.user import UserCreate
from fastapi import HTTPException

def get_user(db: Session, user_id: int) -> User:
    """
    Retrieve a user by ID.

    Args:
    user_id (int): The ID of the user to be retrieved.

    Returns:
    User: The user with the specified ID.

    Raises:
    HTTPException: 404 Not Found if the user does not exist.
    """
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_user_by_email(db: Session, email: str) -> User:
    """
    Retrieve a user by email.

    Args:
    user_email (str): The email of the patient to be retrieved.

    Returns:
    Patient: The user with the specified email.

    Raises:
    HTTPException: 404 Not Found if the user does not exist.
    """

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """
    Retrieve a list of all the users.

    Args:
    skip (int, optional): The number of records to skip. Defaults to 0.
    limit (int, optional): The number of records to limit to. Defaults to 100.

    Returns:
    List[User]: A list of users.
    """
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user.

    Args:
    user (schemas.patient.UserCreate): The user to be created.

    Returns:
    schemas.user.User: The newly created patient.

    Raises:
    HTTPException: 400 Bad Request if the user is already registered.
    """
    user.role = Role.PATIENT if user.role == 1 else Role.DOCTOR
    db_user = User(email=user.email, password=user.password, role=user.role)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

def delete_user(db: Session, user_id: int) -> User:
    """
    Delete a user by ID.

    Args:
    user_id (int): The ID of the user to be deleted.

    Returns:
    schemas.user.User: The deleted user.

    Raises:
    HTTPException: 404 Not Found if the patient does not exist.
    """
    
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return db_user