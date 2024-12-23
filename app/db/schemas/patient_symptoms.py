# app/db/schemas/patient_symptoms.py

'''
Defines Pydantic schemas for a patient symptoms table.
'''

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PatientSymptomBase(BaseModel):
    PatientID: int
    SymptomDescription: Optional[str] = None
    ModelInputDescription: Optional[str] = None
    Severity: Optional[str] = None
    Duration: Optional[str] = None
    AssociatedConditions: Optional[str] = None

class PatientSymptomCreate(PatientSymptomBase):
    """Schema for creating a new patient symptom."""
    pass

class PatientSymptomUpdate(BaseModel):
    """Schema for updating an existing patient symptom. All fields are optional."""
    SymptomDescription: Optional[str] = None
    ModelInputDescription: Optional[str] = None
    Severity: Optional[str] = None
    Duration: Optional[str] = None
    AssociatedConditions: Optional[str] = None

class PatientSymptom(PatientSymptomBase):
    """Schema for a complete patient symptom record."""
    SymptomID: int
    SymptomEnteredDate: datetime

    class Config:
        from_attributes = True