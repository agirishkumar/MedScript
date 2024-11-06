# tests/unit/test_patient_symptoms_endpoint.py

'''
The file tests CRUD operations for patient symptoms using FastAPI, SQLite, and pytest fixtures.
'''

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.api.deps import get_db
from app.db.models.patient_symptoms import PatientSymptom
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

def test_create_patient_symptom(test_client):
    symptom_data = {
        "PatientID": 1,
        "SymptomDescription": "Headache",
        "ModelInputDescription": "Severe headache",
        "Severity": "High",
        "Duration": "2 days",
        "AssociatedConditions": "N/A"
    }
    response = test_client.post(f"{settings.API_V1_STR}/patient_symptoms/", json=symptom_data)
    assert response.status_code == 201
    assert response.json()["SymptomDescription"] == symptom_data["SymptomDescription"]

def test_read_patient_symptoms(test_client):
    response = test_client.get(f"{settings.API_V1_STR}/patient_symptoms/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_patient_symptom(test_client):
    symptom_data = {
        "PatientID": 2,
        "SymptomDescription": "Fever",
        "ModelInputDescription": "High fever for three days",
        "Severity": "High",
        "Duration": "3 days",
        "AssociatedConditions": "N/A"
    }
    created_response = test_client.post(f"{settings.API_V1_STR}/patient_symptoms/", json=symptom_data)
    symptom_id = created_response.json()["SymptomID"]

    response = test_client.get(f"{settings.API_V1_STR}/patient_symptoms/{symptom_id}")
    assert response.status_code == 200
    assert response.json()["SymptomDescription"] == symptom_data["SymptomDescription"]

def test_read_non_existent_patient_symptom(test_client):
    response = test_client.get(f"{settings.API_V1_STR}/patient_symptoms/9999")
    assert response.status_code == 404

def test_update_patient_symptom(test_client):
    symptom_data = {
        "PatientID": 3,
        "SymptomDescription": "Sore throat",
        "ModelInputDescription": "Throat pain",
        "Severity": "Low",
        "Duration": "2 days",
        "AssociatedConditions": "N/A"
    }
    created_response = test_client.post(f"{settings.API_V1_STR}/patient_symptoms/", json=symptom_data)
    symptom_id = created_response.json()["SymptomID"]

    update_data = {
        "PatientID": 3,
        "SymptomDescription": "Severe sore throat",
        "ModelInputDescription": "Severe throat pain",
        "Severity": "High",
        "Duration": "3 days",
        "AssociatedConditions": "N/A"
    }
    response = test_client.put(f"{settings.API_V1_STR}/patient_symptoms/{symptom_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["SymptomDescription"] == update_data["SymptomDescription"]

def test_update_non_existent_patient_symptom(test_client):
    update_data = {
        "PatientID": 9999,
        "SymptomDescription": "Non-existent",
        "ModelInputDescription": "No description",
        "Severity": "Unknown",
        "Duration": "N/A",
        "AssociatedConditions": "N/A"
    }
    response = test_client.put(f"{settings.API_V1_STR}/patient_symptoms/9999", json=update_data)
    assert response.status_code == 404

def test_delete_patient_symptom(test_client):
    symptom_data = {
        "PatientID": 4,
        "SymptomDescription": "Nausea",
        "ModelInputDescription": "Feeling sick",
        "Severity": "Medium",
        "Duration": "1 day",
        "AssociatedConditions": "N/A"
    }
    created_response = test_client.post(f"{settings.API_V1_STR}/patient_symptoms/", json=symptom_data)
    symptom_id = created_response.json()["SymptomID"]

    response = test_client.delete(f"{settings.API_V1_STR}/patient_symptoms/{symptom_id}")
    assert response.status_code == 204

    get_response = test_client.get(f"{settings.API_V1_STR}/patient_symptoms/{symptom_id}")
    assert get_response.status_code == 404

def test_delete_non_existent_patient_symptom(test_client):
    response = test_client.delete(f"{settings.API_V1_STR}/patient_symptoms/9999")
    assert response.status_code == 404

def test_create_patient_symptom_invalid_data(test_client):
    invalid_data = {
        "PatientID": "not-a-number",
        "SymptomDescription": "Invalid",
        "Severity": "High",
        "Duration": "2 days",
        "AssociatedConditions": "N/A"
    }
    response = test_client.post(f"{settings.API_V1_STR}/patient_symptoms/", json=invalid_data)
    assert response.status_code == 422
