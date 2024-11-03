# app/db/crud/patient.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models.patient import Patient
from ..schemas.patient import PatientCreate, PatientUpdate
from ..crud import user as user_crud
from fastapi import HTTPException

def get_patient(db: Session, patient_id: int):
    """
    Retrieve a patient by ID.

    Args:
    patient_id (int): The ID of the patient to be retrieved.

    Returns:
    Patient: The patient with the specified ID.

    Raises:
    HTTPException: 404 Not Found if the patient does not exist.
    """
    
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


def get_patients(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of all patients.

    Args:
    skip (int, optional): The number of records to skip. Defaults to 0.
    limit (int, optional): The number of records to limit to. Defaults to 100.

    Returns:
    List[Patient]: A list of patients.
    """
    return db.query(Patient).offset(skip).limit(limit).all()

def create_patient(db: Session, patient: PatientCreate):
    """
    Create a new patient.

    Args:
    patient (schemas.patient.PatientCreate): The patient to be created.

    Returns:
    schemas.patient.Patient: The newly created patient.

    Raises:
    HTTPException: 400 Bad Request if the email is already registered.
    """
    db_user = user_crud.get_user_by_email(db, patient.email)
    db_patient = Patient(**patient.dict())
    db_patient.user_id = db_user.user_id
    try:
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        return db_patient
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

def update_patient(db: Session, patient_id: int, patient: PatientUpdate):
    """
    Update an existing patient.

    Args:
    patient_id (int): The ID of the patient to be updated.
    patient (schemas.patient.PatientUpdate): The patient with the updated values.

    Returns:
    schemas.patient.Patient: The updated patient.

    Raises:
    HTTPException: 404 Not Found if the patient does not exist.
    HTTPException: 400 Bad Request if the email is already registered.
    """
    db_patient = get_patient(db, patient_id)
    for key, value in patient.dict().items():
        setattr(db_patient, key, value)
    try:
        db.commit()
        db.refresh(db_patient)
        return db_patient
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

def delete_patient(db: Session, patient_id: int):
    """
    Delete a patient by ID.

    Args:
    patient_id (int): The ID of the patient to be deleted.

    Returns:
    schemas.patient.Patient: The deleted patient.

    Raises:
    HTTPException: 404 Not Found if the patient does not exist.
    """
    
    db_patient = get_patient(db, patient_id)
    db.delete(db_patient)
    db.commit()
    return db_patient