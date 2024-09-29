from pydantic import BaseModel, EmailStr, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)