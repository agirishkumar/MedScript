from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException

def get_patient(db: Session, patient_id: int):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

def get_patients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Patient).offset(skip).limit(limit).all()

def get_patient_by_email(db: Session, email: str):
    return db.query(models.Patient).filter(models.Patient.email == email).first()

def create_patient(db: Session, patient: schemas.PatientCreate):
    # Check if the email already exists in the database
    db_patient = get_patient_by_email(db, patient.email)
    if db_patient:
        raise HTTPException(
            status_code=409,
            detail=f"Patient with email {patient.email} already exists.",
        )

    # Create a new patient record if email is unique
    db_patient = models.Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def update_patient(db: Session, patient_id: int, patient: schemas.PatientUpdate):
    db_patient = get_patient(db, patient_id)
    update_data = patient.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_patient, key, value)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int):
    db_patient = get_patient(db, patient_id)
    db.delete(db_patient)
    db.commit()
    return db_patient