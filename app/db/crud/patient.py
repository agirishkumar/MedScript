# app/db/crud/patient.py

from sqlalchemy.orm import Session
from ..models.patient import Patient
from ..schemas.patient import PatientCreate, PatientUpdate
from fastapi import HTTPException

def get_patient(db: Session, patient_id: int):
    """
    Retrieve a patient by ID.

    Args:
    db (Session): The database session to query.
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
    db (Session): The database session to query.
    skip (int, optional): The number of records to skip. Defaults to 0.
    limit (int, optional): The number of records to limit to. Defaults to 100.

    Returns:
    List[Patient]: A list of all patients.
    """
    return db.query(Patient).offset(skip).limit(limit).all()

def create_patient(db: Session, patient: PatientCreate):
    """
    Create a new patient.

    Args:
    db (Session): The database session to interact with.
    patient (PatientCreate): The patient to be created.

    Returns:
    Patient: The newly created patient.
    """
    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient(db: Session, patient_id: int, patient: PatientUpdate):
    """
    Update an existing patient.

    Args:
    db (Session): The database session to interact with.
    patient_id (int): The ID of the patient to be updated.
    patient (PatientUpdate): The patient with the updated values.

    Returns:
    Patient: The updated patient.
    """
    db_patient = get_patient(db, patient_id)
    update_data = patient.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_patient, key, value)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int):
    """
    Delete an existing patient.

    Args:
    db (Session): The database session to interact with.
    patient_id (int): The ID of the patient to be deleted.

    Returns:
    Patient: The deleted patient.
    """
    db_patient = get_patient(db, patient_id)
    db.delete(db_patient)
    db.commit()
    return db_patient