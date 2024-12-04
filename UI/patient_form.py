import streamlit as st
import requests

# Function to send data to the API
def send_data_to_api(payload):
    api_url = "http://35.188.123.19/docs"
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
            return True, "Data submitted successfully!"
        else:
            return False, f"Failed to submit data. Error: {response.text}"
    except Exception as e:
        return False, f"An error occurred: {str(e)}"

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
    gender = st.selectbox("Gender*", ["Select", "Male", "Female"])
    age = st.number_input("Age*", min_value=0, max_value=120, step=1)
    height = st.number_input("Height (cm)*", min_value=0.0, step=0.1, format="%.1f")
    weight = st.number_input("Weight (kg)*", min_value=0.0, step=0.1, format="%.1f")
    blood_type = st.selectbox("Blood Type*", ["Select", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

    # Medical Details
    st.header("Medical Details")
    symptoms = st.text_area("Detailed Symptoms*", placeholder="Describe your symptoms in detail...")
    severity = st.text_area("Severity of your case*", placeholder="Describe the severity of your case")
    existing_conditions = st.text_area("Existing Medical Conditions", placeholder="List any pre-existing medical conditions...")
    allergies = st.text_area("Allergies", placeholder="List any allergies...")
    current_medications = st.text_area("Current Medications", placeholder="List any current medications...")

    # Previous Visits
    previous_visits = st.number_input("Number of Previous Visits*", min_value=0, step=1)

    # Form Submission
    submitted = st.form_submit_button("Submit")
    
    # Confirmation on submission
    if submitted:
        if gender == "Select" or blood_type == "Select":
            st.error("Please fill out all required fields correctly.")
        else:
            payload = {
                "Gender": gender,
                "Age": age,
                "Height (cm)": height,
                "Weight (kg)": weight,
                "Blood Type": blood_type if blood_type != "Select" else "Not provided",
                "Symptoms": symptoms,
                "Severity": severity,
                "Existing Medical Conditions": existing_conditions,
                "Allergies": allergies,
                "Current Medications": current_medications,
                "Number of Previous Visits": previous_visits,
            }

            success, message = send_data_to_api(payload)
            if success:
                st.success(message)
            else:
                st.error(message)

st.markdown("---")
st.header("Diagnostic Report")


# Display Primary Diagnosis
primary_diagnosis = "Primary Diagnosis: Example diagnosis text goes here."
st.text(primary_diagnosis)


# Button to view diagnostic report
if st.button("Download Diagnostic Report"):
    st.write("Diagnostic report is not yet available. Please contact your healthcare provider.")