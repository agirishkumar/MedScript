# tests/unit/test_patient_endpoint.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.api.deps import get_db
from app.db.models.patient import Patient
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_db():
    """
    Creates a test database and provides a database session for testing.

    This fixture creates a test database, and provides a database session that
    can be used for testing. The session is rolled back after each test, to
    ensure the database is in a clean state for each test.

    The scope of this fixture is "module", which means that the test database is
    created and dropped once per test module. This is more efficient than
    creating and dropping the database once per test.

    Yields the test session.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def test_client(test_db):
    """
    Creates a FastAPI test client with a test database session.

    Uses the `test_db` fixture to create a database session, and overrides the
    `get_db` dependency to use the test session. This allows the test client to
    interact with the test database.

    Yields the test client.
    """
    def override_get_db():
        """
        Overrides the get_db dependency to use the test database session.

        Yields the test session, and rolls back the session at the end of the
        context.
        """
        try:
            yield test_db
        finally:
            test_db.rollback()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

def test_create_patient(test_client):
    """
    Tests that a patient can be created successfully with valid data.

    Creates a new patient with valid data, then asserts that the response is a 201
    Created and that the patient's data matches the expected data.
    """
    patient_data = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com"
    }
    response = test_client.post(f"{settings.API_V1_STR}/patients/", json=patient_data)
    assert response.status_code == 201
    assert response.json()["name"] == patient_data["name"]
    assert response.json()["age"] == patient_data["age"]
    assert response.json()["email"] == patient_data["email"]

def test_read_patients(test_client, test_db):
    
    """
    Tests that a list of patients can be retrieved successfully.
    
    Creates a new patient, then retrieves a list of all patients. Asserts that the
    response is a 200 OK and that the list of patients is not empty.
    """
    
    test_db.add(Patient(name="Test Patient", age=25, email="test@example.com"))
    test_db.commit()

    response = test_client.get(f"{settings.API_V1_STR}/patients/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_patient(test_client, test_db):
    
    """
    Tests that a patient can be retrieved by ID.

    Creates a new patient, then fetches it by ID. Asserts that the patient's data
    matches the expected data.
    """
    patient = Patient(name="Read Test", age=35, email="read@example.com")
    test_db.add(patient)
    test_db.commit()

    response = test_client.get(f"{settings.API_V1_STR}/patients/{patient.id}")
    assert response.status_code == 200
    assert response.json()["name"] == patient.name
    assert response.json()["age"] == patient.age
    assert response.json()["email"] == patient.email

def test_update_patient(test_client, test_db):
    
    """
    Tests that a patient can be updated successfully with valid data.

    Creates a new patient, then updates it by ID. Asserts that the updated patient
    returns a 200 OK response and that the patient's data has been updated in the
    database.
    """
    patient = Patient(name="Update Test", age=40, email="update@example.com")
    test_db.add(patient)
    test_db.commit()

    update_data = {
        "name": "Updated Name",
        "age": 41,
        "email": "updated@example.com"
    }
    response = test_client.put(f"{settings.API_V1_STR}/patients/{patient.id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]
    assert response.json()["age"] == update_data["age"]
    assert response.json()["email"] == update_data["email"]

def test_delete_patient(test_client, test_db):
    """
    Tests that a patient can be deleted successfully.

    Creates a new patient, then deletes it by ID. Asserts that the deleted patient
    returns a 204 No Content response and that the patient is no longer present
    in the database.
    """
    patient = Patient(name="Delete Test", age=50, email="delete@example.com")
    test_db.add(patient)
    test_db.commit()

    response = test_client.delete(f"{settings.API_V1_STR}/patients/{patient.id}")
    assert response.status_code == 204

    # Verify patient is deleted
    get_response = test_client.get(f"{settings.API_V1_STR}/patients/{patient.id}")
    assert get_response.status_code == 404

def test_read_non_existent_patient(test_client):
    """
    Tests that reading a non-existent patient returns a 404 error.
    """
    response = test_client.get(f"{settings.API_V1_STR}/patients/9999")
    assert response.status_code == 404

def test_update_non_existent_patient(test_client):
    """
    Tests that updating a non-existent patient returns a 404 error.
    """
    update_data = {"name": "Non-existent", "age": 99, "email": "nonexistent@example.com"}
    response = test_client.put(f"{settings.API_V1_STR}/patients/9999", json=update_data)
    assert response.status_code == 404

def test_delete_non_existent_patient(test_client):
    """
    Tests that deleting a non-existent patient returns a 404 error.
    """
    response = test_client.delete(f"{settings.API_V1_STR}/patients/9999")
    assert response.status_code == 404

def test_create_patient_invalid_data(test_client):
    """
    Tests that creating a patient with invalid data returns a 422 error.
    """
    invalid_data = {
        "name": "Invalid",
        "age": "not a number",
        "email": "invalid-email"
    }
    response = test_client.post(f"{settings.API_V1_STR}/patients/", json=invalid_data)
    assert response.status_code == 422  # Unprocessable Entity