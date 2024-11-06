# tests/unit/test_patient_visits_endpoint.py

'''
This file contains FastAPI tests for patient visits CRUD operations using pytest and SQLite as the database.
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

def test_create_patient_visit(test_client):
    visit_data = {
        "PatientID": 1,
        "DoctorID": 1,
        "SymptomID": 1,
        "VisitDate": "2024-11-01",
        "DoctorsReportPdfLink": "link/to/report.pdf",
        "PatientFriendlyReportPdfLink": "link/to/patient_report.pdf",
        "Notes": "Initial consultation"
    }
    response = test_client.post(f"{settings.API_V1_STR}/patient_visits/", json=visit_data)
    assert response.status_code == 201
    assert response.json()["VisitDate"] == visit_data["VisitDate"]

def test_create_patient_visit_missing_field(test_client):
    visit_data = {
        "PatientID": 1,
        "DoctorID": 1,
        "SymptomID": 1,
        "Notes": "Follow-up"
    }
    response = test_client.post(f"{settings.API_V1_STR}/patient_visits/", json=visit_data)
    assert response.status_code == 422

def test_read_patient_visits(test_client):
    response = test_client.get(f"{settings.API_V1_STR}/patient_visits/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_patient_visit(test_client):
    visit_data = {
        "PatientID": 2,
        "DoctorID": 1,
        "SymptomID": 1,
        "VisitDate": "2024-11-02",
        "DoctorsReportPdfLink": "link/to/report2.pdf",
        "PatientFriendlyReportPdfLink": "link/to/patient_report2.pdf",
        "Notes": "Routine check-up"
    }
    created_response = test_client.post(f"{settings.API_V1_STR}/patient_visits/", json=visit_data)
    visit_id = created_response.json()["VisitID"]

    response = test_client.get(f"{settings.API_V1_STR}/patient_visits/{visit_id}")
    assert response.status_code == 200
    assert response.json()["VisitDate"] == visit_data["VisitDate"]

def test_read_non_existent_patient_visit(test_client):
    response = test_client.get(f"{settings.API_V1_STR}/patient_visits/9999")
    assert response.status_code == 404

def test_update_patient_visit(test_client):
    visit_data = {
        "PatientID": 3,
        "DoctorID": 1,
        "SymptomID": 1,
        "VisitDate": "2024-11-03",
        "DoctorsReportPdfLink": "link/to/report3.pdf",
        "PatientFriendlyReportPdfLink": "link/to/patient_report3.pdf",
        "Notes": "Follow-up appointment"
    }
    created_response = test_client.post(f"{settings.API_V1_STR}/patient_visits/", json=visit_data)
    visit_id = created_response.json()["VisitID"]

    update_data = {
        "PatientID": 3,
        "DoctorID": 1,
        "SymptomID": 1,
        "VisitDate": "2024-11-04",
        "DoctorsReportPdfLink": "link/to/updated_report3.pdf",
        "PatientFriendlyReportPdfLink": "link/to/updated_patient_report3.pdf",
        "Notes": "Updated notes"
    }
    response = test_client.put(f"{settings.API_V1_STR}/patient_visits/{visit_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["VisitDate"] == update_data["VisitDate"]

def test_update_non_existent_patient_visit(test_client):
    update_data = {
        "PatientID": 9999,
        "DoctorID": 9999,
        "SymptomID": 9999,
        "VisitDate": "2024-11-05",
        "DoctorsReportPdfLink": "link/to/non_existent.pdf",
        "PatientFriendlyReportPdfLink": "link/to/non_existent_patient_report.pdf",
        "Notes": "Non-existent visit"
    }
    response = test_client.put(f"{settings.API_V1_STR}/patient_visits/9999", json=update_data)
    assert response.status_code == 404

def test_delete_patient_visit(test_client):
    visit_data = {
        "PatientID": 4,
        "DoctorID": 1,
        "SymptomID": 1,
        "VisitDate": "2024-11-06",
        "DoctorsReportPdfLink": "link/to/report4.pdf",
        "PatientFriendlyReportPdfLink": "link/to/patient_report4.pdf",
        "Notes": "New patient"
    }
    created_response = test_client.post(f"{settings.API_V1_STR}/patient_visits/", json=visit_data)
    visit_id = created_response.json()["VisitID"]

    response = test_client.delete(f"{settings.API_V1_STR}/patient_visits/{visit_id}")
    assert response.status_code == 204

    get_response = test_client.get(f"{settings.API_V1_STR}/patient_visits/{visit_id}")
    assert get_response.status_code == 404

def test_delete_non_existent_patient_visit(test_client):
    response = test_client.delete(f"{settings.API_V1_STR}/patient_visits/9999")
    assert response.status_code == 404

def test_create_patient_visit_invalid_data(test_client):
    invalid_data = {
        "PatientID": "not-a-number",
        "DoctorID": 1,
        "SymptomID": 1,
        "VisitDate": "2024-11-07",
        "DoctorsReportPdfLink": "link/to/report_invalid.pdf",
        "PatientFriendlyReportPdfLink": "link/to/patient_report_invalid.pdf",
        "Notes": "Invalid visit"
    }
    response = test_client.post(f"{settings.API_V1_STR}/patient_visits/", json=invalid_data)
    assert response.status_code == 422
