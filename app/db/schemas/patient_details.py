# app/db/schemas/patient_details.py

from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional

class PatientDetailsBase(BaseModel):
    FirstName: str
    LastName: str
    DateOfBirth: date
    Gender: str
    Address: str
    ContactNumber: str
    Email: EmailStr

class PatientDetailsCreate(PatientDetailsBase):
    pass

class PatientDetailsUpdate(PatientDetailsBase):
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    DateOfBirth: Optional[date] = None
    Gender: Optional[str] = None
    Address: Optional[str] = None
    ContactNumber: Optional[str] = None
    Email: Optional[EmailStr] = None

class PatientDetails(PatientDetailsBase):
    PatientID: int
    CreatedAt: datetime

    class Config:
        from_attributes = True
