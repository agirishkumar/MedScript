# app/db/crud/doctor.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models.doctor import Doctor
from ..schemas.doctor import DoctorCreate, DoctorUpdate
from fastapi import HTTPException

def get_doctor(db: Session, doctor_id: int):
    """
    Retrieve a doctor by DoctorID.

    Args:
    doctor_id (int): The ID of the doctor to be retrieved.

    Returns:
    Doctor: The doctor with the specified ID.

    Raises:
    HTTPException: 404 Not Found if the doctor does not exist.
    """
    doctor = db.query(Doctor).filter(Doctor.DoctorID == doctor_id).first()
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


def get_all_doctors(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of all doctors.

    Args:
    skip (int, optional): The number of records to skip. Defaults to 0.
    limit (int, optional): The number of records to limit to. Defaults to 100.

    Returns:
    List[Doctor]: A list of doctors.
    """
    return db.query(Doctor).offset(skip).limit(limit).all()

def create_doctor(db: Session, doctor: DoctorCreate):
    """
    Create a new doctor.

    Args:
    doctor (schemas.doctor.DoctorCreate): The doctor to be created.

    Returns:
    schemas.doctor.Doctor: The newly created doctor.

    Raises:
    HTTPException: 400 Bad Request if the email or license number is already registered.
    """
    existing_email = db.query(Doctor).filter(
        Doctor.Email == doctor.Email
    ).first()

    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_license = db.query(Doctor).filter(
        Doctor.LicenseNumber == doctor.LicenseNumber
    ).first()

    if existing_license:
        raise HTTPException(status_code=400, detail="License number already registered")

    db_doctor = Doctor(**doctor.dict())

    try:
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating doctor")


def update_doctor(db: Session, doctor_id: int, doctor: DoctorUpdate):
    """
    Update an existing doctor.

    Args:
    doctor_id (int): The ID of the doctor to be updated.
    doctor (schemas.doctor.DoctorUpdate): The doctor with the updated values.

    Returns:
    schemas.doctor.Doctor: The updated doctor.

    Raises:
    HTTPException: 404 Not Found if the doctor does not exist.
    HTTPException: 400 Bad Request if the email or license number is already registered.
    """
    db_doctor = get_doctor(db, doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if doctor.Email:
        existing_email = db.query(Doctor).filter(
            Doctor.Email == doctor.Email,
            Doctor.DoctorID != doctor_id
        ).first()

        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")

    if doctor.LicenseNumber:
        existing_license = db.query(Doctor).filter(
            Doctor.LicenseNumber == doctor.LicenseNumber,
            Doctor.DoctorID != doctor_id
        ).first()

        if existing_license:
            raise HTTPException(status_code=400, detail="License number already registered")

    for key, value in doctor.dict(exclude_unset=True).items():
        setattr(db_doctor, key, value)

    try:
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error updating doctor details")


def delete_doctor(db: Session, doctor_id: int):
    """
    Delete a doctor by DoctorID.

    Args:
    doctor_id (int): The ID of the doctor to be deleted.

    Returns:
    schemas.doctor.Doctor: The deleted doctor.

    Raises:
    HTTPException: 404 Not Found if the doctor does not exist.
    """
    db_doctor = get_doctor(db, doctor_id)
    db.delete(db_doctor)
    db.commit()
    return db_doctor
