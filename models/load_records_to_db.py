import json
import requests
from datetime import datetime
from faker import Faker
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

fake = Faker()

# API endpoint URLs
patient_details_url = "http://127.0.0.1:8000/api/v1/patient_details"
patient_symptoms_url = "http://127.0.0.1:8000/api/v1/patient_symptoms"

# Function to calculate Date of Birth
def calculate_dob(age):
    current_year = datetime.now().year
    dob_year = current_year - int(age)
    random_date = fake.date_of_birth(minimum_age=int(age), maximum_age=int(age))
    dob = random_date.replace(year=dob_year)
    return dob

# Load data from JSON
with open("records_with_med42.json") as file:
    data = json.load(file)

# Iterate over the records and send requests to the API
try:
    for record in data[:950]:
        patient_data = record["patientRecord"]
        diagnosis_report = record["diagnosisReport"]

        # Prepare data for patient details
        patient_details_data = {
            "FirstName": fake.first_name(),
            "LastName": fake.last_name(),
            "DateOfBirth": calculate_dob(patient_data["Age"]).isoformat(),
            "Gender": patient_data["Gender"],
            "Address": fake.address(),
            "ContactNumber": "9999999999",
            "Email": fake.email(),
            "Height": patient_data["Height"],
            "Weight": patient_data["Weight"],
            "BloodType": patient_data["Blood type"]
        }

        # Send POST request to create patient details
        response = requests.post(patient_details_url, json=patient_details_data)
        if response.status_code == 201:
            patient_id = response.json().get("PatientID")  # Assuming the response contains the PatientID
            print(f"Patient ID {patient_id} created successfully.")
        else:
            print(f"Error creating patient details: {response.text}")
            continue  # Skip to the next record if there is an error

        # Prepare data for patient symptoms
        symptom_data = {
            "PatientID": patient_id,
            "SymptomDescription": patient_data["Detailed symptoms"],
            "Severity": patient_data["Severity"],
            "Duration": patient_data["Duration of the symptoms"],
            "AssociatedConditions": ", ".join([
                patient_data["Existing medical conditions"],
                f"Allergies: {patient_data['Allergies']}",
                f"Current medications: {patient_data['Current medications']}"
            ]),
            "ModelInputDescription": f"""
            **Possible Diagnoses:**
            - **Primary Diagnosis**: {diagnosis_report['Possible Diagnoses']['Primary Diagnosis']}
            - **Differential Diagnoses**: 
              - {', '.join(diagnosis_report['Possible Diagnoses']['Differential Diagnoses'])}
            
            **Reasoning Process:**
            {diagnosis_report['Reasoning Process']}
            
            **Recommended Tests or Examinations:**
            {diagnosis_report['Recommended Tests or Examinations']}
            
            **Potential Treatment Options:**
            {diagnosis_report['Potential Treatment Options']}
            
            **Immediate Precautions or Recommendations:**
            {diagnosis_report['Immediate Precautions or Recommendations']}
            
            **Follow-up Plan:**
            {diagnosis_report['Follow-up Plan']}
            """,
            "SymptomEnteredDate": datetime.now().isoformat()
        }

        # Send POST request to create patient symptom
        symptom_response = requests.post(patient_symptoms_url, json=symptom_data)
        if symptom_response.status_code == 201:
            print(f"Symptom data for Patient ID {patient_id} added successfully.")
        else:
            print(f"Error creating patient symptom: {symptom_response.text}")

    print("Data processing complete.")

except Exception as e:
    print(f"An error occurred: {e}")
