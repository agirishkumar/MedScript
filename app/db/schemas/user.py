# app/db/schemas/user.py

'''
Defines Pydantic schemas for a users table.
'''

from pydantic import BaseModel
from enum import Enum

class RoleEnum(int, Enum):
    PATIENT = 1
    DOCTOR = 2

class UserCreate(BaseModel):
    email: str
    password: str
    role: RoleEnum
