# data_pipeline/dags/main.py

'''
This Airflow DAG fetches patient data, preprocesses it, queries a vector database, and generates a prompt for analysis.
'''

from airflow import DAG
from airflow.operators.python import PythonOperator
# from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
from base import *

# define the arguments for the DAG
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=1)
}

# Create the DAG
dag = DAG(
    dag_id='data_pipeline',
    default_args = default_args,
    description='A DAG to fetch data from api endpoints, preprocess and query the vector database to generate a prompt',
    start_date = datetime(2024, 11, 1, 2),
    catchup = False
)

# TASKS

# # TASK 0: Get latest patient ID
# get_latest_id_task = PythonOperator(
#     task_id='get_latest_id_task',
#     python_callable=get_latest_patient_id,
#     dag=dag
# )

# TASK 1: Fetch patient summary
load_data_task = PythonOperator(
    task_id="load_data_task",
    python_callable=get_summary,
    op_kwargs={
        'patient_id': 9
    },
    dag=dag
)

# TASK 2: Preprocess data
data_preprocessing_task = PythonOperator(
    task_id='data_preprocessing_task',
    python_callable=preprocess_data,
    op_args=[load_data_task.output],
    dag=dag
)

# TASK 3: Embeddings for similarity search
query_vector_database_task = PythonOperator(
    task_id='query_vectorDB_task',
    python_callable=query_vector_database,
    op_args=[data_preprocessing_task.output],
    dag=dag
)

# TASK 4: Generate prompt 
generate_prompt_task = PythonOperator(
    task_id='generate_prompt_task',
    python_callable=generate_prompt,
    op_args=[query_vector_database_task.output],
    dag=dag
)

# # Slack notification for failure
# slack_failure_notification = SlackWebhookOperator(
#     task_id='slack_notification_failed',
#     http_conn_id='slack_webhook',
#     message="""
#     :red_circle: Pipeline Failure Alert
#     *Patient Analysis Pipeline Failed*
#     • Patient ID: {{ task_instance.xcom_pull(task_ids='load_data_task') }}
#     • Failed Task: {{ task_instance.task_id }}
#     • Timestamp: {{ ts }}
    
#     Please check the <{{ task_instance.log_url }}|Airflow logs> for more information.
#     """,
#     trigger_rule=TriggerRule.ONE_FAILED,
#     dag=dag
# )

# # Slack notification for success
# slack_success_notification = SlackWebhookOperator(
#     task_id='slack_notification_success',
#     http_conn_id='slack_webhook',
#     message="""
#     :large_green_circle: Pipeline Success
#     *Patient Analysis Pipeline Completed Successfully*
#     • Patient ID: {{ task_instance.xcom_pull(task_ids='load_data_task') }}
#     • Completion Time: {{ ts }}
    
#     All tasks completed successfully!
#     """,
#     trigger_rule=TriggerRule.ALL_SUCCESS,
#     dag=dag
# )

load_data_task >> data_preprocessing_task >> query_vector_database_task >> generate_prompt_task
# generate_prompt_task >> [slack_success_notification, slack_failure_notification]
