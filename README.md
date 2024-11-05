# MedScript
AI assitant for diagnosis

Group Members: 
[Aishwariya Suryamindra](https://github.com/aishwarya-suyamindra) ,[Girish Kumar Adari](https://github.com/agirishkumar), [Mallika Gaikwad](https://github.com/MallikaGaikwad), [Om Mali](https://github.com/maliom939) , [Pramatha Bhat](https://github.com/pramathabhat), [Rohan Reddy](https://github.com/tantalum-73)

### Setup Instructions
Please confirm that **Python >= 3.8** or a later version is present on your system prior to installation. This software is designed to be compatible with Windows, Linux, and macOS platforms.

### Step-by-Step Guide
Step 1: Clone the Repository on your Terminal
Clone the repository to the local machine and navigate into the project directory:

```bash
git repo clone agirishkumar/MedScript.git
cd MedScript
```
Step 2: Open the Project in Visual Studio Code
Open the project folder (MedScript) in Visual Studio Code.

**Step 3: Create and activate a virtual envionment 'MedEnv'**
```bash 
python3 -m venv MedEnv
```
To Activate the virtual environment
```bash
source MedEnv/bin/activate
```
**Step 4: Setup GCP on ubuntu terminal:**

- Add the Cloud SDK distribution URI as a package source
```bash
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
```

- Import the Google Cloud public key
```bash
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
```

- Update and install the Cloud SDK
```bash
sudo apt-get update && sudo apt-get install google-cloud-sdk
```

- initialize the SDK:
```bash
gcloud init
```

login with google account, select the project

- verify the configuration:
`gcloud config list`

**Step 5: Set up the .env file**
Save this file as .env in the repo

DB_USER=admin\
DB_PASS=admin\
DB_NAME=medscript\
DB_HOST=localhost\
DB_PORT=5434\
JWT_SECRET_KEY=myjwtsecretkey\
JWT_REFRESH_SECRET_KEY=myjwtrefreshsecretkey\
AIRFLOW_UID=123\
POSTGRES_USER=your_postgres_user\
POSTGRES_PASSWORD=your_postgres_password\
POSTGRES_DB=your_postgres_db\
AIRFLOW_WWW_USER_USERNAME=your_airflow_user\
AIRFLOW_WWW_USER_PASSWORD=your_airflow_user_password\
CLOUD_SQL_INSTANCE=your_cloud_sql_instance\
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json

**Step 6 : Run the requirements.txt file to install all the required libraries 
```bash
pip install -r requirements.txt
```

**Step 7 : To run and check the app**
`python3 -m uvicorn app.main:app --reload`

- check the urls `http://127.0.0.1:8000`, `http://127.0.0.1:8000/api/v1/health`

**Step 8: Set up Airflow

1. Initialize Airflow:
   ```bash
   docker compose up airflow-init
   ```
2. Start all containers:
   ```bash
   docker compose up
   ```
- Airflow orchestrates the execution of tasks in the pipeline by managing the scheduling and dependencies between various tasks defined in the DAGs. 

**To run the pipeline:**

- Navigate to the data-pipeline directory from the root folder

    ```bash
    cd data-pipeline
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
 
## Project Overview

This healthcare application project aims to enhance patient-doctor interactions by integrating AI into the medical workflow. Key features include:

The key factors for this healthcare application project are:

1. **Comprehensive Data Collection**: Ensuring standardized and detailed patient data is captured for accurate analysis and continuity in care.

2. **AI-Powered Disease Detection**: Utilizing advanced machine learning models to analyze patient data and identify potential diseases, increasing diagnostic speed and precision.

3. **Automated Prescription Generation**: Creating initial prescription suggestions based on AI-detected health conditions, which supports quicker treatment planning.

4. **Doctor Review and Oversight**: Providing doctors with a user-friendly interface to review, adjust, or override AI-generated prescriptions, maintaining medical expertise in the decision-making process.

5. **Enhanced Workflow Efficiency**: Streamlining the healthcare process by integrating AI tools, reducing time spent on data entry and initial diagnosis, allowing doctors to focus more on patient care.

6. **Educational Value for Medical Professionals**: Serving as a learning tool for doctors, as they can observe and evaluate AI-driven recommendations and adapt as needed.

These factors collectively improve patient outcomes, make healthcare workflows more efficient, and offer an educational advantage for medical professionals.


## Data Information

1. For a General Diagnostic Model:
   
**Model: Med42
Data Card:**
- Type: Large Language Model
- Base: Llama-2\
- Size: 70B parameters\
- Specialization: Medical knowledge and reasoning\
- Performance: 72% accuracy on USMLE sample exams\
- License: Custom open-access license (requires acceptance)\
- URL: https://huggingface.co/m42-health/med42-70b

**Dataset: MIMIC-III Clinical Database
Data Card:**
- Type: Clinical Database\
- Size: >40,000 patient stays\
- Format: CSV files\
- Data types: Structured clinical data (demographics, vital signs, lab tests, medications,
etc.)\
License: PhysioNet Credentialed Health Data License 1.5.0\
URL: https://physionet.org/content/mimiciii/1.4/

Data Rights and Privacy: De-identified data, requires completion of training course for access

2. X-ray Diagosis Model:
   
**Model: CheXNet (open-source implementation)]
Data Card:**
- Type: Convolutional Neural Network\
- Base: DenseNet-121\
- Specialization: Chest X-ray analysis\
- Performance: Exceeds radiologist performance on pneumonia detection\
- License: MIT License\
- URL: https://github.com/zoogzog/chexnet



## Modules and Their Roles:

__main.py:__
 - The entry point of the application.
- Sets up the FastAPI instance, adds middleware, and includes routers for endpoints.
- Initializes the database and starts the server using Uvicorn.

__config.py:__
- Holds the configuration settings for the app, such as project metadata and database credentials.
- Reads from an environment file (.env), which is useful for securely managing sensitive information like database connection strings.

__patients.py (API Endpoints):__
- Defines the endpoints for interacting with patient records.
- Contains endpoints like:
    - POST /api/v1/patients/: Create a new patient.
    - GET /api/v1/patients/: Get a list of patients.
    - GET /api/v1/patients/{patient_id}: Get a specific patient by ID.

__models/patient.py:__
- Defines the SQLAlchemy model for the Patient table, including columns 
- for id, name, age, email, and timestamps.~

__schemas/patient.py:__
- Provides Pydantic schemas for data validation and serialization when working with patient data.
- Contains models for PatientBase, PatientCreate, PatientUpdate, and Patient.

__crud/patient.py:__
- Contains the CRUD operations for interacting with the database using SQLAlchemy’s ORM. This includes functions like:
    - get_patient(): Retrieve a patient by ID.
    - get_patients(): Retrieve multiple patients with pagination support.
    - create_patient(): Add a new patient to the database.
    - update_patient(): Update an existing patient’s data.
    - delete_patient(): Remove a patient from the database.

**Database Connection (session.py):**
- Establishes a connection to the PostgreSQL database using SQLAlchemy’s create_engine.
- Provides a SessionLocal class to manage database sessions.

__Logging (logging.py):__
- Sets up a logger that logs application activities to both the console and a file.
- Uses a rotating file handler to manage logs and avoid excessive log size.

__Middleware (middleware.py):__
- RequestIDMiddleware: Adds a unique request ID to each incoming request for traceability.
- LoggingMiddleware: Logs request details such as method, path, status code, and processing time.

## Git Workflow and Branching Strategy for the Project
__main Branch:__
- This branch is your production-ready branch.
- Only stable, tested, and production-ready code should be present here.
- Merges to main should only happen from dev after thorough testing and code review.

__dev Branch:__
- This branch is used for active development.
- All features, bug fixes, and enhancements are merged into dev.
- Once a feature or fix is complete, it’s merged back into dev via a pull request.

__Feature Branches:__
- Feature branches are created from the dev branch for any new feature, bug fix, or task.
- Naming convention: feature/\<task-name>, bugfix/\<task-name>, enhancement/\<task-name>.
__Examples:__
    feature/user-authentication
    bugfix/patient-age-validation
    enhancement/api-logging
Once the feature or fix is complete, a pull request is created to merge the feature branch into dev.

- To run the application:
`python3 -m uvicorn app.main:app --reload`

- To run the unit tests:
`pytest tests/unit/ --cov=app`

[Refer to the Notes](./Notes.md) file for details
