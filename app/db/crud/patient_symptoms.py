# app/db/crud/patient_symptom.py

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models import PatientVisit
from ..models.patient_symptoms import PatientSymptom
from ..schemas.patient_symptoms import PatientSymptomCreate, PatientSymptomUpdate
from fastapi import HTTPException

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_patient_symptom(db: Session, symptom_id: int):
    """
    Retrieve a patient symptom by SymptomID.

    Args:
        db (Session): The database session.
        symptom_id (int): The ID of the symptom to be retrieved.

    Returns:
        PatientSymptom: The patient symptom with the specified ID.

    Raises:
        HTTPException: 404 Not Found if the symptom does not exist.
    """
    logger.info(f"Fetching patient symptom with ID: {symptom_id}")
    symptom = db.query(PatientSymptom).filter(PatientSymptom.SymptomID == symptom_id).first()
    if symptom is None:
        logger.warning(f"Patient symptom with ID {symptom_id} not found")
        raise HTTPException(status_code=404, detail="Patient symptom not found")
    logger.info(f"Successfully retrieved patient symptom with ID: {symptom_id}")
    return symptom


def get_patient_symptoms_by_visit_id(db: Session, visit_id: int):
    """
    Retrieve all patient symptoms by VisitID.

    Args:
        db (Session): The database session.
        visit_id (int): The ID of the visit.

    Returns:
        List[PatientSymptom]: A list of patient symptoms for the specified visit.
    """
    logger.info(f"Fetching patient symptoms for visit ID: {visit_id}")
    symptoms = db.query(PatientSymptom).filter(PatientSymptom.VisitID == visit_id).all()
    logger.info(f"Retrieved {len(symptoms)} symptoms for visit ID: {visit_id}")
    return symptoms


def get_patient_symptoms_by_patient_id(db: Session, patient_id: int):
    """
    Retrieve all patient symptoms by PatientID.

    Args:
        db (Session): The database session.
        patient_id (int): The ID of the patient.

    Returns:
        List[PatientSymptom]: A list of patient symptoms for the specified patient.
    """
    logger.info(f"Fetching patient symptoms for patient ID: {patient_id}")
    symptoms = db.query(PatientSymptom).join(PatientVisit).filter(PatientVisit.PatientID == patient_id).all()
    logger.info(f"Retrieved {len(symptoms)} symptoms for patient ID: {patient_id}")
    return symptoms


def get_all_patient_symptoms(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of all patient symptoms.

    Args:
        db (Session): The database session.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The number of records to limit to. Defaults to 100.

    Returns:
        List[PatientSymptom]: A list of patient symptoms.
    """
    logger.info(f"Fetching all patient symptoms with skip={skip} and limit={limit}")
    symptoms = db.query(PatientSymptom).offset(skip).limit(limit).all()
    logger.info(f"Retrieved {len(symptoms)} patient symptoms")
    return symptoms


def create_patient_symptom(db: Session, patient_symptom: PatientSymptomCreate):
    """
    Create a new patient symptom.

    Args:
        db (Session): The database session.
        patient_symptom (PatientSymptomCreate): The patient symptom to be created.

    Returns:
        PatientSymptom: The newly created patient symptom.
    """
    logger.info("Creating a new patient symptom")
    db_patient_symptom = PatientSymptom(**patient_symptom.dict())
    try:
        db.add(db_patient_symptom)
        db.commit()
        db.refresh(db_patient_symptom)
        logger.info(f"Successfully created patient symptom with ID: {db_patient_symptom.SymptomID}")
        return db_patient_symptom
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error during patient symptom creation: {e}")
        raise HTTPException(status_code=400, detail="Error creating patient symptom")


def update_patient_symptom(db: Session, symptom_id: int, patient_symptom: PatientSymptomUpdate):
    """
    Update an existing patient symptom.

    Args:
        db (Session): The database session.
        symptom_id (int): The ID of the patient symptom to be updated.
        patient_symptom (PatientSymptomUpdate): The patient symptom with updated values.

    Returns:
        PatientSymptom: The updated patient symptom.

    Raises:
        HTTPException: 404 Not Found if the patient symptom does not exist.
    """
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    logger.info(f"Updating patient symptom with ID: {symptom_id}")
=======

>>>>>>> Stashed changes
=======

>>>>>>> Stashed changes
    db_patient_symptom = get_patient_symptom(db, symptom_id)
    for key, value in patient_symptom.dict().items():
        setattr(db_patient_symptom, key, value)
    try:
        db.commit()
        db.refresh(db_patient_symptom)
        logger.info(f"Successfully updated patient symptom with ID: {symptom_id}")
        return db_patient_symptom
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error during patient symptom update: {e}")
        raise HTTPException(status_code=400, detail="Error updating patient symptom")


def delete_patient_symptom(db: Session, symptom_id: int):
    """
    Delete a patient symptom by SymptomID.

    Args:
        db (Session): The database session.
        symptom_id (int): The ID of the patient symptom to be deleted.

    Returns:
        PatientSymptom: The deleted patient symptom.

    Raises:
        HTTPException: 404 Not Found if the patient symptom does not exist.
    """
    logger.info(f"Deleting patient symptom with ID: {symptom_id}")
    db_patient_symptom = get_patient_symptom(db, symptom_id)
    db.delete(db_patient_symptom)
    db.commit()
    logger.info(f"Successfully deleted patient symptom with ID: {symptom_id}")
    return db_patient_symptom