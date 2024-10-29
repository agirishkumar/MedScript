# app/api/endpoints/patient_visits.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.crud import patient_visits as patient_visit_crud
from app.db.schemas.patient_visits import PatientVisit, PatientVisitCreate, PatientVisitUpdate
from app.api.deps import get_db

router = APIRouter(prefix="/patient_visits", tags=["patient_visits"])

@router.post("/", response_model=PatientVisit, status_code=201)
def create_patient_visit(patient_visit: PatientVisitCreate, db: Session = Depends(get_db)):
    """
    Create a new patient visit record.
    """
    return patient_visit_crud.create_patient_visit(db=db, patient_visit=patient_visit)

@router.get("/", response_model=List[PatientVisit])
def read_patient_visits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of all patient visits.
    """
    return patient_visit_crud.get_all_patient_visits(db, skip=skip, limit=limit)

@router.get("/{visit_id}", response_model=PatientVisit)
def read_patient_visit(visit_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a patient visit by ID.
    """
    db_visit = patient_visit_crud.get_patient_visit(db, visit_id=visit_id)
    if db_visit is None:
        raise HTTPException(status_code=404, detail="Patient visit not found")
    return db_visit

@router.put("/{visit_id}", response_model=PatientVisit)
def update_patient_visit(visit_id: int, patient_visit: PatientVisitUpdate, db: Session = Depends(get_db)):
    """
    Update an existing patient visit record.
    """
    db_visit = patient_visit_crud.update_patient_visit(db=db, visit_id=visit_id, patient_visit=patient_visit)
    if db_visit is None:
        raise HTTPException(status_code=404, detail="Patient visit not found")
    return db_visit

@router.delete("/{visit_id}", status_code=204)
def delete_patient_visit(visit_id: int, db: Session = Depends(get_db)):
    """
    Delete a patient visit by ID.
    """
    result = patient_visit_crud.delete_patient_visit(db=db, visit_id=visit_id)
    if not result:
        raise HTTPException(status_code=404, detail="Patient visit not found")
    return None
