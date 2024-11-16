# data_pipeline/dags/preprocess_dag.py

''' 
DAG for running data preprocessing
'''

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator 


default_args = {
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    'data_preprocessing_dag',
    default_args=default_args,
    description='DAG for running data preprocessing',
    schedule_interval=None,  # Set to None for manual triggering
    start_date=datetime(2024, 11, 2),
    catchup=False,
) as dag:
    
    preprocess_task = BashOperator(
        task_id='run_preprocess_script',
        bash_command='python /opt/airflow/src/preprocessing/preprocess_dataset.py'
    )
