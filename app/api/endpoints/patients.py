# app/api/endpoints/patients.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.crud import patient as patient_crud
from app.db.schemas.patient import Patient, PatientCreate, PatientUpdate
from app.api.deps import get_db

router = APIRouter(prefix="/patients", tags=["patients"])

@router.post("/", response_model=Patient, status_code=201)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """
    Create a new patient.
    """
    return patient_crud.create_patient(db=db, patient=patient)

@router.get("/", response_model=List[Patient])
def read_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of all patients.
    """
    return patient_crud.get_patients(db, skip=skip, limit=limit)

@router.get("/{patient_id}", response_model=Patient)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a patient by ID.
    """
    db_patient = patient_crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@router.put("/{patient_id}", response_model=Patient)
def update_patient(patient_id: int, patient: PatientUpdate, db: Session = Depends(get_db)):
    """
    Update an existing patient.
    """
    db_patient = patient_crud.update_patient(db=db, patient_id=patient_id, patient=patient)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Delete a patient by ID.
    """
    result = patient_crud.delete_patient(db=db, patient_id=patient_id)
    if not result:
        raise HTTPException(status_code=404, detail="Patient not found")
    return None