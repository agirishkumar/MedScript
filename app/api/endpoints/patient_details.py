# app/api/endpoints/patient_details.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.crud import patient_details as patient_details_crud
from app.db.schemas.patient_details import PatientDetails, PatientDetailsCreate, PatientDetailsUpdate
from app.api.deps import get_db

router = APIRouter(prefix="/patient_details", tags=["patient_details"])

@router.post("/", response_model=PatientDetails, status_code=201)
def create_patient_details(patient_details: PatientDetailsCreate, db: Session = Depends(get_db)):
    """
    Create a new patient details record.
    """
    return patient_details_crud.create_patient_details(db=db, patient_details=patient_details)

@router.get("/", response_model=List[PatientDetails])
def read_patient_details(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of all patient details.
    """
    return patient_details_crud.get_all_patient_details(db, skip=skip, limit=limit)

@router.get("/{patient_id}", response_model=PatientDetails)
def read_patient_detail(patient_id: int, db: Session = Depends(get_db)):
    """
    Retrieve patient details by ID.
    """
    db_details = patient_details_crud.get_patient_details(db, patient_id=patient_id)
    return db_details

@router.put("/{patient_id}", response_model=PatientDetails)
def update_patient_detail(patient_id: int, patient_details: PatientDetailsUpdate, db: Session = Depends(get_db)):
    """
    Update an existing patient details record.
    """
    db_details = patient_details_crud.update_patient_details(db=db, patient_id=patient_id, patient_details=patient_details)
    return db_details

@router.delete("/{patient_id}", status_code=204)
def delete_patient_detail(patient_id: int, db: Session = Depends(get_db)):
    """
    Delete patient details by ID.
    """
    patient_details_crud.delete_patient_details(db=db, patient_id=patient_id)
    return {"message": "Deleted successfully"}
