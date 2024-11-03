# tests/unit/test_patient_crud.py

from app.db.crud.patient import create_patient, get_patient, update_patient, delete_patient
from app.db.models.patient import Patient
from app.db.models.user import User
from app.db.schemas.patient import PatientCreate, PatientUpdate
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock, Mock
import pytest
from pydantic import ValidationError

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