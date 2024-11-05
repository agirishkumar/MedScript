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

DB_USER=admin
DB_PASS=admin
DB_NAME=medscript
DB_HOST=localhost
DB_PORT=5434
JWT_SECRET_KEY=myjwtsecretkey
JWT_REFRESH_SECRET_KEY=myjwtrefreshsecretkey
AIRFLOW_UID=123
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_postgres_db
AIRFLOW_WWW_USER_USERNAME=your_airflow_user
AIRFLOW_WWW_USER_PASSWORD=your_airflow_user_password
CLOUD_SQL_INSTANCE=your_cloud_sql_instance
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
