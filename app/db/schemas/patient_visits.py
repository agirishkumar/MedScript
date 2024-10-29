# app/db/schemas/patient_visits.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class PatientVisitBase(BaseModel):
    PatientID: int
    DoctorID: int
    SymptomID: int
    VisitDate: date
    DoctorsReportPdfLink: Optional[str] = None
    PatientFriendlyReportPdfLink: Optional[str] = None
    Notes: Optional[str] = None

class PatientVisitCreate(PatientVisitBase):
    """Schema for creating a new patient visit."""
    pass

class PatientVisitUpdate(BaseModel):
    """Schema for updating an existing patient visit. All fields are optional."""
    VisitDate: Optional[date] = None
    DoctorsReportPdfLink: Optional[str] = None
    PatientFriendlyReportPdfLink: Optional[str] = None
    Notes: Optional[str] = None

class PatientVisit(PatientVisitBase):
    """Schema for a complete patient visit record."""
    VisitID: int
    CreatedAt: datetime

    class Config:
        from_attributes = True
