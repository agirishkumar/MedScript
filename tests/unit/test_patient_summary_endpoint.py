# tests/unit/test_patient_summary_endpoint.py

'''
The file tests patient summary retrieval, validating correct data, visits, symptoms, and error handling.
'''

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.api.deps import get_db
from app.db.models.patient_details import PatientDetails
from app.db.models.patient_symptoms import PatientSymptom
from app.db.models.patient_visits import PatientVisit
from app.db.models.doctor import Doctor
from unittest.mock import patch
from datetime import datetime
from app.core.config import settings

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

def test_get_patient_summary_with_full_data(test_client, test_db):
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

    patient_id = patient_details.PatientID

    doctor = Doctor(
        FirstName="Dr. Emily",
        LastName="Johnson",
        Specialty="General Medicine",
        LicenseNumber="A123456",
        ContactNumber="9876543210",
        Email="emily.johnson@example.com"
    )
    test_db.add(doctor)
    test_db.commit()

    doctor_id = doctor.DoctorID

    symptom = PatientSymptom(
        PatientID=patient_id,
        SymptomDescription="Headache",
        Severity="Mild",
        Duration="2 hours"
    )
    test_db.add(symptom)
    test_db.commit()

    symptom_id = symptom.SymptomID

    visit = PatientVisit(
        PatientID=patient_id,
        DoctorID=doctor_id,
        SymptomID=symptom_id,
        VisitDate=datetime.strptime("2024-11-01", "%Y-%m-%d"),
        DoctorsReportPdfLink="link/to/report.pdf",
        PatientFriendlyReportPdfLink="link/to/patient_report.pdf",
        Notes="Initial consultation"
    )
    test_db.add(visit)
    test_db.commit()

    response = test_client.get(f"{settings.API_V1_STR}/patient_summary/{patient_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["patient"]["FirstName"] == "Mark"
    assert data["patient"]["LastName"] == "Smith"
    assert data["patient"]["Gender"] == "Male"
    assert data["patient"]["ContactNumber"] == "5555555555"

    assert len(data["visits"]) == 1
    visit = data["visits"][0]
    assert visit["visit"]["VisitDate"] == "2024-11-01"
    assert visit["visit"]["DoctorsReportPdfLink"] == "link/to/report.pdf"
    assert visit["doctor"]["FirstName"] == "Dr. Emily"

    assert len(visit["symptoms"]) == 1
    assert visit["symptoms"][0]["SymptomDescription"] == "Headache"
    assert visit["symptoms"][0]["Severity"] == "Mild"

def test_get_patient_summary_patient_not_found(test_client):
    response = test_client.get(f"{settings.API_V1_STR}/patient_summary/999")
    assert response.status_code == 404

def test_get_patient_summary_no_visits_or_symptoms(test_client, test_db):
    patient_details = PatientDetails(
        FirstName="Alice",
        LastName="Wonderland",
        DateOfBirth=datetime.strptime("1992-01-01", "%Y-%m-%d").date(),
        Gender="Female",
        Address="456 Imaginary Lane",
        ContactNumber="555-000-0000",
        Email="alice@example.com",
        Height=165.0,
        Weight=130.0,
        BloodType="A+"
    )
    test_db.add(patient_details)
    test_db.commit()

    patient_id = patient_details.PatientID
    response = test_client.get(f"{settings.API_V1_STR}/patient_summary/{patient_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["patient"]["FirstName"] == "Alice"
    assert data["visits"] == []  # No visits or symptoms should return an empty list

def test_get_patient_summary_multiple_visits_for_same_symptom(test_client, test_db):
    # Create a patient
    patient_details = PatientDetails(
        FirstName="Bob",
        LastName="Builder",
        DateOfBirth=datetime.strptime("1988-02-15", "%Y-%m-%d").date(),
        Gender="Male",
        Address="789 Construction Ave",
        ContactNumber="555-111-2222",
        Email="bob.builder@example.com",
        Height=180.0,
        Weight=190.0,
        BloodType="O-"
    )
    test_db.add(patient_details)
    test_db.commit()

    patient_id = patient_details.PatientID

    # Create a doctor
    doctor = Doctor(
        FirstName="Dr. Green",
        LastName="Thumb",
        Specialty="Gardening",
        LicenseNumber="B654321",
        ContactNumber="555-123-4567",
        Email="dr.green@example.com"
    )
    test_db.add(doctor)
    test_db.commit()

    doctor_id = doctor.DoctorID

    # Create a symptom
    symptom = PatientSymptom(
        PatientID=patient_id,
        SymptomDescription="Back Pain",
        Severity="Moderate",
        Duration="1 week"
    )
    test_db.add(symptom)
    test_db.commit()

    symptom_id = symptom.SymptomID

    # Create multiple visits for the same symptom
    visit1 = PatientVisit(
        PatientID=patient_id,
        DoctorID=doctor_id,
        SymptomID=symptom_id,
        VisitDate=datetime.strptime("2024-11-01", "%Y-%m-%d"),
        DoctorsReportPdfLink="link/to/report1.pdf",
        PatientFriendlyReportPdfLink="link/to/patient_report1.pdf",
        Notes="Initial consultation"
    )
    test_db.add(visit1)

    visit2 = PatientVisit(
        PatientID=patient_id,
        DoctorID=doctor_id,
        SymptomID=symptom_id,
        VisitDate=datetime.strptime("2024-11-15", "%Y-%m-%d"),
        DoctorsReportPdfLink="link/to/report2.pdf",
        PatientFriendlyReportPdfLink="link/to/patient_report2.pdf",
        Notes="Follow-up consultation"
    )
    test_db.add(visit2)
    test_db.commit()

    response = test_client.get(f"{settings.API_V1_STR}/patient_summary/{patient_id}")
    assert response.status_code == 200
    data = response.json()

    assert len(data["visits"]) == 2
    assert data["visits"][0]["visit"]["VisitDate"] == "2024-11-01"
    assert data["visits"][1]["visit"]["VisitDate"] == "2024-11-15"

