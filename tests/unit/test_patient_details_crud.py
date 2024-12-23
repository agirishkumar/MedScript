# tests/unit/test_patient_details_crud.py

'''
This file contains tests for CRUD operations on patient details, including creation, retrieval, updating, and deletion.
'''

import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException
from unittest.mock import MagicMock
from app.db.crud.patient_details import get_patient_details, get_all_patient_details, create_patient_details, update_patient_details, delete_patient_details
from app.db.schemas.patient_details import PatientDetailsCreate, PatientDetailsUpdate
from app.db.models.patient_details import PatientDetails
from datetime import date
from unittest.mock import patch, MagicMock, Mock
from app.db.models.user import User


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


def test_update_patient_details_email_to_existing_email(mock_db_session: Session):
    """
    Tests updating a patient's email in patient details to an email that already exists raises an HTTPException.
    """
    patient1_data = PatientDetailsCreate(
        FirstName="Alice", LastName="Smith", DateOfBirth=date(1990, 1, 1),
        Gender="Female", Address="123 Main St", ContactNumber="1234567890",
        Email="alice@example.com", Height=5.5, Weight=65, BloodType="A+"
    )

    patient2_data = PatientDetailsCreate(
        FirstName="Bob", LastName="Jones", DateOfBirth=date(1985, 2, 2),
        Gender="Male", Address="456 Elm St", ContactNumber="0987654321",
        Email="bob@example.com", Height=6.0, Weight=80, BloodType="B+"
    )

    with patch("app.db.crud.user_crud.get_user_by_email") as mock_get_user_by_email:
        mock_user = MagicMock(spec=User)
        mock_user.user_id = 1
        mock_get_user_by_email.return_value = mock_user
        new_patient1 = create_patient_details(mock_db_session, patient1_data)
        mock_user.user_id = 2
        mock_get_user_by_email.return_value = mock_user
        new_patient2 = create_patient_details(mock_db_session, patient2_data)

    update_data = PatientDetailsUpdate(Email="bob@example.com")

    with pytest.raises(HTTPException) as exc_info:
        update_patient_details(mock_db_session, new_patient1.PatientID, update_data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already registered"





