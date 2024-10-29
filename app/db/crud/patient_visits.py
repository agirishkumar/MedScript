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
    visit_id (int): The ID of the visit to be retrieved.

    Returns:
    PatientVisit: The patient visit with the specified ID.

    Raises:
    HTTPException: 404 Not Found if the visit does not exist.
    """
    visit = db.query(PatientVisit).filter(PatientVisit.VisitID == visit_id).first()
    if visit is None:
        raise HTTPException(status_code=404, detail="Patient visit not found")
    return visit

def get_patient_visits_by_patient_id(db: Session, patient_id: int):
    return db.query(PatientVisit).filter(PatientVisit.PatientID == patient_id).all()

def get_patient_visits_by_symptom_id(db: Session, symptom_id: int):
    return db.query(PatientVisit).filter(PatientVisit.SymptomID == symptom_id).all()

def get_all_patient_visits(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of all patient visits.

    Args:
    skip (int, optional): The number of records to skip. Defaults to 0.
    limit (int, optional): The number of records to limit to. Defaults to 100.

    Returns:
    List[PatientVisit]: A list of patient visits.
    """
    return db.query(PatientVisit).offset(skip).limit(limit).all()

def create_patient_visit(db: Session, patient_visit: PatientVisitCreate):
    """
    Create a new patient visit.

    Args:
    visit (PatientVisitCreate): The patient visit to be created.

    Returns:
    PatientVisit: The newly created patient visit.

    Raises:
    HTTPException: 400 Bad Request if there is an integrity error.
    """
    visit_data = patient_visit.dict()
    visit_data['DoctorsReportPdfLink'] = str(
        patient_visit.DoctorsReportPdfLink) if patient_visit.DoctorsReportPdfLink else None
    visit_data['PatientFriendlyReportPdfLink'] = str(
        patient_visit.PatientFriendlyReportPdfLink) if patient_visit.PatientFriendlyReportPdfLink else None

    db_visit = PatientVisit(**visit_data)
    try:
        db.add(db_visit)
        db.commit()
        db.refresh(db_visit)
        return db_visit
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error occurred while creating the patient visit.")


def update_patient_visit(db: Session, visit_id: int, patient_visit: PatientVisitUpdate):
    """
    Update an existing patient visit.

    Args:
    visit_id (int): The ID of the patient visit to be updated.
    patient_visit (schemas.patient_visit.PatientVisitUpdate): The patient visit with updated values.

    Returns:
    schemas.patient_visit.PatientVisit: The updated patient visit.

    Raises:
    HTTPException: 404 Not Found if the patient visit does not exist.
    """
    db_patient_visit = get_patient_visit(db, visit_id)
    for key, value in patient_visit.dict().items():
        if value is not None:
            setattr(db_patient_visit, key, value)
    try:
        db.commit()
        db.refresh(db_patient_visit)
        return db_patient_visit
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error during update: {e}")
        raise HTTPException(status_code=400, detail="Error updating patient visit")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=400, detail="An error occurred during the update.")


def delete_patient_visit(db: Session, visit_id: int):
    """
    Delete a patient visit by VisitID.

    Args:
    visit_id (int): The ID of the patient visit to be deleted.

    Returns:
    schemas.patient_visit.PatientVisit: The deleted patient visit.

    Raises:
    HTTPException: 404 Not Found if the patient visit does not exist.
    """
    db_patient_visit = get_patient_visit(db, visit_id)
    db.delete(db_patient_visit)
    db.commit()
    return db_patient_visit
