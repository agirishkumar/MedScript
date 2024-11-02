# app/db/crud/patient_visit.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models.patient_visits import PatientVisit
from ..schemas.patient_visits import PatientVisitCreate, PatientVisitUpdate
from fastapi import HTTPException
from ...core.logging import logger


def get_patient_visit(db: Session, visit_id: int):
    """
    Retrieve a patient visit by VisitID.

    Args:
        db (Session): The database session.
        visit_id (int): The ID of the visit to be retrieved.

    Returns:
        PatientVisit: The patient visit with the specified ID.

    Raises:
        HTTPException: 404 Not Found if the visit does not exist.
    """
    logger.info(f"Fetching patient visit with ID: {visit_id}")
    visit = db.query(PatientVisit).filter(PatientVisit.VisitID == visit_id).first()
    if visit is None:
        logger.warning(f"Patient visit with ID {visit_id} not found")
        raise HTTPException(status_code=404, detail="Patient visit not found")
    logger.info(f"Successfully retrieved patient visit with ID: {visit_id}")
    return visit


def get_patient_visits_by_patient_id(db: Session, patient_id: int):
    """
    Retrieve all patient visits by PatientID.

    Args:
        db (Session): The database session.
        patient_id (int): The ID of the patient.

    Returns:
        List[PatientVisit]: A list of patient visits for the specified patient.
    """
    logger.info(f"Fetching visits for patient ID: {patient_id}")
    visits = db.query(PatientVisit).filter(PatientVisit.PatientID == patient_id).all()
    logger.info(f"Retrieved {len(visits)} visits for patient ID: {patient_id}")
    return visits


def get_patient_visits_by_symptom_id(db: Session, symptom_id: int):
    """
    Retrieve all patient visits by SymptomID.

    Args:
        db (Session): The database session.
        symptom_id (int): The ID of the symptom.

    Returns:
        List[PatientVisit]: A list of patient visits associated with the specified symptom.
    """
    logger.info(f"Fetching visits with symptom ID: {symptom_id}")
    visits = db.query(PatientVisit).filter(PatientVisit.SymptomID == symptom_id).all()
    logger.info(f"Retrieved {len(visits)} visits with symptom ID: {symptom_id}")
    return visits


def get_all_patient_visits(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of all patient visits.

    Args:
        db (Session): The database session.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The number of records to limit to. Defaults to 100.

    Returns:
        List[PatientVisit]: A list of patient visits.
    """
    logger.info(f"Fetching all patient visits with skip={skip} and limit={limit}")
    visits = db.query(PatientVisit).offset(skip).limit(limit).all()
    logger.info(f"Retrieved {len(visits)} patient visits")
    return visits


def create_patient_visit(db: Session, patient_visit: PatientVisitCreate):
    """
    Create a new patient visit.

    Args:
        db (Session): The database session.
        patient_visit (PatientVisitCreate): The patient visit to be created.

    Returns:
        PatientVisit: The newly created patient visit.

    Raises:
        HTTPException: 400 Bad Request if there is an integrity error.
    """
    logger.info("Creating a new patient visit")
    visit_data = patient_visit.dict()
    visit_data['DoctorsReportPdfLink'] = str(patient_visit.DoctorsReportPdfLink) if patient_visit.DoctorsReportPdfLink else None
    visit_data['PatientFriendlyReportPdfLink'] = str(patient_visit.PatientFriendlyReportPdfLink) if patient_visit.PatientFriendlyReportPdfLink else None

    db_visit = PatientVisit(**visit_data)
    try:
        db.add(db_visit)
        db.commit()
        db.refresh(db_visit)
        logger.info(f"Successfully created patient visit with ID: {db_visit.VisitID}")
        return db_visit
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error during patient visit creation: {e}")
        raise HTTPException(status_code=400, detail="Error occurred while creating the patient visit.")


def update_patient_visit(db: Session, visit_id: int, patient_visit: PatientVisitUpdate):
    """
    Update an existing patient visit.

    Args:
        db (Session): The database session.
        visit_id (int): The ID of the patient visit to be updated.
        patient_visit (PatientVisitUpdate): The patient visit with updated values.

    Returns:
        PatientVisit: The updated patient visit.

    Raises:
        HTTPException: 404 Not Found if the patient visit does not exist.
        HTTPException: 400 Bad Request if an integrity error occurs during the update.
    """
    logger.info(f"Updating patient visit with ID: {visit_id}")
    db_patient_visit = get_patient_visit(db, visit_id)
    for key, value in patient_visit.dict().items():
        if value is not None:
            setattr(db_patient_visit, key, value)
    try:
        db.commit()
        db.refresh(db_patient_visit)
        logger.info(f"Successfully updated patient visit with ID: {visit_id}")
        return db_patient_visit
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error during patient visit update: {e}")
        raise HTTPException(status_code=400, detail="Error updating patient visit")
    except Exception as e:
        logger.error(f"Unexpected error during patient visit update: {e}")
        raise HTTPException(status_code=400, detail="An error occurred during the update.")


def delete_patient_visit(db: Session, visit_id: int):
    """
    Delete a patient visit by VisitID.

    Args:
        db (Session): The database session.
        visit_id (int): The ID of the patient visit to be deleted.

    Returns:
        PatientVisit: The deleted patient visit.

    Raises:
        HTTPException: 404 Not Found if the patient visit does not exist.
    """
    logger.info(f"Deleting patient visit with ID: {visit_id}")
    db_patient_visit = get_patient_visit(db, visit_id)
    db.delete(db_patient_visit)
    db.commit()
    logger.info(f"Successfully deleted patient visit with ID: {visit_id}")
    return db_patient_visit
