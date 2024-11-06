# tests/unit/test_doctor_endpoint.py

'''
The file contains tests for FastAPI endpoints, validating CRUD operations for doctor management.
'''

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.api.deps import get_db
from app.core.config import settings
from unittest.mock import patch

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def test_client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.rollback()

    with patch("app.db.base.init"):
        from app.main import app
        app.dependency_overrides[get_db] = override_get_db
        with TestClient(app) as client:
            yield client
        app.dependency_overrides.clear()

def test_create_doctor(test_client):
    doctor_data = {
        "FirstName": "John",
        "LastName": "Doe",
        "Specialty": "Pediatrics",
        "LicenseNumber": "123456",
        "ContactNumber": "1234567890",
        "Email": "john.doe@example.com"
    }
    response = test_client.post(f"{settings.API_V1_STR}/doctors/", json=doctor_data)
    assert response.status_code == 201
    assert response.json()["FirstName"] == doctor_data["FirstName"]

def test_create_doctor_duplicate_entry(test_client):
    doctor_data = {
        "FirstName": "Jane",
        "LastName": "Doe",
        "Specialty": "Cardiology",
        "LicenseNumber": "654321",
        "ContactNumber": "0987654321",
        "Email": "jane.doe@example.com"
    }
    test_client.post(f"{settings.API_V1_STR}/doctors/", json=doctor_data)
    response = test_client.post(f"{settings.API_V1_STR}/doctors/", json=doctor_data)
    assert response.status_code == 400

def test_read_doctors(test_client, test_db):
    response = test_client.get(f"{settings.API_V1_STR}/doctors/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_doctor(test_client, test_db):
    doctor_data = {
        "FirstName": "Alice",
        "LastName": "Smith",
        "Specialty": "Dermatology",
        "LicenseNumber": "789012",
        "ContactNumber": "3213213210",
        "Email": "alice.smith@example.com"
    }
    created_response = test_client.post(f"{settings.API_V1_STR}/doctors/", json=doctor_data)
    doctor_id = created_response.json()["DoctorID"]

    response = test_client.get(f"{settings.API_V1_STR}/doctors/{doctor_id}")
    assert response.status_code == 200
    assert response.json()["FirstName"] == doctor_data["FirstName"]

def test_read_non_existent_doctor(test_client):
    response = test_client.get(f"{settings.API_V1_STR}/doctors/9999")
    assert response.status_code == 404

def test_update_doctor(test_client, test_db):
    doctor_data = {
        "FirstName": "Bob",
        "LastName": "Builder",
        "Specialty": "Construction",
        "LicenseNumber": "345678",
        "ContactNumber": "4564564567",
        "Email": "bob.builder@example.com"
    }
    created_response = test_client.post(f"{settings.API_V1_STR}/doctors/", json=doctor_data)
    doctor_id = created_response.json()["DoctorID"]

    update_data = {
        "FirstName": "Robert",
        "LastName": "Builder",
        "Specialty": "Construction",
        "LicenseNumber": "345678",
        "ContactNumber": "4564564567",
        "Email": "robert.builder@example.com"
    }
    response = test_client.put(f"{settings.API_V1_STR}/doctors/{doctor_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["FirstName"] == update_data["FirstName"]

def test_update_non_existent_doctor(test_client):
    update_data = {
        "FirstName": "Non-existent",
        "LastName": "Doctor",
        "Specialty": "Unknown",
        "LicenseNumber": "000000",
        "ContactNumber": "0000000000",
        "Email": "nonexistent.doctor@example.com"
    }
    response = test_client.put(f"{settings.API_V1_STR}/doctors/9999", json=update_data)
    assert response.status_code == 404

def test_delete_doctor(test_client, test_db):
    doctor_data = {
        "FirstName": "Delete",
        "LastName": "Doctor",
        "Specialty": "General Practice",
        "LicenseNumber": "111222",
        "ContactNumber": "1231231234",
        "Email": "delete.doctor@example.com"
    }
    created_response = test_client.post(f"{settings.API_V1_STR}/doctors/", json=doctor_data)
    doctor_id = created_response.json()["DoctorID"]

    response = test_client.delete(f"{settings.API_V1_STR}/doctors/{doctor_id}")
    assert response.status_code == 204

    get_response = test_client.get(f"{settings.API_V1_STR}/doctors/{doctor_id}")
    assert get_response.status_code == 404

def test_delete_non_existent_doctor(test_client):
    response = test_client.delete(f"{settings.API_V1_STR}/doctors/9999")
    assert response.status_code == 404

def test_create_doctor_invalid_data(test_client):
    invalid_data = {
        "FirstName": "Invalid",
        "LastName": "Doctor",
        "Specialty": "Unknown",
        "LicenseNumber": "not-a-number",
        "ContactNumber": "not-a-number",
        "Email": "invalid-email"
    }
    response = test_client.post(f"{settings.API_V1_STR}/doctors/", json=invalid_data)
    assert response.status_code == 422

def test_create_doctor_missing_field(test_client):
    missing_field_data = {
        "LastName": "Doe",
        "Specialty": "Pediatrics",
        "LicenseNumber": "123456",
        "ContactNumber": "1234567890",
        "Email": "missing.first@example.com"
    }
    response = test_client.post(f"{settings.API_V1_STR}/doctors/", json=missing_field_data)
    assert response.status_code == 422  # Unprocessable Entity

def test_create_doctor_invalid_email(test_client):
    invalid_email_data = {
        "FirstName": "John",
        "LastName": "Doe",
        "Specialty": "Pediatrics",
        "LicenseNumber": "123456",
        "ContactNumber": "1234567890",
        "Email": "invalid-email-format"
    }
    response = test_client.post(f"{settings.API_V1_STR}/doctors/", json=invalid_email_data)
    assert response.status_code == 422

def test_update_doctor_with_invalid_data(test_client, test_db):
    doctor_data = {
        "FirstName": "Alice",
        "LastName": "Jones",
        "Specialty": "Neurology",
        "LicenseNumber": "999888",
        "ContactNumber": "9999999999",
        "Email": "alice.jones@example.com"
    }
    created_response = test_client.post(f"{settings.API_V1_STR}/doctors/", json=doctor_data)
    doctor_id = created_response.json()["DoctorID"]

    invalid_update_data = {
        "FirstName": "Alice",
        "LastName": "Jones",
        "Specialty": "Neurology",
        "LicenseNumber": "invalid",
        "ContactNumber": "not-a-number",
        "Email": "invalid-email"
    }
    response = test_client.put(f"{settings.API_V1_STR}/doctors/{doctor_id}", json=invalid_update_data)
    assert response.status_code == 422

def test_create_doctor_integrity_error(test_client):
    doctor_data = {
        "FirstName": "Jake",
        "LastName": "Doe",
        "Specialty": "Orthopedics",
        "LicenseNumber": "555555",
        "ContactNumber": "9876543210",
        "Email": "jake.doe@example.com"
    }
    test_client.post(f"{settings.API_V1_STR}/doctors/", json=doctor_data)
    response = test_client.post(f"{settings.API_V1_STR}/doctors/", json=doctor_data)
    assert response.status_code == 400
