# app/db/schemas/patient_symptoms.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PatientSymptomBase(BaseModel):
    patient_id: int
    symptom_description: str
    input_description: str

class PatientSymptomCreate(PatientSymptomBase):
    """Schema for creating a new patient symptom."""
    pass

class PatientSymptomUpdate(BaseModel):
    """Schema for updating an existing patient symptom. All fields are optional."""
    symptom_description: Optional[str] = None
    input_description: Optional[str] = None

class PatientSymptom(PatientSymptomBase):
    """Schema for a complete patient symptom record."""
    symptom_id: int
    symptom_entered_date: datetime

    class Config:
        from_attributes = True
