FROM apache/airflow:latest

WORKDIR ${AIRFLOW_HOME}
USER root

RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p ./dags
RUN chmod -R 777 ./dags 

COPY ../data_pipeline/dags/. ./dags/

COPY ../deployment/airflow-requirements.txt .

USER airflow
RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r airflow-requirements.txt