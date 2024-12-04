# app/api/endpoints/get_latest_patientid.py

'''
This file contains the endpoint for retrieving the latest patient ID
'''

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.crud import patient_details
from app.api.deps import get_db

router = APIRouter(prefix="/latest_patient", tags=["patient"])

@router.get("/id", response_model=int)
def get_latest_patient_id(db: Session = Depends(get_db)):
    """
    Retrieve the most recent patient ID from the database.
    
    Returns:
        int: The ID of the most recently added patient
    
    Raises:
        HTTPException: If no patients are found in the database
    """
    latest_id = patient_details.get_latest_patient_id(db)
    if latest_id is None:
        raise HTTPException(
            status_code=404,
            detail="No patients found in the database"
        )
    return latest_id