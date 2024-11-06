# app/db/schemas/doctor.py

'''
Defines Pydantic schemas for doctor data, including base, create, update, and complete record models.
'''

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class DoctorBase(BaseModel):
    FirstName: str
    LastName: str
    Specialty: str
    LicenseNumber: str
    ContactNumber: str
    Email: EmailStr

class DoctorCreate(DoctorBase):
    """Schema for creating a new doctor."""
    pass

class DoctorUpdate(BaseModel):
    """Schema for updating an existing doctor. All fields are optional."""
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    Specialty: Optional[str] = None
    LicenseNumber: Optional[str] = None
    ContactNumber: Optional[str] = None
    Email: Optional[EmailStr] = None

class Doctor(DoctorBase):
    """Schema for a complete doctor record."""
    DoctorID: int
    CreatedAt: datetime

    class Config:
        from_attributes = True