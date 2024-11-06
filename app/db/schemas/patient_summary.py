from typing import List
from pydantic import BaseModel
from .patient_details import PatientDetails
from .patient_symptoms import PatientSymptom
from .patient_visits import PatientVisit
from .doctor import Doctor
from typing import Optional

class VisitDetails(BaseModel):
    visit: Optional[PatientVisit]
    symptoms: Optional[List[PatientSymptom]]
    doctor: Optional[Doctor]

class PatientSummaryResponse(BaseModel):
    patient: PatientDetails
    visits: Optional[List[VisitDetails]]
