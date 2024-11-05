FROM apache/airflow:2.10.2

WORKDIR /opt/airflow

# Install dependencies

COPY ../requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt