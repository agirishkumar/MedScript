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
from airflow.providers.google.cloud.sensors.pubsub import PubSubPullSensor
from airflow.providers.google.cloud.operators.pubsub import PubSubCreateSubscriptionOperator
import os


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

SLACK_WEBHOOK_DAG_URL = os.environ.get("SLACK_WEBHOOK_DAG_URL")

def send_slack_notification(message):
    """Helper function to send slack notification using curl"""
    curl_command = [
        'curl',
        '-X', 'POST',
        '-H', 'Content-type: application/json',
        '--data', json.dumps({"text": message}),
        SLACK_WEBHOOK_DAG_URL
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


# TASK 3: Fetch patient summary (using the patient_id from DAG run config)
load_data_task = PythonOperator(
    task_id="load_data_task",
    python_callable=get_summary,
    op_kwargs={'patient_id': "{{ dag_run.conf['patient_id'] }}"},
    provide_context=True,
    on_failure_callback=slack_failure_alert,
    dag=dag,
)

# TASK 4: Preprocess data
data_preprocessing_task = PythonOperator(
    task_id='data_preprocessing_task',
    python_callable=preprocess_data,
    op_args=[load_data_task.output],
    on_failure_callback=slack_failure_alert,
    dag=dag
)

# TASK 5: Embeddings for similarity search
query_vector_database_task = PythonOperator(
    task_id='query_vectorDB_task',
    python_callable=query_vector_database,
    op_args=[data_preprocessing_task.output],
    on_failure_callback=slack_failure_alert,
    dag=dag
)

# TASK 6: Generate prompt
generate_prompt_task = PythonOperator(
    task_id='generate_prompt_task',
    python_callable=generate_prompt,
    op_args=[query_vector_database_task.output],
    on_failure_callback=slack_failure_alert,
    dag=dag
)

# TASK 7: Generate Model Response
generate_model_response_task = PythonOperator(
    task_id='generate_model_response_task',
    python_callable=generate_model_response,
    op_args=[generate_prompt_task.output],
    on_failure_callback=slack_failure_alert,
    on_success_callback=slack_success_alert,  
    dag=dag
)

# the task dependencies
load_data_task >> data_preprocessing_task >> query_vector_database_task >> generate_prompt_task >> generate_model_response_task
