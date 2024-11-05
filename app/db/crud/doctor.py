# app/db/crud/doctor.py
'''
this file contains all the crud operations for the doctor resource'''

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from ..models.doctor import Doctor
from ..schemas.doctor import DoctorCreate, DoctorUpdate


# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_doctor(db: Session, doctor_id: int):
    """
    Retrieve a doctor by DoctorID.

    Args:
        db (Session): The database session.
        doctor_id (int): The ID of the doctor to be retrieved.

    Returns:
        Doctor: The doctor with the specified ID.

    Raises:
        HTTPException: 404 Not Found if the doctor does not exist.
    """
    logger.info("Fetching doctor with ID: %s", doctor_id)
    doctor = db.query(Doctor).filter(Doctor.DoctorID == doctor_id).first()
    if doctor is None:
        logger.warning("Doctor with ID %s not found", doctor_id)
        raise HTTPException(status_code=404, detail="Doctor not found")
    logger.info("Successfully retrieved doctor with ID: %s", doctor_id)
    return doctor


def get_all_doctors(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of all doctors.

    Args:
        db (Session): The database session.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The number of records to limit to. Defaults to 100.

    Returns:
        List[Doctor]: A list of doctors.
    """
    logger.info("Fetching all doctors with skip=%s and limit=%s", skip, limit)
    doctors = db.query(Doctor).offset(skip).limit(limit).all()
    logger.info("Retrieved %s doctor records", len(doctors))
    return doctors


def create_doctor(db: Session, doctor: DoctorCreate):
    """
    Create a new doctor.

    Args:
        db (Session): The database session.
        doctor (DoctorCreate): The doctor to be created.

    Returns:
        Doctor: The newly created doctor.

    Raises:
        HTTPException: 400 Bad Request if the email or license number is already registered.
    """
    logger.info("Creating new doctor with email: %s", doctor.Email)
    existing_email = db.query(Doctor).filter(Doctor.Email == doctor.Email).first()
    if existing_email:
        logger.warning("Email %s already registered", doctor.Email)
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_license = db.query(Doctor).filter(Doctor.LicenseNumber == doctor.LicenseNumber).first()
    if existing_license:
        logger.warning("License number %s already registered", doctor.LicenseNumber)
        raise HTTPException(status_code=400, detail="License number already registered")

    db_doctor = Doctor(**doctor.dict())

    try:
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
        logger.info("Successfully created doctor with ID: %s", db_doctor.DoctorID)
        return db_doctor
    except IntegrityError as e:
        db.rollback()
        logger.error("Integrity error during doctor creation: %s", e)
        raise HTTPException(status_code=400, detail="Error creating doctor") from e


def update_doctor(db: Session, doctor_id: int, doctor: DoctorUpdate):
    """
    Update an existing doctor.

    Args:
        db (Session): The database session.
        doctor_id (int): The ID of the doctor to be updated.
        doctor (DoctorUpdate): The doctor with the updated values.

    Returns:
        Doctor: The updated doctor.

    Raises:
        HTTPException: 404 Not Found if the doctor does not exist.
        HTTPException: 400 Bad Request if the email or license number is already registered.
    """
    logger.info(f"Updating doctor with ID: {doctor_id}")
    db_doctor = get_doctor(db, doctor_id)
    if db_doctor is None:
        logger.warning(f"Doctor with ID {doctor_id} not found for update")
        raise HTTPException(status_code=404, detail="Doctor not found")

    if doctor.Email:
        existing_email = db.query(Doctor).filter(
            Doctor.Email == doctor.Email,
            Doctor.DoctorID != doctor_id
        ).first()
        if existing_email:
            logger.warning(f"Email {doctor.Email} already registered by another doctor")
            raise HTTPException(status_code=400, detail="Email already registered")

    if doctor.LicenseNumber:
        existing_license = db.query(Doctor).filter(
            Doctor.LicenseNumber == doctor.LicenseNumber,
            Doctor.DoctorID != doctor_id
        ).first()
        if existing_license:
            logger.warning(f"License number {doctor.LicenseNumber} already registered by another doctor")
            raise HTTPException(status_code=400, detail="License number already registered")

    for key, value in doctor.dict(exclude_unset=True).items():
        setattr(db_doctor, key, value)

    try:
        db.commit()
        db.refresh(db_doctor)
        logger.info(f"Successfully updated doctor with ID: {doctor_id}")
        return db_doctor
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error during doctor update: {e}")
        raise HTTPException(status_code=400, detail="Error updating doctor details")


def delete_doctor(db: Session, doctor_id: int):
    """
    Delete a doctor by DoctorID.

    Args:
        db (Session): The database session.
        doctor_id (int): The ID of the doctor to be deleted.

    Returns:
        Doctor: The deleted doctor.

    Raises:
        HTTPException: 404 Not Found if the doctor does not exist.
    """
    logger.info(f"Deleting doctor with ID: {doctor_id}")
    db_doctor = get_doctor(db, doctor_id)
    if db_doctor is None:
        logger.warning(f"Doctor with ID {doctor_id} not found for deletion")
        raise HTTPException(status_code=404, detail="Doctor not found")

    db.delete(db_doctor)
    db.commit()
    logger.info(f"Successfully deleted doctor with ID: {doctor_id}")
    return db_doctor
