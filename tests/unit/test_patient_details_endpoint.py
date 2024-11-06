# tests/unit/test_patient_details_endpoint.py

'''
This file contains tests for CRUD operations on patient details using FastAPI and SQLAlchemy.
'''

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.api.deps import get_db
from app.db.models.patient_details import PatientDetails
from app.core.config import settings
from unittest.mock import patch
from datetime import datetime

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

def test_create_patient_details(test_client):
    patient_details_data = {
        "FirstName": "John",
        "LastName": "Doe",
        "DateOfBirth": datetime.strptime("1990-01-01", "%Y-%m-%d").date().isoformat(),
        "Gender": "Male",
        "Address": "123 Main St",
        "ContactNumber": "1234567890",
        "Email": "john.doe@example.com",
        "Height": 175.3,
        "Weight": 150.0,
        "BloodType": "O+"
    }
    response = test_client.post(f"{settings.API_V1_STR}/patient_details/", json=patient_details_data)
    assert response.status_code == 201
    assert response.json()["FirstName"] == patient_details_data["FirstName"]


def test_read_patient_details(test_client, test_db):
    patient_details = PatientDetails(
        FirstName="Jane",
        LastName="Doe",
        DateOfBirth=datetime.strptime("1992-02-02", "%Y-%m-%d").date(),
        Gender="Female",
        Address="456 Another St",
        ContactNumber="0987654321",
        Email="jane.doe@example.com",
        Height=165.0,
        Weight=130.0,
        BloodType="A+"
    )
    test_db.add(patient_details)
    test_db.commit()

    response = test_client.get(f"{settings.API_V1_STR}/patient_details/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_patient_detail(test_client, test_db):
    patient_details = PatientDetails(
        FirstName="Mark",
        LastName="Smith",
        DateOfBirth=datetime.strptime("1985-03-03", "%Y-%m-%d").date(),
        Gender="Male",
        Address="789 Different St",
        ContactNumber="5555555555",
        Email="mark.smith@example.com",
        Height=180.0,
        Weight=175.0,
        BloodType="B+"
    )
    test_db.add(patient_details)
    test_db.commit()

    response = test_client.get(f"{settings.API_V1_STR}/patient_details/{patient_details.PatientID}")
    assert response.status_code == 200
    assert response.json()["FirstName"] == patient_details.FirstName

def test_update_patient_detail(test_client, test_db):
    patient_details = PatientDetails(
        FirstName="Alice",
        LastName="Johnson",
        DateOfBirth=datetime.strptime("1993-04-04", "%Y-%m-%d").date(),
        Gender="Female",
        Address="321 Update Ave",
        ContactNumber="7777777777",
        Email="alice.johnson@example.com",
        Height=170.0,
        Weight=140.0,
        BloodType="AB+"
    )
    test_db.add(patient_details)
    test_db.commit()

    update_data = {
        "FirstName": "Alicia",
        "LastName": "Johnson",
        "DateOfBirth": "1993-04-04",
        "Gender": "Female",
        "Address": "321 Updated Ave",
        "ContactNumber": "7777777777",
        "Email": "alicia.johnson@example.com",
        "Height": 172.0,
        "Weight": 145.0,
        "BloodType": "AB+"
    }
    response = test_client.put(f"{settings.API_V1_STR}/patient_details/{patient_details.PatientID}", json=update_data)
    assert response.status_code == 200
    assert response.json()["FirstName"] == update_data["FirstName"]

def test_delete_patient_detail(test_client, test_db):
    patient_details = PatientDetails(
        FirstName="Delete",
        LastName="Patient",
        DateOfBirth=datetime.strptime("1995-05-05", "%Y-%m-%d").date(),
        Gender="Male",
        Address="999 Delete St",
        ContactNumber="1231231234",
        Email="delete.patient@example.com",
        Height=165.0,
        Weight=155.0,
        BloodType="O+"
    )
    test_db.add(patient_details)
    test_db.commit()

    response = test_client.delete(f"{settings.API_V1_STR}/patient_details/{patient_details.PatientID}")
    assert response.status_code == 204

    get_response = test_client.get(f"{settings.API_V1_STR}/patient_details/{patient_details.PatientID}")
    assert get_response.status_code == 404

def test_read_non_existent_patient_detail(test_client):
    response = test_client.get(f"{settings.API_V1_STR}/patient_details/9999")
    assert response.status_code == 404

def test_update_non_existent_patient_detail(test_client):
    update_data = {
        "FirstName": "Non-existent",
        "LastName": "Patient",
        "DateOfBirth": "1995-05-05",
        "Gender": "Male",
        "Address": "123 Non-existent St",
        "ContactNumber": "1111111111",
        "Email": "nonexistent.patient@example.com",
        "Height": 170.0,
        "Weight": 150.0,
        "BloodType": "O+"
    }
    response = test_client.put(f"{settings.API_V1_STR}/patient_details/9999", json=update_data)
    assert response.status_code == 404

def test_delete_non_existent_patient_detail(test_client):
    response = test_client.delete(f"{settings.API_V1_STR}/patient_details/9999")
    assert response.status_code == 404

def test_create_patient_details_invalid_data(test_client):
    invalid_data = {
        "FirstName": "Invalid",
        "LastName": "Patient",
        "DateOfBirth": "not-a-date",
        "Gender": "Unknown",
        "Address": "Invalid Address",
        "ContactNumber": "not-a-number",
        "Email": "invalid-email",
        "Height": "not-a-number",
        "Weight": "not-a-number",
        "BloodType": "ZZ"
    }
    response = test_client.post(f"{settings.API_V1_STR}/patient_details/", json=invalid_data)
    assert response.status_code == 422  # Unprocessable Entity

def test_create_patient_details_missing_field(test_client):
    missing_field_data = {
        "LastName": "Doe",
        "DateOfBirth": "1990-01-01",
        "Gender": "Male",
        "Address": "123 Main St",
        "ContactNumber": "1234567890",
        "Email": "john.doe@example.com",
        "Height": 175.3,
        "Weight": 150.0,
        "BloodType": "O+"
    }
    response = test_client.post(f"{settings.API_V1_STR}/patient_details/", json=missing_field_data)
    assert response.status_code == 422  # Unprocessable Entity

def test_create_patient_details_invalid_email(test_client):
    invalid_email_data = {
        "FirstName": "John",
        "LastName": "Doe",
        "DateOfBirth": "1990-01-01",
        "Gender": "Male",
        "Address": "123 Main St",
        "ContactNumber": "1234567890",
        "Email": "invalid-email-format",
        "Height": 175.3,
        "Weight": 150.0,
        "BloodType": "O+"
    }
    response = test_client.post(f"{settings.API_V1_STR}/patient_details/", json=invalid_email_data)
    assert response.status_code == 422

def test_read_patient_detail_with_invalid_id(test_client):
    response = test_client.get(f"{settings.API_V1_STR}/patient_details/67")
    assert response.status_code == 404

def test_update_patient_detail_with_invalid_data(test_client, test_db):
    patient_details = PatientDetails(
        FirstName="Bob",
        LastName="Builder",
        DateOfBirth=datetime.strptime("1988-08-08", "%Y-%m-%d").date(),
        Gender="Male",
        Address="123 Construction Way",
        ContactNumber="8888888888",
        Email="bob.builder@example.com",
        Height=180.0,
        Weight=160.0,
        BloodType="AB+"
    )
    test_db.add(patient_details)
    test_db.commit()

    invalid_update_data = {
        "FirstName": "Bob",
        "LastName": "Builder",
        "DateOfBirth": "not-a-date",
        "Gender": "Unknown",
        "Address": "123 Construction Way",
        "ContactNumber": "8888888888",
        "Email": "bob.builder@example.com",
        "Height": "not-a-number",
        "Weight": "not-a-number",
        "BloodType": "ZZ"
    }
    response = test_client.put(f"{settings.API_V1_STR}/patient_details/{patient_details.PatientID}", json=invalid_update_data)
    assert response.status_code == 422

def test_create_patient_details_duplicate_entry(test_client):
    patient_details_data = {
        "FirstName": "John",
        "LastName": "Doe",
        "DateOfBirth": datetime.strptime("1990-01-01", "%Y-%m-%d").date().isoformat(),
        "Gender": "Male",
        "Address": "123 Main St",
        "ContactNumber": "1234567890",
        "Email": "john.doe@example.com",
        "Height": 175.3,
        "Weight": 150.0,
        "BloodType": "O+"
    }
    test_client.post(f"{settings.API_V1_STR}/patient_details/", json=patient_details_data)
    response = test_client.post(f"{settings.API_V1_STR}/patient_details/", json=patient_details_data)
    assert response.status_code == 400

