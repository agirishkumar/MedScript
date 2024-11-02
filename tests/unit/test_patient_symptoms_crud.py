# tests/unit/test_doctor_crud.py

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from app.db.crud.patient_symptoms import (
    get_patient_symptom,
    get_all_patient_symptoms,
    create_patient_symptom,
    update_patient_symptom,
    delete_patient_symptom,
)
from app.db.models.patient_symptoms import PatientSymptom
from app.db.schemas.patient_symptoms import PatientSymptomCreate, PatientSymptomUpdate


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


def test_create_patient_symptom(mock_db_session):
    """
    Tests that a new doctor can be created successfully with valid data.
    """
    patient_symptom_data = PatientSymptomCreate(
        PatientID=1,
        SymptomDescription="Fever",
        ModelInputDescription="High temperature"
    )
    symptom = create_patient_symptom(mock_db_session, patient_symptom_data)
    assert symptom.PatientID == 1
    assert symptom.SymptomDescription == "Fever"
    assert symptom.ModelInputDescription == "High temperature"

def test_get_patient_symptom(mock_db_session):

    patient_symptom_data = PatientSymptomCreate( PatientID=1,SymptomDescription="Fever", ModelInputDescription="High temperature")
    new_patient_symptom = create_patient_symptom(mock_db_session, patient_symptom_data)
    fetched_patient_symptom = get_patient_symptom(mock_db_session, new_patient_symptom.PatientID)
    assert fetched_patient_symptom.PatientID == 1
    assert fetched_patient_symptom.SymptomDescription == "Fever"
    assert fetched_patient_symptom.ModelInputDescription == "High temperature"

# def test_update_patient_symptom(mock_db_session):
    
#     patient_symptom_data = PatientSymptomCreate( PatientID=1,SymptomDescription="Fever", ModelInputDescription="High temperature")
#     new_patient_symptom = create_patient_symptom(mock_db_session, patient_symptom_data)
#     updated_patient_symptom_data = PatientSymptomUpdate(SymptomDescription = "Cough")
#     patient_symptom_data = updated_patient_symptom_data (mock_db_session, new_patient_symptom.PatientID, updated_patient_symptom_data)
#     assert patient_symptom_data.SymptomDescription == "Cough"


def test_update_patient_symptom(mock_db_session):
    patient_symptom_data = PatientSymptomCreate(PatientID=1,SymptomDescription="Headache", ModelInputDescription="Throbbing pain")
    new_patient_symptom = create_patient_symptom(mock_db_session, patient_symptom_data)
    updated_data = PatientSymptomUpdate(SymptomDescription="Severe Headache", ModelInputDescription="Throbbing pain")
    updated_patient_symptom = update_patient_symptom(mock_db_session, new_patient_symptom.SymptomID, updated_data)
    assert updated_patient_symptom.SymptomDescription == "Severe Headache"
    assert updated_patient_symptom.ModelInputDescription == "Throbbing pain"  # Unchanged field

def test_delete_patient_symptom(mock_db_session):
    patient_symptom_data = PatientSymptomCreate(PatientID=1, SymptomDescription="Fever", ModelInputDescription="High temperature")
    new_patient_symptom = create_patient_symptom(mock_db_session, patient_symptom_data)
    deleted_patient_symptom = delete_patient_symptom(mock_db_session, new_patient_symptom.PatientID)
    assert deleted_patient_symptom.SymptomDescription == "Fever"
    assert mock_db_session.query(PatientSymptom).filter(PatientSymptom.PatientID == new_patient_symptom.PatientID).first() is None