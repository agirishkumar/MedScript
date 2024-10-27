# app/db/crud/patient_details.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models.patient_details import PatientDetails
from ..schemas.patient_details import PatientDetailsCreate, PatientDetailsUpdate
from fastapi import HTTPException


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

    patient_details = db.query(PatientDetails).filter(PatientDetails.PatientID == patient_id).first()
    if patient_details is None:
        raise HTTPException(status_code=404, detail="Patient details not found")
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
    return db.query(PatientDetails).offset(skip).limit(limit).all()


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
    db_patient_details = PatientDetails(**patient_details.dict())
    try:
        db.add(db_patient_details)
        db.commit()
        db.refresh(db_patient_details)
        return db_patient_details
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")


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
    db_patient_details = get_patient_details(db, patient_id)
    if db_patient_details is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    for key, value in patient_details.dict(exclude_unset=True).items():
        setattr(db_patient_details, key, value)

    if patient_details.Email:
        existing_patient = db.query(PatientDetails).filter(
            PatientDetails.Email == patient_details.Email,
            PatientDetails.PatientID != patient_id
        ).first()

        if existing_patient:
            raise HTTPException(status_code=400, detail="Email already registered")

    try:
        db.commit()
        db.refresh(db_patient_details)
        return db_patient_details
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")


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
    db_patient_details = get_patient_details(db, patient_id)
    db.delete(db_patient_details)
    db.commit()
    return db_patient_details
