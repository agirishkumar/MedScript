# app/api/endpoints/patients.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import crud
from app.db import schemas
from app.db.schemas import Patient, PatientCreate, PatientUpdate
from app.api.deps import get_db

router = APIRouter()

@router.post("/", response_model=schemas.patient.Patient)
def create_patient(patient: schemas.patient.PatientCreate, db: Session = Depends(get_db)):
    """
    Create a new patient.

    Args:
    patient (schemas.patient.PatientCreate): The patient to be created.

    Returns:
    schemas.patient.Patient: The newly created patient.
    """
    return crud.patient.create_patient(db=db, patient=patient)

@router.get("/", response_model=list[schemas.patient.Patient])
def read_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of all patients.

    Args:
    skip (int, optional): The number of records to skip. Defaults to 0.
    limit (int, optional): The number of records to limit to. Defaults to 100.

    Returns:
    List[schemas.patient.Patient]: A list of all patients.
    """
    return crud.patient.get_patients(db, skip=skip, limit=limit)

@router.get("/{patient_id}", response_model=schemas.patient.Patient)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a patient by ID.

    Args:
    patient_id (int): The ID of the patient to be retrieved.

    Returns:
    schemas.patient.Patient: The patient with the specified ID.

    Raises:
    HTTPException: 404 Not Found if the patient does not exist.
    """
    db_patient = crud.patient.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient
