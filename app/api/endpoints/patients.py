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
    return crud.patient.create_patient(db=db, patient=patient)

@router.get("/", response_model=list[schemas.patient.Patient])
def read_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.patient.get_patients(db, skip=skip, limit=limit)

@router.get("/{patient_id}", response_model=schemas.patient.Patient)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.patient.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient
