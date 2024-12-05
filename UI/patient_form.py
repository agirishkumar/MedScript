import streamlit as st
import requests
from dotenv import load_dotenv
import os

from generate_patient_report_pdf import create_pdf

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load the environment file
load_dotenv()

# class Settings(BaseSettings):
#     API_BASE_URL: str

#     # class Config:
#     #     env_file = "MedScript/.env"
#     #     extra = "ignore"

# # Initialize settings
# settings = Settings()

# # Use the base URL in your code
# api_base_url = settings.API_BASE_URL

api_base_url = "http://34.170.255.245"

def send_patient_details(payload):
    api_url = f"{api_base_url}/api/v1/patient_details"
    try:
       
        response = requests.post(api_url, json=payload)
        st.write(f"Response Status Code: {response.status_code}")
        st.write(f"Response Text: {response.text}")
        if response.status_code == 200 or response.status_code == 201:
            return True, response.json().get('PatientID', 'Unknown ID')
        else:
            return False, f"Failed to submit patient details. Error: {response.text}"
    except Exception as e:
        return False, f"An error occurred: {str(e)}"


# Function to send symptoms to the API
def send_patient_symptoms(payload):
    api_url = f"{api_base_url}/api/v1/patient_symptoms"
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200 or response.status_code == 201:
            return True, "Symptoms submitted successfully!"
        else:
            return False, f"Failed to submit symptoms. Error: {response.text}"
    except Exception as e:
        return False, f"An error occurred: {str(e)}"

from generate_patient_report_pdf import create_pdf

st.title("Welcome to MedScript")

# Streamlit application

st.markdown("<h1 style='font-size: 29px;'>Patient Information Submission Form</h1>", unsafe_allow_html=True)

st.markdown("""
Please fill out the form below with your details. Fields marked with an asterisk (*) are required.
""")

# Streamlit form
with st.form(key='patient_form'):
    # Basic Information
    st.header("Basic Information")
    first_name = st.text_input("First Name*", max_chars=50)
    last_name = st.text_input("Last Name*", max_chars=50)
    dob = st.date_input("Date of Birth*", max_value=None)
    gender = st.selectbox("Gender*", ["Select", "Male", "Female"])
    contact_number = st.text_input("Contact Number*", max_chars=10)
    email = st.text_input("Email*", max_chars=100)
    address = st.text_area("Address*", max_chars=255)
    height = st.number_input("Height (cm)*", min_value=0.0, step=0.1, format="%.1f")
    weight = st.number_input("Weight (kg)*", min_value=0.0, step=0.1, format="%.1f")
    blood_type = st.selectbox("Blood Type", ["Select", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])


    # Medical Details
    st.header("Medical Details")
    symptoms = st.text_area("Detailed Symptoms*", placeholder="Describe your symptoms in detail...")
    severity = st.text_area("Severity of your case*", placeholder="Describe the severity of your case")
    existing_conditions = st.text_area("Existing Medical Conditions",
                                       placeholder="List any pre-existing medical conditions...")
    allergies = st.text_area("Allergies", placeholder="List any allergies...")
    current_medications = st.text_area("Current Medications", placeholder="List any current medications...")

    # Form Submission
    submitted = st.form_submit_button("Submit")

    # Confirmation on submission
    if submitted:
        if not (first_name and last_name and gender != "Select" and blood_type != "Select"):
            st.error("Please fill out all required fields correctly")
        else:
            patient_payload = {
                "FirstName": first_name,
                "LastName": last_name,
                "DateOfBirth": dob.isoformat(),
                "Gender": gender,
                "ContactNumber": contact_number,
                "Email": email,
                "Address": address,
                "Height": height,
                "Weight": weight,
                "BloodType": blood_type if blood_type != "Select" else None
            }

            # Send patient details first
            success, message = send_patient_details(patient_payload)
            if success:
                patient_id = message  # Extract PatientID from the response
                st.success(f"Patient details submitted successfully! Patient ID: {patient_id}")

                # Now, create the symptoms payload with associated conditions
                symptoms_payload = {
                    "PatientID": patient_id,
                    "SymptomDescription": symptoms,
                    "Severity": severity,
                    "AssociatedConditions": f"Existing Conditions: {existing_conditions}, Allergies: {allergies}, Medications: {current_medications}",
                }

                # Send patient symptoms
                success, message = send_patient_symptoms(symptoms_payload)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.error(message)

st.markdown("---")
st.header("Diagnostic Report")

# Display Primary Diagnosis
primary_diagnosis = "Primary Diagnosis: Example diagnosis text goes here."
st.text(primary_diagnosis)

# Button to view diagnostic report
if st.button("Download Diagnostic Report"):
    try:
        pdf = create_pdf()
        st.download_button(
            label="Download PDF",
            data=pdf,
            file_name="diagnostic_report.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        print(f"An error occured: {e}")
    # st.write("Diagnostic report is not yet available. Please contact your healthcare provider.")
    st.write("Diagnostic report is not yet available. Please contact your healthcare provider.")
