# data_pipeline/dags/main.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
from src.base import *
import subprocess

# define the arguments for the DAG
default_args = {
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

# Create the DAG
dag = DAG(
    dag_id='data_pipeline',
    default_args = default_args,
    description='A DAG to fetch data from api endpoints, preprocess and query the vector database to generate a prompt',
    start_date = datetime(2024, 11, 1, 2),
)

# TASKS

# TASK 1: Fetch patient summary

load_data_task = PythonOperator(

    task_id="load_data_task",

    python_callable=get_summary,

    op_kwargs={'patient_id': 9},

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

# TASK 3: Query the vector database
# write output to file?


# TASK 4: Generate prompt 
# generate_prompt_task = PythonOperator(

# )


# # Task to trigger displaying the generated prompt
# TriggerDagRunOperator = TriggerDagRunOperator(
#     task_id='my_trigger_task',
#     trigger_rule=TriggerRule.ALL_DONE,
#     trigger_dag_id='display_prompt',
#     dag=dag
# )



load_data_task >> data_preprocessing_task >> query_vector_database_task