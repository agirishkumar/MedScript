from typing import List
from pydantic import BaseModel
from .patient_details import PatientDetails
from .patient_symptoms import PatientSymptom
from .patient_visits import PatientVisit
from .doctor import Doctor

class VisitDetails(BaseModel):
    visit: PatientVisit
    symptoms: List[PatientSymptom]
    doctor: Doctor

class PatientSummaryResponse(BaseModel):
    patient: PatientDetails
    visits: List[VisitDetails]
