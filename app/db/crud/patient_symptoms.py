# app/db/crud/patient_symptom.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models.patient_symptoms import PatientSymptom
from ..schemas.patient_symptoms import PatientSymptomCreate, PatientSymptomUpdate
from fastapi import HTTPException

def get_patient_symptom(db: Session, symptom_id: int):
    """
    Retrieve a patient symptom by SymptomID.

    Args:
    symptom_id (int): The ID of the symptom to be retrieved.

    Returns:
    PatientSymptom: The patient symptom with the specified ID.

    Raises:
    HTTPException: 404 Not Found if the symptom does not exist.
    """
    symptom = db.query(PatientSymptom).filter(PatientSymptom.SymptomID == symptom_id).first()
    if symptom is None:
        raise HTTPException(status_code=404, detail="Patient symptom not found")
    return symptom

def get_patient_symptoms_by_visit_id(db: Session, visit_id: int):
    return db.query(PatientSymptom).filter(PatientSymptom.VisitID == visit_id).all()

def get_all_patient_symptoms(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of all patient symptoms.

    Args:
    skip (int, optional): The number of records to skip. Defaults to 0.
    limit (int, optional): The number of records to limit to. Defaults to 100.

    Returns:
    List[PatientSymptom]: A list of patient symptoms.
    """
    return db.query(PatientSymptom).offset(skip).limit(limit).all()

def create_patient_symptom(db: Session, patient_symptom: PatientSymptomCreate):
    """
    Create a new patient symptom.

    Args:
    patient_symptom (schemas.patient_symptom.PatientSymptomCreate): The patient symptom to be created.

    Returns:
    schemas.patient_symptom.PatientSymptom: The newly created patient symptom.
    """
    db_patient_symptom = PatientSymptom(**patient_symptom.dict())
    try:
        db.add(db_patient_symptom)
        db.commit()
        db.refresh(db_patient_symptom)
        return db_patient_symptom
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating patient symptom")


def update_patient_symptom(db: Session, symptom_id: int, patient_symptom: PatientSymptomUpdate):
    """
    Update an existing patient symptom.

    Args:
    symptom_id (int): The ID of the patient symptom to be updated.
    patient_symptom (schemas.patient_symptom.PatientSymptomUpdate): The patient symptom with updated values.

    Returns:
    schemas.patient_symptom.PatientSymptom: The updated patient symptom.

    Raises:
    HTTPException: 404 Not Found if the patient symptom does not exist.
    """
    db_patient_symptom = get_patient_symptom(db, symptom_id)
    for key, value in patient_symptom.dict().items():
        setattr(db_patient_symptom, key, value)
    try:
        db.commit()
        db.refresh(db_patient_symptom)
        return db_patient_symptom
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error updating patient symptom")


def delete_patient_symptom(db: Session, symptom_id: int):
    """
    Delete a patient symptom by SymptomID.

    Args:
    symptom_id (int): The ID of the patient symptom to be deleted.

    Returns:
    schemas.patient_symptom.PatientSymptom: The deleted patient symptom.

    Raises:
    HTTPException: 404 Not Found if the patient symptom does not exist.
    """
    db_patient_symptom = get_patient_symptom(db, symptom_id)
    db.delete(db_patient_symptom)
    db.commit()
    return db_patient_symptom
