# tests/unit/test_schemas.py

import pytest
from app.db.schemas.patient import PatientCreate, PatientUpdate, Patient
from pydantic import ValidationError
from datetime import datetime

def test_patient_schema():
    """
    Tests that a valid PatientCreate schema can be created and serialized to a dictionary.
    """
    patient = PatientCreate(name="John", age=30, email="john@example.com")
    patient_data = patient.model_dump()  
    assert patient_data["name"] == "John"


def test_invalid_patient_create_schema():
    """
    Tests that a PatientCreate schema with missing required fields raises a ValidationError.
    """
    
    with pytest.raises(ValidationError):
        PatientCreate(age=30, email="john@example.com")

def test_patient_schema():
    """
    Tests that a full Patient schema can be created and that its fields can be accessed.
    """
    patient = Patient(
        id=1,
        name="John Doe",
        age=30,
        email="john@example.com",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        user_id = 1
    )
    assert patient.id == 1
    assert patient.email == "john@example.com"
    assert patient.user_id == 1

