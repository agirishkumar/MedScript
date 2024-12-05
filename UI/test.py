import requests
from requests.auth import HTTPBasicAuth

# Set the URL of the Airflow webserver and the DAG ID
url = "http://34.123.143.96:8080/api/v1/dags/data_pipeline/dagRuns"

# Assume `patient_id` is the ID you want to pass to the DAG
patient_id = 135

# Create a payload with the `conf` key, which Airflow uses to pass parameters to the DAG
payload = {
    "conf": {
        "patient_id": patient_id
    }
}

# Make the POST request to trigger the DAG with Basic Auth
response = requests.post(url, json=payload, auth=HTTPBasicAuth('admin', 'admin'))

# Print the response
if response.status_code == 200:
    print("DAG triggered successfully!")
else:
    print(f"Failed to trigger DAG. Status code: {response.status_code}, Response: {response.text}")
