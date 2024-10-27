from typing import List
from pydantic import BaseModel
from .patient import Patient
from .patient_symptoms import PatientSymptom
from .patient_visits import PatientVisit
from .doctor import Doctor

class VisitDetails(BaseModel):
    visit: PatientVisit
    symptoms: List[PatientSymptom]
    doctor: Doctor

class PatientSummaryResponse(BaseModel):
    patient: Patient
    visits: List[VisitDetails]
