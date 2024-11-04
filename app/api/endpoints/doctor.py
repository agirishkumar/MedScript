# app/api/endpoints/doctors.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.crud import doctor as doctor_crud
from app.db.schemas.doctor import Doctor, DoctorCreate, DoctorUpdate
from app.api.deps import get_db

router = APIRouter(prefix="/doctors", tags=["doctors"])

@router.post("/", response_model=Doctor, status_code=201)
def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    """
    Create a new doctor record.
    """
    return doctor_crud.create_doctor(db=db, doctor=doctor)

@router.get("/", response_model=List[Doctor])
def read_doctors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of all doctors.
    """
    return doctor_crud.get_all_doctors(db, skip=skip, limit=limit)

@router.get("/{doctor_id}", response_model=Doctor)
def read_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a doctor by ID.
    """
    db_doctor = doctor_crud.get_doctor(db, doctor_id=doctor_id)
    return db_doctor

@router.put("/{doctor_id}", response_model=Doctor)
def update_doctor(doctor_id: int, doctor: DoctorUpdate, db: Session = Depends(get_db)):
    """
    Update an existing doctor record.
    """
    db_doctor = doctor_crud.update_doctor(db=db, doctor_id=doctor_id, doctor=doctor)
    return db_doctor

@router.delete("/{doctor_id}", status_code=204)
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """
    Delete a doctor by ID.
    """
    doctor_crud.delete_doctor(db=db, doctor_id=doctor_id)
    return None
