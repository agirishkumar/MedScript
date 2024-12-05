# app/db/crud/patient_details.py

'''
This file contains all the CRUD operations for the patient details table.
'''

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models.patient_details import PatientDetails
from ..schemas.patient_details import PatientDetailsCreate, PatientDetailsUpdate
from fastapi import HTTPException

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_patient_details(db: Session, patient_id: int):
    """
    Retrieve patient details by PatientID.

    Args:
    patient_id (int): The ID of the patient whose details to be retrieved.

    Returns:
    PatientDetails: The patient details with the specified ID.

    Raises:
    HTTPException: 404 Not Found if the patient does not exist.
    """
    logger.info(f"Fetching patient details with ID: {patient_id}")
    patient_details = db.query(PatientDetails).filter(PatientDetails.PatientID == patient_id).first()
    if patient_details is None:
        logger.warning(f"Patient details with ID {patient_id} not found")
        raise HTTPException(status_code=404, detail="Patient details not found")
    logger.info(f"Successfully retrieved patient details with ID: {patient_id}")
    return patient_details


def get_all_patient_details(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of all patient details.

    Args:
    skip (int, optional): The number of records to skip. Defaults to 0.
    limit (int, optional): The number of records to limit to. Defaults to 100.

    Returns:
    List[PatientDetails]: A list of patient details.
    """
    logger.info(f"Fetching patient details with skip={skip} and limit={limit}")
    patient_details = db.query(PatientDetails).offset(skip).limit(limit).all()
    logger.info(f"Retrieved {len(patient_details)} patient details records")
    return patient_details


def create_patient_details(db: Session, patient_details: PatientDetailsCreate):
    """
    Create new patient details.

    Args:
        patient_details (schemas.patient_details.PatientDetailsCreate): The patient details to be created.

    Returns:
        schemas.patient_details.PatientDetails: The newly created patient details.

    Raises:
        HTTPException: 400 Bad Request if the email is already registered.
    """
    logger.info(f"Creating new patient details with email: {patient_details.Email}")
    existing_patient = db.query(PatientDetails).filter(PatientDetails.Email == patient_details.Email).first()
    if existing_patient:
        logger.warning(f"Email {patient_details.Email} already registered")
        raise HTTPException(status_code=400, detail="Email already registered")

    db_patient_details = PatientDetails(**patient_details.dict())
    try:
        db.add(db_patient_details)
        db.commit()
        db.refresh(db_patient_details)
        logger.info(f"Successfully created patient details with ID: {db_patient_details.PatientID}")
        return db_patient_details
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error during patient details creation: {e}")
        raise HTTPException(status_code=400, detail="An error occurred while creating patient details")


def update_patient_details(db: Session, patient_id: int, patient_details: PatientDetailsUpdate):
    """
    Update existing patient details.

    Args:
        db (Session): The database session.
        patient_id (int): The ID of the patient whose details are to be updated.
        patient_details (PatientDetailsUpdate): The patient details with updated values.

    Returns:
        PatientDetails: The updated patient details.

    Raises:
        HTTPException: 404 Not Found if the patient does not exist.
        HTTPException: 400 Bad Request if the email is already registered.
    """
    logger.info(f"Updating patient details with ID: {patient_id}")
    db_patient_details = get_patient_details(db, patient_id)

    for key, value in patient_details.dict(exclude_unset=True).items():
        setattr(db_patient_details, key, value)

    if patient_details.Email:
        existing_patient = db.query(PatientDetails).filter(
            PatientDetails.Email == patient_details.Email,
            PatientDetails.PatientID != patient_id
        ).first()

        if existing_patient:
            logger.warning(f"Email {patient_details.Email} already registered by another patient")
            raise HTTPException(status_code=400, detail="Email already registered")

    try:
        db.commit()
        db.refresh(db_patient_details)
        logger.info(f"Successfully updated patient details with ID: {patient_id}")
        return db_patient_details
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error during patient details update: {e}")
        raise HTTPException(status_code=400, detail="An error occurred while updating patient details")


def delete_patient_details(db: Session, patient_id: int):
    """
    Delete patient details by PatientID.

    Args:
    patient_id (int): The ID of the patient whose details are to be deleted.

    Returns:
    schemas.patient_details.PatientDetails: The deleted patient details.

    Raises:
    HTTPException: 404 Not Found if the patient does not exist.
    """
    logger.info(f"Deleting patient details with ID: {patient_id}")
    db_patient_details = get_patient_details(db, patient_id)
    db.delete(db_patient_details)
    db.commit()
    logger.info(f"Successfully deleted patient details with ID: {patient_id}")
    return db_patient_details



def get_latest_patient_id(db: Session) -> int:
    """
    Get the ID of the most recently added patient.
    
    Args:
        db (Session): Database session
        
    Returns:
        int: The latest patient ID, or None if no patients exist
    """
    latest_patient = db.query(PatientDetails).order_by(PatientDetails.PatientID.desc()).first()
    return latest_patient.PatientID if latest_patient else None