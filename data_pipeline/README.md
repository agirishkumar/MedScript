# Data - pipeline

Airflow orchestrates the execution of tasks in the pipeline by managing the scheduling and dependencies between various tasks defined in the DAGs. 

To run the pipeline:

- Navigate to the data_pipeline directory from the root folder

    ```bash
    cd data_pipeline
    ```

- Create a secrets folder to store the service account key

    ```bash
    mkdir secrets
    ```

- Copy the JSON service account key file into the secrets folder and rename it to service-account-key.json

    ```bash
    cp path/to/your/service-account-key.json secrets/
    ```

- Ensure Docker is installed. To install, follow the instructions on [Docker website](https://docs.docker.com/engine/install/)

    ```bash
    docker --version
    docker-compose --version
    ```
- Use Docker Compose to start the data pipeline

    ```bash
    docker-compose --env-file ../.env up
    ```
The Airflow UI will run on port `8080`. It can be accessed at `http://localhost:8080`. 

- To stop the data pipeline, run the following command:

    ```bash
    docker-compose --env-file ../.env down
    ```

### Folder structure

- **config/**: Contains configuration files for the pipeline, such as `airflow.cfg`, which defines settings for Apache Airflow.
- **logs/**: Directory where logs for the Airflow tasks are stored.
- **dags/**: Contains Directed Acyclic Graphs (DAGs) that define the workflow of the data pipeline.
  - **src/**: Directory for source files used in the DAGs.
    - **base.py**: Contains base classes or functions used across various tasks.
  - **main.py**: Entry point for executing the data pipeline tasks.

    

