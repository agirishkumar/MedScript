from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.crud import patient_details, patient_symptoms, patient_visits, doctor
from app.api.deps import get_db
from app.db.schemas.patient import Patient
from app.db.schemas.patient_symptoms import PatientSymptom
from app.db.schemas.patient_visits import PatientVisit
from app.db.schemas.doctor import Doctor
from app.db.schemas.patient_summary import PatientSummaryResponse, VisitDetails

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/{patient_id}/summary", response_model=PatientSummaryResponse)
def get_patient_summary(patient_id: int, db: Session = Depends(get_db)):
    """
    Retrieve detailed summary for a patient including visits, symptoms, and doctor details.
    """
    patient = patient_details.get_patient_details(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get all visits for the patient
    visits = patient_visits.get_patient_visits_by_patient_id(db, patient_id)

    visit_details = []

    for visit in visits:
        # Retrieve symptoms for each visit
        symptoms = patient_symptoms.get_patient_symptoms_by_visit_id(db, visit.VisitID)

        # Retrieve doctor information for the visit
        doctor_data = doctor.get_doctor(db, visit.DoctorID)

        visit_details.append(VisitDetails(visit=visit, symptoms=symptoms, doctor=doctor_data))

    return PatientSummaryResponse(patient=patient, visits=visit_details)
