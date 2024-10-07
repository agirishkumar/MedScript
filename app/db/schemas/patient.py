# app/db/schemas/patient.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class PatientBase(BaseModel):
    name: str
    age: int
    email: EmailStr

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[EmailStr] = None

class Patient(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True