import requests
from requests.auth import HTTPBasicAuth

# Set the URL of the Airflow webserver and the DAG ID
url = "http://34.123.143.96:8080/api/v1/dags/data_pipeline/dagRuns"
url1 = "http://34.123.143.96:8080/api/v1/dags/data_pipeline/dagRuns/manual__2024-12-05T23:30:44.799680+00:00/taskInstances/generate_prompt_task/logs/1"
# https://airflow.apache.org/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/logs/{task_try_number}
# Assume `patient_id` is the ID you want to pass to the DAG
patient_id = 135

# Create a payload with the `conf` key, which Airflow uses to pass parameters to the DAG
payload = {
    "conf": {
        "patient_id": patient_id
    }
}

# Make the POST request to trigger the DAG with Basic Auth
# response = requests.post(url, json=payload, auth=HTTPBasicAuth('admin', 'admin'))
response = requests.get(url1, json={}, auth=HTTPBasicAuth('admin', 'admin'))

# Print the response
if response.status_code == 200:
    print(f"DAG triggered successfully! {response.text}")
else:
    print(f"Failed to trigger DAG. Status code: {response.status_code}, Response: {response.text}")
