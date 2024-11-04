# tests/unit/test_doctor_crud.py

from app.db.crud.doctor import create_doctor, get_doctor, update_doctor, delete_doctor, get_all_doctors
from fastapi import HTTPException
from app.db.models.doctor import Doctor
from app.db.models.user import User
from app.db.schemas.doctor import DoctorCreate, DoctorUpdate
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
import pytest
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from unittest.mock import patch, call

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


def test_create_doctor(mock_db_session: Session):
    """
    Tests that a new doctor can be created successfully with valid data.
    """
    doctor_data = DoctorCreate(FirstName="Test", LastName="Doctor", Specialty = "Cardiologist", LicenseNumber="12345", ContactNumber = "9878656422", Email="test@example.com")
    new_doctor = create_doctor(mock_db_session, doctor_data)
    assert new_doctor.FirstName == "Test"
    assert new_doctor.LastName == "Doctor"
    assert new_doctor.Specialty == "Cardiologist"
    assert new_doctor.LicenseNumber == "12345"
    assert new_doctor.ContactNumber == "9878656422"
    assert new_doctor.Email == "test@example.com"

def test_get_doctor(mock_db_session: Session):
    """
    Tests that a doctor can be retrieved from the database using its ID.
    """
    doctor_data = DoctorCreate(FirstName="Jane", LastName="Doe", Specialty = "Cardiologist", LicenseNumber="54321", ContactNumber = "9984567887", Email="test_john@example.com")
    new_doctor = create_doctor(mock_db_session, doctor_data)
    fetched_doctor = get_doctor(mock_db_session, new_doctor.DoctorID)
    assert fetched_doctor.FirstName == "Jane"
    assert fetched_doctor.LastName == "Doe"
    assert fetched_doctor.Specialty == "Cardiologist"
    assert fetched_doctor.LicenseNumber == "54321"
    assert fetched_doctor.ContactNumber == "9984567887"
    assert fetched_doctor.Email == "test_john@example.com"

# def test_update_doctor(mock_db_session: Session):

def test_update_doctor(mock_db_session: Session):
    doctor_data = DoctorCreate(FirstName="John", LastName="Doe", Specialty = "Neurologist", LicenseNumber="54321", ContactNumber = "9984567887", Email="test_john@example.com")
    new_doctor = create_doctor(mock_db_session, doctor_data)
    updated_data = DoctorUpdate(FirstName="Johnny")
    updated_doctor = update_doctor(mock_db_session, new_doctor.DoctorID, updated_data)
    assert updated_doctor.FirstName == "Johnny"


def test_delete_doctor(mock_db_session: Session):
    """
    Tests that a doctor can be deleted successfully from the database.

    Creates a new doctor with valid data, then deletes it by ID. Asserts that the
    deleted doctor matches the one created and that the doctor is no longer present
    in the database.
    """
    doctor_data = DoctorCreate(FirstName="Alice", LastName="Fernandes", Specialty = "Oncologist", LicenseNumber="56789", ContactNumber = "9984560000", Email="alice@example.com")
    new_doctor = create_doctor(mock_db_session, doctor_data)
    deleted_doctor = delete_doctor(mock_db_session, new_doctor.DoctorID)
    assert deleted_doctor.FirstName == "Alice"
    assert mock_db_session.query(Doctor).filter(Doctor.DoctorID == new_doctor.DoctorID).first() is None



def test_create_doctor_duplicate_email(mock_db_session: Session):
    """
    Tests that creating a doctor with a duplicate email raises an HTTPException.
    """
    doctor_data1 = DoctorCreate(FirstName="John", LastName="Doe", Specialty = "Neurologist", LicenseNumber="54321", ContactNumber = "9876545678", Email="test_123@example.com")
    create_doctor(mock_db_session, doctor_data1)
    
    doctor_data2 = DoctorCreate(FirstName="Jake", LastName="Davis", Specialty = "Oncologist", LicenseNumber="13579", ContactNumber = "9984567887", Email="test_123@example.com")
    with pytest.raises(HTTPException) as excinfo:
        create_doctor(mock_db_session, doctor_data2)
    assert excinfo.value.status_code == 400
    assert "Email already registered" in str(excinfo.value.detail)


def test_create_doctor_duplicate_license(mock_db_session: Session):
    """
    Tests that creating a doctor with a duplicate license number raises an HTTPException.
    """
    doctor_data1 = DoctorCreate(FirstName="Test1", LastName="Doctor", Specialty="Ophtalmologist", LicenseNumber="12345", ContactNumber = "1234567890", Email="test1@example.com" )
    create_doctor(mock_db_session, doctor_data1)
    
    doctor_data2 = DoctorCreate(FirstName="Test2", LastName="Doctor", Specialty="Cardiologist", LicenseNumber="12345", ContactNumber = "0987654321", Email="test123@example.com" )
    with pytest.raises(HTTPException) as excinfo:
        create_doctor(mock_db_session, doctor_data2)
    assert excinfo.value.status_code == 400
    assert "License number already registered" in str(excinfo.value.detail)



def test_delete_doctor_not_found(mock_db_session: Session):
    """
    Tests that deleting a non-existent doctor raises an HTTPException.
    """
    with pytest.raises(HTTPException) as excinfo:
        delete_doctor(mock_db_session, 999)
    assert excinfo.value.status_code == 404
    assert "Doctor not found" in str(excinfo.value.detail)




def test_get_doctor_not_found(mock_db_session: Session):
    """
    Tests that fetching a non-existent doctor raises an HTTPException.
    """
    with pytest.raises(HTTPException) as excinfo:
        get_doctor(mock_db_session, 999)  # ID that does not exist
    assert excinfo.value.status_code == 404
    assert "Doctor not found" in str(excinfo.value.detail)


def test_update_doctor_duplicate_license(mock_db_session: Session):
    """
    Tests that updating a doctor to have a duplicate license number raises an HTTPException.
    """
    doctor_data1 = DoctorCreate(FirstName="John", LastName="Doe", Specialty="Neurologist", LicenseNumber="12345", ContactNumber="9876545678", Email="test@example.com")
    create_doctor(mock_db_session, doctor_data1)

    doctor_data2 = DoctorCreate(FirstName="Jane", LastName="Smith", Specialty="Cardiologist", LicenseNumber="54321", ContactNumber="8765432109", Email="jane@example.com")
    new_doctor = create_doctor(mock_db_session, doctor_data2)

    updated_data = DoctorUpdate(LicenseNumber="12345")  # Attempt to update to duplicate license number
    with pytest.raises(HTTPException) as excinfo:
        update_doctor(mock_db_session, new_doctor.DoctorID, updated_data)
    assert excinfo.value.status_code == 400
    assert "License number already registered" in str(excinfo.value.detail)

def test_get_all_doctors(mock_db_session: Session):
    """
    Tests that all doctors can be retrieved from the database.
    """
    # Create multiple doctors with unique email addresses
    doctor_data1 = DoctorCreate(
        FirstName="Alice",
        LastName="Johnson",
        Email="alice@example.com",
        LicenseNumber="11111",
        Specialty="Cardiology",
        ContactNumber="1234567890"
    )
    doctor_data2 = DoctorCreate(
        FirstName="Bob",
        LastName="Williams",
        Email="bob@example.com",
        LicenseNumber="22222",
        Specialty="Neurology",
        ContactNumber="2345678901"
    )
    
    create_doctor(mock_db_session, doctor_data1)
    create_doctor(mock_db_session, doctor_data2)
    
    # Test getting all doctors
    doctors = get_all_doctors(mock_db_session)
    assert len(doctors) == 2
    
    # Test skip and limit
    doctors_limited = get_all_doctors(mock_db_session, skip=1, limit=1)
    assert len(doctors_limited) == 1

    # Verify the contents of the retrieved doctors
    assert doctors[0].Email == "alice@example.com"
    assert doctors[1].Email == "bob@example.com"


def test_create_doctor_integrity_error(mock_db_session: Session):
    doctor_data = DoctorCreate(
        FirstName="Test",
        LastName="Doctor",
        Specialty="Cardiologist",
        LicenseNumber="12345",
        ContactNumber="9878656422",
        Email="test@example.com"
    )

    # Mock the add and commit methods of the session
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock(side_effect=IntegrityError(None, None, None))
    mock_db_session.rollback = MagicMock()

    with pytest.raises(HTTPException) as excinfo:
        create_doctor(mock_db_session, doctor_data)

    assert excinfo.value.status_code == 400
    assert "Error creating doctor" in str(excinfo.value.detail)

    # Verify that rollback was called
    mock_db_session.rollback.assert_called_once()

def test_update_doctor_not_found(mock_db_session: Session):
    """
    Tests that updating a non-existent doctor raises an HTTPException and logs a warning.
    """
    # Create an instance of the updated data
    updated_data = DoctorUpdate(FirstName="Johnny", LastName ="Davis", Specialty="Neurologist", LicenseNumber="67890", ContactNumber="8765432109", Email="johnny_davis@example.com")  # Adjust according to your model

    # Mock the get_doctor function to return None
    with patch("app.db.crud.doctor.get_doctor", return_value=None) as mock_get_doctor:
        with patch("app.main.logger.warning") as mock_logger_warning:  # Adjust based on your actual logger import
            with pytest.raises(HTTPException) as excinfo:
                update_doctor(mock_db_session, 89898, updated_data)  # Using a non-existent doctor ID
                
            # Assert that the exception is raised with the correct status and detail
            assert excinfo.value.status_code == 404
            assert "Doctor not found" in str(excinfo.value.detail)

            # Check if the warning log was called with the expected message
            # mock_logger.warning.assert_called_once_with("Doctor with ID 89898 not found for update")
            # mock_get_doctor.assert_called_once_with(mock_db_session, 89898)  # Ensure the get_doctor was called with the right parameters

            # Check if the warning log was called with the expected message
            mock_logger_warning.assert_called_once_with("Doctor with ID 89898 not found for update")
            mock_get_doctor.assert_called_once_with(mock_db_session, 89898)