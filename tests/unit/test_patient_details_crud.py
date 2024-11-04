# tests/unit/test_patient_details_crud.py

import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException
from unittest.mock import MagicMock
from app.db.crud.patient_details import get_patient_details, get_all_patient_details, create_patient_details, update_patient_details, delete_patient_details
from app.db.schemas.patient_details import PatientDetailsCreate, PatientDetailsUpdate
from app.db.models.patient_details import PatientDetails
from datetime import date



#Mock data for tests
mock_patient_data = PatientDetailsCreate(
    FirstName="John",
    LastName="Doe",
    DateOfBirth=date(1990, 1, 1),
    Gender="Male",
    Address="123 Main St",
    ContactNumber="1234567890",
    Email="johndoe@example.com",
    Height= 5.6,
    Weight = 76,
    BloodType= "B+"
)

@pytest.fixture
def mock_db_session():
    """
    A pytest fixture that creates a temporary in-memory database session
    for testing purposes.  The session is created using the SQLite in-memory
    database engine, and the tables are created using the Base.metadata.create_all()
    method. The fixture yields the session object, and then closes it after the
    test is finished.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    # Create tables in the in-memory database
    from app.db.base import Base
    Base.metadata.create_all(bind=engine)
    yield db
    db.close()


def test_get_patient_details_found(mock_db_session: Session):
    mock_patient = PatientDetails(**mock_patient_data.dict())
    mock_db_session.add(mock_patient)
    mock_db_session.commit()

    retrieved_patient = get_patient_details(mock_db_session, mock_patient.PatientID)
    assert retrieved_patient.Email == mock_patient_data.Email
    assert retrieved_patient.FirstName == mock_patient_data.FirstName
    assert retrieved_patient.DateOfBirth == mock_patient_data.DateOfBirth


def test_get_patient_details_not_found(mock_db_session: Session):
    with pytest.raises(HTTPException) as exc_info:
        get_patient_details(mock_db_session, patient_id=9999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Patient details not found"


# def test_get_all_patient_details(mock_db_session: Session):
#     patients = [PatientDetails(**mock_patient_data.dict()) for _ in range(5)]
#     mock_db_session.add_all(patients)
#     mock_db_session.commit()

#     result = get_all_patient_details(mock_db_session, skip=0, limit=10)
#     assert len(result) == 5


def test_create_patient_details_success(mock_db_session: Session):
    new_patient = create_patient_details(mock_db_session, mock_patient_data)
    assert new_patient.FirstName == mock_patient_data.FirstName
    assert new_patient.LastName == mock_patient_data.LastName
    assert new_patient.DateOfBirth == mock_patient_data.DateOfBirth
    assert new_patient.Gender == mock_patient_data.Gender
    assert new_patient.Address == mock_patient_data.Address
    assert new_patient.Email == mock_patient_data.Email


def test_create_patient_details_duplicate_email(mock_db_session: Session):
    mock_patient = PatientDetails(**mock_patient_data.dict())
    mock_db_session.add(mock_patient)
    mock_db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        create_patient_details(mock_db_session, mock_patient_data)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already registered"


def test_update_patient_details_success(mock_db_session: Session):
    mock_patient = PatientDetails(**mock_patient_data.dict())
    mock_db_session.add(mock_patient)
    mock_db_session.commit()

    update_data = PatientDetailsUpdate(FirstName="Jane", Address="456 Elm St")
    updated_patient = update_patient_details(mock_db_session, mock_patient.PatientID, update_data)
    assert updated_patient.FirstName == "Jane"
    assert updated_patient.Address == "456 Elm St"


def test_update_patient_details_email_duplicate(mock_db_session: Session):
    patient1 = PatientDetails(**mock_patient_data.dict())
    patient2_data = PatientDetailsCreate(
        FirstName="Alice",
        LastName="Smith",
        DateOfBirth=date(1985, 5, 20),
        Gender="Female",
        Address="789 Oak Ave",
        ContactNumber="9876543210",
        Email="alice@example.com",
        Height= 5.2,
        Weight = 90,
        BloodType= "AB-"
    )
    patient2 = PatientDetails(**patient2_data.dict())
    mock_db_session.add_all([patient1, patient2])
    mock_db_session.commit()

    update_data = PatientDetailsUpdate(Email=mock_patient_data.Email)
    with pytest.raises(HTTPException) as exc_info:
        update_patient_details(mock_db_session, patient2.PatientID, update_data)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already registered"


def test_update_patient_details_not_found(mock_db_session: Session):
    update_data = PatientDetailsUpdate(FirstName="Jane")
    with pytest.raises(HTTPException) as exc_info:
        update_patient_details(mock_db_session, patient_id=9999, patient_details=update_data)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Patient details not found"


def test_delete_patient_details_success(mock_db_session: Session):
    mock_patient = PatientDetails(**mock_patient_data.dict())
    mock_db_session.add(mock_patient)
    mock_db_session.commit()

    deleted_patient = delete_patient_details(mock_db_session, mock_patient.PatientID)
    assert deleted_patient.PatientID == mock_patient.PatientID

    with pytest.raises(HTTPException) as exc_info:
        get_patient_details(mock_db_session, mock_patient.PatientID)
    assert exc_info.value.status_code == 404


def test_delete_patient_details_not_found(mock_db_session: Session):
    with pytest.raises(HTTPException) as exc_info:
        delete_patient_details(mock_db_session, patient_id=9999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Patient details not found"


def test_create_patient_details_integrity_error(mock_db_session: Session):
    """Test that creating a patient with a duplicate email raises an IntegrityError."""
    
    # First, create a patient to simulate the existing entry
    existing_patient = PatientDetails(**mock_patient_data.dict())
    mock_db_session.add(existing_patient)
    mock_db_session.commit()

    # Attempt to create a new patient with the same email, which should raise an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        create_patient_details(mock_db_session, mock_patient_data)
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "An error occurred while creating patient details"

def test_update_patient_details_integrity_error(mock_db_session: Session):
    """Test that updating a patient to a duplicate email raises an IntegrityError."""

    # Create an existing patient
    existing_patient = PatientDetails(**mock_patient_data.dict())
    mock_db_session.add(existing_patient)
    mock_db_session.commit()

    # Create another patient with a different email
    other_patient_data = PatientDetailsCreate(
        FirstName="Jane",
        LastName="Doe",
        DateOfBirth=date(1992, 1, 1),
        Gender="Female",
        Address="456 Main St",
        ContactNumber="0987654321",
        Email="janedoe@example.com",
        Height=5.4,
        Weight=65,
        BloodType="A+"
    )
    other_patient = PatientDetails(**other_patient_data.dict())
    mock_db_session.add(other_patient)
    mock_db_session.commit()

    # Attempt to update the first patient to the email of the second patient, which should raise an HTTPException
    update_data = PatientDetailsUpdate(Email="janedoe@example.com")  # Attempting to set the same email
    with pytest.raises(HTTPException) as exc_info:
        update_patient_details(mock_db_session, existing_patient.PatientID, update_data)
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "An error occurred while updating patient details"
