import streamlit as st
import requests
from generate_patient_report_pdf import create_pdf
from requests.auth import HTTPBasicAuth
import time
import datetime

base_api_url = "http://34.170.255.245"
airflow_base_url = "http://34.123.143.96:8080/api/v1"
dag_id = "data_pipeline"
today = datetime.date.today()

def send_patient_details(payload):
    api_url = f"{base_api_url}/api/v1/patient_details"
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200 or response.status_code == 201:
            return True, response.json().get('PatientID', 'Unknown ID')
        else:
            return False, f"Failed to submit patient details. Error: {response.text}"
    except Exception as e:
        return False, f"An error occurred: {str(e)}"


def send_patient_symptoms(payload):
    api_url = f"{base_api_url}/api/v1/patient_symptoms"
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200 or response.status_code == 201:
            return True
        else:
            return False
    except Exception as e:
        return False


def trigger_airflow_dag(patient_id):
    payload = {
        "conf": {
            "patient_id": patient_id
        }
    }

    # Trigger the DAG
    response = requests.post(f"{airflow_base_url}/dags/{dag_id}/dagRuns", json=payload,
                             auth=HTTPBasicAuth('admin', 'admin'))

    if response.status_code == 200:
        dag_run_id = response.json()['dag_run_id']
        st.success(f"Generating report...")

        # Poll the DAG run status
        while True:
            run_status_response = requests.get(
                f"{airflow_base_url}/dags/{dag_id}/dagRuns/{dag_run_id}",
                auth=HTTPBasicAuth('admin', 'admin')
            )
            run_status = run_status_response.json()['state']
            last_task_id = "generate_model_response_task"
            if run_status == 'success':
                st.success(f"Generating report successfully")
                break
            elif run_status == 'failed':
                st.error(f"DAG run failed for Patient ID: {patient_id}")
                break
            else:
                time.sleep(10)

        # Fetch the logs of the last task
        task_log_response = requests.get(
            f"{airflow_base_url}/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{last_task_id}/logs/1",
            auth=HTTPBasicAuth('admin', 'admin')
        )

        if task_log_response.status_code == 200:
            task_log = task_log_response.text
            start_index = task_log.find("Returned value was:")
            if start_index != -1:
                task_log = task_log[start_index + len("Returned value was:"):]
            task_log = "\n".join(task_log.splitlines()[:-1])
            return task_log
        else:
            return f"Failed to fetch last task logs. Status code: {task_log_response.status_code}"

    else:
        return f"Failed to trigger DAG. Status code: {response.status_code}, Response: {response.text}"


def render():
    st.title("Welcome to MedScript")

    st.markdown("<h1 style='font-size: 29px;'>Patient Information Submission Form</h1>", unsafe_allow_html=True)

    st.markdown("""
    Please fill out the form below with your details. Fields marked with an asterisk (*) are required.
    """)

    with st.form(key='patient_form'):
        st.header("Basic Information")
        first_name = st.text_input("First Name*", max_chars=50)
        last_name = st.text_input("Last Name*", max_chars=50)
        dob = st.date_input("Date of Birth*", min_value=datetime.date(1900, 1, 1), max_value=today)
        gender = st.selectbox("Gender*", ["Select", "Male", "Female"])
        contact_number = st.text_input("Contact Number*", max_chars=10)
        email = st.text_input("Email*", max_chars=100)
        address = st.text_area("Address*", max_chars=255)
        height = st.number_input("Height (cm)*", min_value=0.0, step=0.1, format="%.1f")
        weight = st.number_input("Weight (kg)*", min_value=0.0, step=0.1, format="%.1f")
        blood_type = st.selectbox("Blood Type", ["Select", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

        st.header("Medical Details")
        symptoms = st.text_area("Detailed Symptoms*", placeholder="Describe your symptoms in detail...")
        severity = st.text_area("Severity of your case*", placeholder="Describe the severity of your case")
        existing_conditions = st.text_area("Existing Medical Conditions",
                                           placeholder="List any pre-existing medical conditions...")
        allergies = st.text_area("Allergies", placeholder="List any allergies...")
        current_medications = st.text_area("Current Medications", placeholder="List any current medications...")

        submitted = st.form_submit_button("Submit")

    if submitted:
        if not (
                first_name and last_name and gender != "Select" and blood_type != "Select" and dob and contact_number and address and height and weight and symptoms and severity):
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

            success, message = send_patient_details(patient_payload)
            if success:
                patient_id = message
                st.success(f"Patient details submitted successfully! Patient ID: {patient_id}")

                symptoms_payload = {
                    "PatientID": patient_id,
                    "SymptomDescription": symptoms,
                    "Severity": severity,
                    "AssociatedConditions": f"Existing Conditions: {existing_conditions}, Allergies: {allergies}, Medications: {current_medications}",
                }

                success = send_patient_symptoms(symptoms_payload)
                if success:
                    task_log = trigger_airflow_dag(patient_id)

                    st.markdown("---")
                    st.header("Diagnostic Report")
                    st.markdown(task_log, height=1000, disabled=True)
                else:
                    st.error(message)
            else:
                st.error(message)

    st.markdown("---")
    st.header("Download Diagnostic Report")

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
            st.error(f"An error occurred: {e}")
            st.write("Diagnostic report is not yet available. Please contact your healthcare provider.")


render()
