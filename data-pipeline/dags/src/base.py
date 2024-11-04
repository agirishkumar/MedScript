import requests
import json
from datetime import datetime

# TODO: Move to a config file!
BASE_API_URL = "http://fastapi:8000/"

def get_data(url: str) -> dict:
    """
    Helper function to get data from the specified url.
    
    Parameters:
        url (str): The URL of the API endpoint to get data from.
        
    Returns:
        dict: The JSON response data from the API.
    """
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("data:", data)
        return data
    else:
        raise

def get_summary(patient_id: int) -> dict:
    """
    Fetches summary for a patient with the given patient id and returns the data.

    Returns: The JSON data
    """
    url = BASE_API_URL + f"/api/v1/patient_summary/{patient_id}"
    return get_data(url)


def preprocess_data(data: dict) -> dict:
    print("Preprocess:", data)
    if not data: 
        raise
    
    processed_data = {}
    processed_data["User information"] = extract_patient_details(data["patient"])
    processed_data["Symptoms"] = extract_symptoms(data["visits"])
    print(processed_data)
    return processed_data


def calculate_age(date_of_birth: str):
    """
    Helper function to calculate age from the date of birth
    """
    birthdate = datetime.strptime(date_of_birth, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

def extract_patient_details(patient: dict) -> str:
    age = calculate_age(patient['DateOfBirth'])
    gender = patient['Gender']
    patient_details = f"""
            Age: {age}
            Gender: {gender}
            Medical History: No significant past medical issues
            Allergies: None known
            Current Medications: None
        """    
    return patient_details

def extract_symptoms(visits: dict) -> str:
    symptoms_list = []
    for visit in visits:
        visit_symptoms = visit["symptoms"][0]
        symptoms_list.append(visit_symptoms["SymptomDescription"])
    
    symptoms = "\n".join([f"- {symptom}" for symptom in symptoms_list])
    return symptoms




