# app/db/schemas/patient_visits.py

from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime, date

class PatientVisitBase(BaseModel):
    patient_id: int
    doctor_id: int
    symptom_id: int
    visit_date: date
    doctors_report_pdf_link: Optional[HttpUrl] = None
    patient_friendly_report_pdf_link: Optional[HttpUrl] = None
    notes: Optional[str] = None

class PatientVisitCreate(PatientVisitBase):
    """Schema for creating a new patient visit."""
    pass

class PatientVisitUpdate(BaseModel):
    """Schema for updating an existing patient visit. All fields are optional."""
    visit_date: Optional[date] = None
    doctors_report_pdf_link: Optional[HttpUrl] = None
    patient_friendly_report_pdf_link: Optional[HttpUrl] = None
    notes: Optional[str] = None

class PatientVisit(PatientVisitBase):
    """Schema for a complete patient visit record."""
    visit_id: int
    created_at: datetime

    class Config:
        from_attributes = True
