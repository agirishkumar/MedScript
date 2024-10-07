## Steps for setting up GCP on ubuntu terminal:

- Add the Cloud SDK distribution URI as a package source
`echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list`

- Import the Google Cloud public key
`curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -`

- Update and install the Cloud SDK
`sudo apt-get update && sudo apt-get install google-cloud-sdk`

- initialize the SDK:
`gcloud init`

login with google account, select the project

- verify the configuration:
`gcloud config list`


## clone repo from github:
- `gh repo clone agirishkumar/MedScript`
- create and activate virtual envionment 'MedEnv'.
`python3 -m venv MedEnv`
`source MedEnv/bin/activate`

## install fastapi, uvicorn, sqlalchemy

`pip3 install 'fastapi[standard]' 'uvicorn[standard]' sqlalchemy`

## To run and check the app
`python3 -m uvicorn app.main:app --reload`

- check the urls `http://127.0.0.1:8000`, `http://127.0.0.1:8000/api/v1/health`,

## Install and start the Cloud SQL Proxy in terminal
- `wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy`
- `chmod +x cloud_sql_proxy`
- `./cloud_sql_proxy -instances=medscript-437117:us-east4:medscript-db-1=tcp:5432` # change the port number if 5432 is already in use (5433).

## Connect to the database and use psql: 
`psql -h localhost -p 5433 -U <username> -d medscript` and enter the password.

## To run the application:
`python3 -m uvicorn app.main:app --reload`


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

