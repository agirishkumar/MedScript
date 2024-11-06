from datetime import date
from unittest.mock import Mock, patch
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.db.crud.patient_visits import create_patient_visit
from app.db.schemas.patient_visits import PatientVisitCreate
from app.db.schemas.patient_visits import PatientVisitCreate, PatientVisitUpdate
from app.db.models.patient_visits import PatientVisit
from app.db.crud.patient_visits import (
    get_patient_visit,
    get_patient_visits_by_patient_id,
    get_patient_visits_by_symptom_id,
    get_all_patient_visits,
    create_patient_visit,
    update_patient_visit,
    delete_patient_visit,
)


# Mock database session
@pytest.fixture
def mock_db_session():
    return Mock(spec=Session)

def test_get_patient_visit(mock_db_session):
    # Arrange
    visit_id = 1
    mock_visit = PatientVisit(VisitID=visit_id, PatientID=1, DoctorID=2, SymptomID=3, VisitDate=date.today())
    mock_db_session.query().filter().first.return_value = mock_visit

    # Act
    result = get_patient_visit(mock_db_session, visit_id)

    # Assert
    assert result == mock_visit
    mock_db_session.query().filter().first.assert_called_once()

def test_get_patient_visits_by_patient_id(mock_db_session):
    # Arrange
    patient_id = 1
    mock_visits = [
        PatientVisit(PatientID=patient_id, DoctorID=2, SymptomID=3, VisitDate=date.today()),
        PatientVisit(PatientID=patient_id, DoctorID=2, SymptomID=4, VisitDate=date.today()),
    ]
    mock_db_session.query().filter().all.return_value = mock_visits

    # Act
    result = get_patient_visits_by_patient_id(mock_db_session, patient_id)

    # Assert
    assert result == mock_visits
    mock_db_session.query().filter().all.assert_called_once()

def test_get_patient_visits_by_symptom_id(mock_db_session):
    # Arrange
    symptom_id = 3
    mock_visits = [
        PatientVisit(PatientID=1, DoctorID=2, SymptomID=symptom_id, VisitDate=date.today()),
        PatientVisit(PatientID=2, DoctorID=2, SymptomID=symptom_id, VisitDate=date.today()),
    ]
    mock_db_session.query().filter().all.return_value = mock_visits

    # Act
    result = get_patient_visits_by_symptom_id(mock_db_session, symptom_id)

    # Assert
    assert result == mock_visits
    mock_db_session.query().filter().all.assert_called_once()

def test_get_all_patient_visits(mock_db_session):
    # Arrange
    mock_visits = [
        PatientVisit(PatientID=1, DoctorID=2, SymptomID=3, VisitDate=date.today()),
        PatientVisit(PatientID=2, DoctorID=2, SymptomID=3, VisitDate=date.today()),
    ]
    mock_db_session.query().offset().limit().all.return_value = mock_visits

    # Act
    result = get_all_patient_visits(mock_db_session)

    # Assert
    assert result == mock_visits
    mock_db_session.query().offset().limit().all.assert_called_once()

def test_create_patient_visit(mock_db_session):
    # Arrange
    patient_visit_data = PatientVisitCreate(
        PatientID=1,
        DoctorID=2,
        SymptomID=3,
        VisitDate=date.today(),
        DoctorsReportPdfLink="link_to_report",
        PatientFriendlyReportPdfLink="link_to_patient_report",
        Notes="Visit notes"
    )
    mock_visit = PatientVisit(**patient_visit_data.dict())
    mock_db_session.add = Mock()
    mock_db_session.commit = Mock()
    mock_db_session.refresh = Mock()

    # Act
    result = create_patient_visit(mock_db_session, patient_visit_data)

    # Assert
    assert result.PatientID == patient_visit_data.PatientID
    assert result.DoctorID == patient_visit_data.DoctorID
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

def test_update_patient_visit(mock_db_session):
    # Arrange
    visit_id = 1
    updated_data = PatientVisitUpdate(DoctorsReportPdfLink="new_link", Notes="Updated notes")
    existing_visit = PatientVisit(VisitID=visit_id, PatientID=1, DoctorID=2, SymptomID=3, VisitDate=date.today())
    mock_db_session.query().filter().first.return_value = existing_visit

    # Act
    updated_visit = update_patient_visit(mock_db_session, visit_id, updated_data)

    # Assert
    assert updated_visit.DoctorsReportPdfLink == "new_link"
    assert updated_visit.Notes == "Updated notes"
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

def test_delete_patient_visit(mock_db_session):
    # Arrange
    visit_id = 1
    mock_visit = PatientVisit(VisitID=visit_id, PatientID=1, DoctorID=2, SymptomID=3, VisitDate=date.today())
    mock_db_session.query().filter().first.return_value = mock_visit

    # Act
    deleted_visit = delete_patient_visit(mock_db_session, visit_id)

    # Assert
    assert deleted_visit == mock_visit
    mock_db_session.delete.assert_called_once_with(mock_visit)
    mock_db_session.commit.assert_called_once()



def test_create_patient_visit_integrity_error(mock_db_session):
    # Arrange
    patient_visit_data = PatientVisitCreate(
        PatientID=1,
        DoctorID=2,
        SymptomID=3,
        VisitDate=date.today(),
        DoctorsReportPdfLink="link_to_report",
        PatientFriendlyReportPdfLink="link_to_patient_report",
        Notes="Visit notes"
    )

    # Mock `db.add()` to raise an IntegrityError
    mock_db_session.add.side_effect = IntegrityError("Mock integrity error", None, None)
    
    # Act and Assert
    with pytest.raises(HTTPException) as exc_info:
        create_patient_visit(mock_db_session, patient_visit_data)
        
    # Check that the rollback was called and the exception message is as expected
    mock_db_session.rollback.assert_called_once()
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Error occurred while creating the patient visit."


def test_update_patient_visit_not_found(mock_db_session):
    # Arrange
    visit_id = 1
    updated_data = PatientVisitUpdate(DoctorsReportPdfLink="new_link", Notes="Updated notes")
    mock_db_session.query().filter().first.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        update_patient_visit(mock_db_session, visit_id, updated_data)

    # Check exception details
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Patient visit not found"

def test_get_patient_visit_not_found(mock_db_session):
    # Arrange
    visit_id = 1
    mock_db_session.query().filter().first.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_patient_visit(mock_db_session, visit_id)

    # Check exception details
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Patient visit not found"

def test_delete_patient_visit_not_found(mock_db_session):
    # Arrange
    visit_id = 1
    mock_db_session.query().filter().first.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        delete_patient_visit(mock_db_session, visit_id)

    # Check exception details
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Patient visit not found"


def test_update_patient_visit_not_found(mock_db_session):
    # Arrange
    visit_id = 1
    updated_data = PatientVisitUpdate(DoctorsReportPdfLink="new_link", Notes="Updated notes")
    mock_db_session.query().filter().first.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        update_patient_visit(mock_db_session, visit_id, updated_data)

    # Check exception details
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Patient visit not found"


def test_update_patient_visit_integrity_error(mock_db_session):
    # Arrange
    visit_id = 1
    updated_data = PatientVisitUpdate(DoctorsReportPdfLink="new_link", Notes="Updated notes")
    existing_visit = PatientVisit(VisitID=visit_id, PatientID=1, DoctorID=2, SymptomID=3, VisitDate=date.today())
    mock_db_session.query().filter().first.return_value = existing_visit
    mock_db_session.commit.side_effect = IntegrityError("Mock integrity error", None, None)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        update_patient_visit(mock_db_session, visit_id, updated_data)

    # Check rollback and exception message
    mock_db_session.rollback.assert_called_once()
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Error updating patient visit"


def test_update_patient_visit_unexpected_error(mock_db_session):
    visit_id = 1
    updated_data = PatientVisitUpdate(DoctorsReportPdfLink="new_link", Notes="Updated notes")
    existing_visit = PatientVisit(VisitID=visit_id, PatientID=1, DoctorID=2, SymptomID=3, VisitDate=date.today())
    
    # Mock that the patient visit exists
    mock_db_session.query().filter().first.return_value = existing_visit
    
    # Trigger a generic Exception on commit
    mock_db_session.commit.side_effect = Exception("Unexpected error during commit")
    
    # Call the update function and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        update_patient_visit(mock_db_session, visit_id, updated_data)
    
    # Verify that the exception detail matches the generic error message
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "An error occurred during the update."