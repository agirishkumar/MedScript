# tests/unit/test_patient_symptoms_crud.py

'''
The file tests CRUD operations for patient symptoms, handling exceptions and database interactions.
'''

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.db.models.patient_symptoms import PatientSymptom
from app.db.schemas.patient_symptoms import PatientSymptomCreate, PatientSymptomUpdate
from app.db.crud.patient_symptoms import (
    get_patient_symptom,
    get_patient_symptoms_by_patient_id,
    get_all_patient_symptoms,
    create_patient_symptom,
    update_patient_symptom,
    delete_patient_symptom,
)

# Sample data
sample_symptom_id = 1
sample_symptom_data = {"PatientID": sample_symptom_id, "SymptomDescription": "Headache"}
sample_symptom_create = PatientSymptomCreate(**sample_symptom_data)
sample_symptom_update = PatientSymptomUpdate(**{"SymptomDescription": "Migraine"})

@pytest.fixture
def mock_db_session():
    """Fixture to mock the database session."""
    return MagicMock(spec=Session)

# Test get_patient_symptom
def test_get_patient_symptom_existing(mock_db_session):
    """Test retrieving an existing patient symptom."""
    symptom = PatientSymptom(**sample_symptom_data)

    # Setting up the mock query
    mock_db_session.query.return_value.filter.return_value.first.return_value = symptom

    result = get_patient_symptom(mock_db_session, sample_symptom_id)
    assert result == symptom

def test_get_patient_symptom_not_found(mock_db_session):
    """Test retrieving a non-existing patient symptom."""
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_patient_symptom(mock_db_session, sample_symptom_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Patient symptom not found"


# Test get_patient_symptoms_by_patient_id
def test_get_patient_symptoms_by_patient_id(mock_db_session):
    """
    Test retrieving all patient symptoms by patient ID.
    """
    sample_symptom_data = {
        "PatientID": 1,
        "SymptomDescription": "Persistent headache with occasional dizziness.",
        "ModelInputDescription": None,
        "Severity": "Moderate",
        "Duration": "3 weeks",
        "AssociatedConditions": "Hypertension, Seasonal allergies",
        "SymptomID": 101,
        "SymptomEnteredDate": "2024-11-15T06:13:14.615640"
    }

    mock_symptom = PatientSymptom(**sample_symptom_data)

    mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_symptom]

    result = get_patient_symptoms_by_patient_id(mock_db_session, 1)

    assert len(result) == 1
    assert result[0].PatientID == 1
    assert result[0].SymptomDescription == "Persistent headache with occasional dizziness."
    assert result[0].Severity == "Moderate"
    assert result[0].Duration == "3 weeks"
    assert result[0].AssociatedConditions == "Hypertension, Seasonal allergies"

    mock_db_session.query.assert_called_once()
    mock_db_session.query.return_value.filter.assert_called_once_with(PatientSymptom.PatientID == 1)
    mock_db_session.query.return_value.filter.return_value.all.assert_called_once()

# Test get_all_patient_symptoms
def test_get_all_patient_symptoms(mock_db_session):
    """Test retrieving all patient symptoms."""
    symptoms = [PatientSymptom(**sample_symptom_data)]

    # Mocking the query and its chain for offset and limit
    mock_db_session.query.return_value.offset.return_value.limit.return_value.all.return_value = symptoms

    result = get_all_patient_symptoms(mock_db_session)
    assert result == symptoms

# Test create_patient_symptom
def test_create_patient_symptom(mock_db_session):
    """Test creating a new patient symptom."""
    symptom = PatientSymptom(**sample_symptom_data)

    # Mocking add, commit, and refresh methods
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock(return_value=symptom)

    result = create_patient_symptom(mock_db_session, sample_symptom_create)

    # Compare specific attributes instead of the entire object
    assert result.SymptomID == symptom.SymptomID
    assert result.SymptomDescription == symptom.SymptomDescription


def test_create_patient_symptom_integrity_error(mock_db_session):
    """Test handling integrity error during patient symptom creation."""
    mock_db_session.add = MagicMock()
    mock_db_session.commit.side_effect = IntegrityError("Integrity error", params=None, orig=None)

    with pytest.raises(HTTPException) as exc_info:
        create_patient_symptom(mock_db_session, sample_symptom_create)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Error creating patient symptom"

# Test update_patient_symptom
def test_update_patient_symptom(mock_db_session):
    """Test updating an existing patient symptom."""
    symptom = PatientSymptom(**sample_symptom_data)
    mock_db_session.query.return_value.filter.return_value.first.return_value = symptom

    # Mocking commit and refresh methods
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock(return_value=symptom)

    result = update_patient_symptom(mock_db_session, sample_symptom_id, sample_symptom_update)
    assert result.SymptomDescription == "Migraine"

def test_update_patient_symptom_not_found(mock_db_session):
    """Test updating a non-existing patient symptom."""
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        update_patient_symptom(mock_db_session, sample_symptom_id, sample_symptom_update)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Patient symptom not found"

def test_update_patient_symptom_integrity_error(mock_db_session):
    """Test handling integrity error during patient symptom update."""
    symptom = PatientSymptom(**sample_symptom_data)
    mock_db_session.query.return_value.filter.return_value.first.return_value = symptom

    mock_db_session.commit.side_effect = IntegrityError("Integrity error", params=None, orig=None)

    with pytest.raises(HTTPException) as exc_info:
        update_patient_symptom(mock_db_session, sample_symptom_id, sample_symptom_update)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Error updating patient symptom"

# Test delete_patient_symptom
def test_delete_patient_symptom(mock_db_session):
    """Test deleting a patient symptom."""
    symptom = PatientSymptom(**sample_symptom_data)
    mock_db_session.query.return_value.filter.return_value.first.return_value = symptom

    mock_db_session.delete = MagicMock()
    mock_db_session.commit = MagicMock()

    result = delete_patient_symptom(mock_db_session, sample_symptom_id)
    assert result == symptom

def test_delete_patient_symptom_not_found(mock_db_session):
    """Test deleting a non-existing patient symptom."""
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_patient_symptom(mock_db_session, sample_symptom_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Patient symptom not found"
