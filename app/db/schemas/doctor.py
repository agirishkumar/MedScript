# app/db/schemas/doctor.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class DoctorBase(BaseModel):
    first_name: str
    last_name: str
    specialty: str
    license_number: str
    contact_number: str
    email: EmailStr

class DoctorCreate(DoctorBase):
    """Schema for creating a new doctor."""
    pass

class DoctorUpdate(BaseModel):
    """Schema for updating an existing doctor. All fields are optional."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    specialty: Optional[str] = None
    license_number: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[EmailStr] = None

class Doctor(DoctorBase):
    """Schema for a complete doctor record."""
    doctor_id: int
    created_at: datetime

    class Config:
        from_attributes = True
