# tests/unit/test_patient_crud.py

from app.db.crud.patient import create_patient, get_patient, update_patient, delete_patient
from app.db.models.patient import Patient
from app.db.models.user import User
from app.db.schemas.patient import PatientCreate, PatientUpdate
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock, Mock
import pytest
from fastapi import HTTPException

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

def test_create_patient(mock_db_session: Session):
    """
    Tests that a new patient can be created successfully with valid data.
    """
    patient_data = PatientCreate(name="Test Patient", age=25, email="test@example.com", user_id=1)
    with patch("app.db.crud.user_crud.get_user_by_email") as mock_get_user_by_email:
        mock_user = MagicMock(spec=User)
        mock_user.user_id = 1
        mock_get_user_by_email.return_value = mock_user
        new_patient = create_patient(mock_db_session, patient_data)
    assert new_patient.name == "Test Patient"
    assert new_patient.age == 25
    assert new_patient.email == "test@example.com"
    assert new_patient.user_id == 1


def test_get_patient(mock_db_session: Session):
    """
    Tests that a patient can be retrieved from the database using its ID.
    """
    patient_data = PatientCreate(name="Jane Doe", age=30, email="jane@example.com")
    with patch("app.db.crud.user_crud.get_user_by_email") as mock_get_user_by_email:
        mock_user = MagicMock(spec=User)
        mock_user.user_id = 1
        mock_get_user_by_email.return_value = mock_user
        new_patient = create_patient(mock_db_session, patient_data)
    fetched_patient = get_patient(mock_db_session, new_patient.id)
    assert fetched_patient.name == "Jane Doe"
    assert fetched_patient.email == "jane@example.com"


def test_update_patient(mock_db_session: Session):
    """
    Tests that a patient can be updated successfully with valid data.
    """
    patient_data = PatientCreate(name="John Doe", age=40, email="john@example.com")
    with patch("app.db.crud.user_crud.get_user_by_email") as mock_get_user_by_email:
        mock_user = MagicMock(spec=User)
        mock_user.user_id = 1
        mock_get_user_by_email.return_value = mock_user
        new_patient = create_patient(mock_db_session, patient_data)
    updated_data = PatientUpdate(age=45)
    updated_patient = update_patient(mock_db_session, new_patient.id, updated_data)
    assert updated_patient.age == 45


def test_update_patient_email_to_existing_email(mock_db_session: Session):
    """
    Tests updating a patient's email to an email that already exists raises an IntegrityError.
    """
    patient1_data = PatientCreate(name="Alice", age=30, email="alice@example.com")
    patient2_data = PatientCreate(name="Bob", age=40, email="bob@example.com")

    with patch("app.db.crud.user_crud.get_user_by_email") as mock_get_user_by_email:
        mock_user = MagicMock(spec=User)
        mock_user.user_id = 1
        mock_get_user_by_email.return_value = mock_user
        new_patient1 = create_patient(mock_db_session, patient1_data)
        mock_user.user_id = 2
        mock_get_user_by_email.return_value = mock_user
        new_patient2 = create_patient(mock_db_session, patient2_data)

    update_data = PatientUpdate(email="bob@example.com")

    with pytest.raises(HTTPException) as exc_info:
        update_patient(mock_db_session, new_patient1.id, update_data)

    # Confirm exception details
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already registered"

def test_delete_patient(mock_db_session: Session):
    """
    Tests that a patient can be deleted successfully from the database.

    Creates a new patient with valid data, then deletes it by ID. Asserts that the
    deleted patient matches the one created and that the patient is no longer present
    in the database.
    """
    patient_data = PatientCreate(name="Alice", age=28, email="alice@example.com")
    with patch("app.db.crud.user_crud.get_user_by_email") as mock_get_user_by_email:
        mock_user = MagicMock(spec=User)
        mock_user.user_id = 1
        mock_get_user_by_email.return_value = mock_user
        new_patient = create_patient(mock_db_session, patient_data)
    deleted_patient = delete_patient(mock_db_session, new_patient.id)
    assert deleted_patient.name == "Alice"
    assert mock_db_session.query(Patient).filter(Patient.id == new_patient.id).first() is None

def test_create_patient_duplicate_email(mock_db_session: Session):
    """
    Tests that attempting to create a patient with a duplicate email raises an exception.
    """
    patient_data = PatientCreate(name="John Doe", age=35, email="duplicate@example.com", user_id=1)
    with patch("app.db.crud.user.get_user_by_email") as mock_get_user_by_email:
        mock_user = MagicMock(spec=User)
        mock_user.user_id = 1
        mock_get_user_by_email.return_value = mock_user
        create_patient(mock_db_session, patient_data)
        with pytest.raises(HTTPException) as exc_info:
            create_patient(mock_db_session, patient_data)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Email already registered"

def test_get_patient(mock_db_session: Session):
    """
    Tests that a patient can be retrieved from the database using its ID.
    """
    patient_data = PatientCreate(name="Jane Doe", age=30, email="jane@example.com", user_id=1)
    with patch("app.db.crud.user.get_user_by_email") as mock_get_user_by_email:
        mock_user = MagicMock(spec=User)
        mock_user.user_id = 1
        mock_get_user_by_email.return_value = mock_user
        new_patient = create_patient(mock_db_session, patient_data)
    fetched_patient = get_patient(mock_db_session, new_patient.id)
    assert fetched_patient.name == "Jane Doe"
    assert fetched_patient.email == "jane@example.com"

def test_get_patient_not_found(mock_db_session: Session):
    """
    Tests that attempting to retrieve a non-existent patient raises an HTTPException.
    """
    with pytest.raises(HTTPException) as exc_info:
        get_patient(mock_db_session, patient_id=999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Patient not found"


def test_create_patient_integrity_error(mock_db_session: Session):
    """
    Tests that an IntegrityError is raised when attempting to create a patient with an email
    that is already registered.
    """
    # Set up initial patient data
    patient_data_1 = PatientCreate(name="Existing Patient", age=30, email="duplicate@example.com", user_id=1)
    patient_data_2 = PatientCreate(name="New Patient", age=35, email="duplicate@example.com", user_id=1)
    
    with patch("app.db.crud.user_crud.get_user_by_email") as mock_get_user_by_email:
        # Mocking user for association
        mock_user = MagicMock(spec=User)
        mock_user.user_id = 1
        mock_get_user_by_email.return_value = mock_user
        
        # Create the initial patient
        create_patient(mock_db_session, patient_data_1)
        
        # Attempt to create a second patient with the same email, expecting an IntegrityError
        with pytest.raises(HTTPException) as exc_info:
            create_patient(mock_db_session, patient_data_2)
        
        # Assert that the exception has the expected status code and message
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Email already registered"


def test_get_patient_not_found(mock_db_session: Session):
    """
    Tests that an HTTPException with a 404 status code is raised when trying to
    retrieve a patient that does not exist in the database.
    """
    non_existent_patient_id = 999  # An ID that does not exist in the database
    
    with pytest.raises(HTTPException) as exc_info:
        get_patient(mock_db_session, non_existent_patient_id)
    
    # Assert that the exception has the expected status code and message
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Patient not found"
