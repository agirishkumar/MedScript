'''
This Airflow DAG fetches patient data, preprocesses it, queries a vector database, and generates a prompt for analysis.
'''
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta
from base import *
import subprocess
import json

# define the arguments for the DAG
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=1)
}

# Create the DAG
dag = DAG(
    dag_id='data_pipeline',
    default_args=default_args,
    description='A DAG to fetch data from api endpoints, preprocess and query the vector database to generate a prompt',
    start_date=datetime(2024, 11, 1, 2),
    catchup=False
)

# Slack Webhook URL
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

def send_slack_notification(message):
    """Helper function to send slack notification using curl"""
    curl_command = [
        'curl',
        '-X', 'POST',
        '-H', 'Content-type: application/json',
        '--data', json.dumps({"text": message}),
        SLACK_WEBHOOK_URL
    ]
    try:
        subprocess.run(curl_command, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to send Slack notification: {e}")

def slack_failure_alert(context):
    """Callback function for task failure notification"""
    slack_msg = f"""
:red_circle: Task Failed.
*Task*: {context.get('task_instance').task_id}
*Dag*: {context.get('task_instance').dag_id}
*Execution Time*: {context.get('execution_date')}
*Log Url*: {context.get('task_instance').log_url}
"""
    send_slack_notification(slack_msg)

def slack_success_alert(context):
    """Callback function for successful DAG completion notification"""
    slack_msg = f"""
:white_check_mark: DAG Succeeded!
*DAG*: {context.get('dag').dag_id}
*Execution Time*: {context.get('execution_date')}
"""
    send_slack_notification(slack_msg)

# TASK 1: Fetch patient summary
load_data_task = PythonOperator(
    task_id="load_data_task",
    python_callable=get_summary,
    op_kwargs={
        'patient_id': 9
    },
    on_failure_callback=slack_failure_alert,
    dag=dag
)

# TASK 2: Preprocess data
data_preprocessing_task = PythonOperator(
    task_id='data_preprocessing_task',
    python_callable=preprocess_data,
    op_args=[load_data_task.output],
    on_failure_callback=slack_failure_alert,
    dag=dag
)

# TASK 3: Embeddings for similarity search
query_vector_database_task = PythonOperator(
    task_id='query_vectorDB_task',
    python_callable=query_vector_database,
    op_args=[data_preprocessing_task.output],
    on_failure_callback=slack_failure_alert,
    dag=dag
)

# TASK 4: Generate prompt
generate_prompt_task = PythonOperator(
    task_id='generate_prompt_task',
    python_callable=generate_prompt,
    op_args=[query_vector_database_task.output],
    on_failure_callback=slack_failure_alert,
    on_success_callback=slack_success_alert,  # Add success notification to final task
    dag=dag
)

# Set task dependencies
load_data_task >> data_preprocessing_task >> query_vector_database_task >> generate_prompt_task