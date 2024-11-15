import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.crud.patient_details import create_patient_details
from app.db.crud.patient_symptoms import create_patient_symptom
from app.db.schemas.patient_details import PatientDetailsCreate
from app.db.schemas.patient_symptoms import PatientSymptomCreate
from app.db.base import engine
from faker import Faker
import re

fake = Faker()
session = Session(bind=engine)

with open("models/records.json") as file:
    data = json.load(file)

def calculate_dob(age):
    current_year = datetime.now().year
    dob_year = current_year - int(age)
    random_date = fake.date_of_birth(minimum_age=int(age), maximum_age=int(age))
    dob = random_date.replace(year=dob_year)
    return dob

try:
    for record in data[846:]:
        patient_data = record["patientRecord"]

        patient_details_data = PatientDetailsCreate(
            FirstName=fake.first_name(),
            LastName=fake.last_name(),
            DateOfBirth=calculate_dob(patient_data["Age"]),
            Gender=patient_data["Gender"],
            Address=fake.address(),
            ContactNumber="9999999999",
            Email=fake.email(),
            Height=patient_data["Height"],
            Weight=patient_data["Weight"],
            BloodType=patient_data["Blood type"]
        )

        # Create patient details and retrieve PatientID
        patient = create_patient_details(session, patient_details_data)
        patient_id = patient.PatientID

        # Prepare data for PatientSymptomCreate schema
        symptom_data = PatientSymptomCreate(
            PatientID=patient_id,
            SymptomDescription=patient_data["Detailed symptoms"],
            ModelInputDescription=None,
            Severity=patient_data["Severity"],
            Duration=patient_data["Duration of the symptoms"],
            AssociatedConditions=", ".join([
                patient_data["Existing medical conditions"],
                f"Allergies: {patient_data['Allergies']}",
                f"Current medications: {patient_data['Current medications']}"
            ]),
            SymptomEnteredDate=datetime.now()
        )

        # Create patient symptom entry
        create_patient_symptom(session, symptom_data)
        print(f"Patient ID {patient_id} added to the database.")

    session.commit()
    print("Data successfully added to the database.")

except Exception as e:
    session.rollback()
    print(f"An error occurred: {e}")
finally:
    session.close()