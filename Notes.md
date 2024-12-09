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

(MedEnv) asuran@asuran:~/Downloads/projects/MedScript$ ./deploy.sh
Welcome to the GKE Deployment Script
Please provide the following information (press Enter to use default values):
----------------------------------------
Enter your Google Cloud Project ID [medscript-437117]: medscript-437117
Enter the cluster name [project-cluster-1]: project-cluster-2
Enter the zone [us-central1-a]: us-central1-a
Enter the namespace [medscript]: medscript
Enter the machine type [e2-standard-2]: e2-standard-2
Enter minimum number of nodes [0]: 0
Enter maximum number of nodes [3]: 3
Enter the service account email [github-actions-sa@medscript-437117.iam.gserviceaccount.com]: github-actions-sa@medscript-437117.iam.gserviceaccount.com

Select components to deploy:
1) Backend API
2) Data Pipeline
3) Both
Enter choice [1]: 3
Enter the image tag [latest]: V1

Configuration Summary:
----------------------------------------
Project ID: medscript-437117
Cluster Name: project-cluster-2
Zone: us-central1-a
Namespace: medscript
Machine Type: e2-standard-2
Node Range: 0 to 3
Service Account: github-actions-sa@medscript-437117.iam.gserviceaccount.com
Components to deploy: gke-backend airflow-webserver
Image Tag: V1
----------------------------------------
Do you want to proceed? (y/n): y

Step: 1. Authenticating with Google Cloud
----------------------------------------
Your browser has been opened to visit:

    https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=32555940559.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A8085%2F&scope=openid+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fappengine.admin+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fsqlservice.login+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcompute+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Faccounts.reauth&state=33PYQ4oVCJSzrFHe32U05qGXsbaebS&access_type=offline&code_challenge=uCa7d2PJZlvRXbF5pF9GK3ljdHIwv9zryNz9vvT6NF8&code_challenge_method=S256


You are now logged in as [adari.girishkumar@gmail.com].
Your current project is [medscript-437117].  You can change this setting by running:
  $ gcloud config set project PROJECT_ID
Updated property [core/project].
✓ Success

Step: 2. Configuring Docker authentication
----------------------------------------
WARNING: Your config file at [/home/asuran/.docker/config.json] contains these credential helper entries:

{
  "credHelpers": {
    "gcr.io": "gcloud",
    "us.gcr.io": "gcloud",
    "eu.gcr.io": "gcloud",
    "asia.gcr.io": "gcloud",
    "staging-k8s.gcr.io": "gcloud",
    "marketplace.gcr.io": "gcloud"
  }
}
Adding credentials for all GCR repositories.
WARNING: A long list of credential helpers may cause delays running 'docker build'. We recommend passing the registry name to configure only the registry you are using.
gcloud credential helpers already registered correctly.
✓ Success
Cluster project-cluster-2 already exists in zone us-central1-a. Skipping cluster creation.

Step: 4. Getting cluster credentials
----------------------------------------
Fetching cluster endpoint and auth data.
kubeconfig entry generated for project-cluster-2.
✓ Success

Step: 5. Creating namespace
----------------------------------------
✓ Success

Step: 6. Creating Kubernetes secrets
----------------------------------------

Step: Creating Kubernetes Secrets
----------------------------------------
Creating FastAPI secrets...
secret/gke-fastapi-secrets configured
✓ Success
Creating Airflow secrets...
secret/gke-airflow-secrets configured
✓ Success
✓ Kubernetes secrets created successfully

Step: Deploying Backend API first
----------------------------------------

Deploying gke-backend...
----------------------------------------
Image gcr.io/medscript-437117/gke-backend:V1 already exists. Skipping build steps.
Updating image in deployment/backend/app-deployment.yaml
deployment.apps/gke-backend unchanged
✓ Success
Updating image in deployment/backend/app-service.yaml
service/backend-service unchanged
✓ Success

Step: Waiting for deployment to be ready...
----------------------------------------
deployment "gke-backend" successfully rolled out
✓ Success

Step: Verifying pod status for app: gke-fast-api-app
----------------------------------------
Debug: PODS_READY=1, PODS_TOTAL=1
All pods for app: gke-fast-api-app are running and ready!

Step: Getting backend service IP
----------------------------------------
Backend service IP: http://34.29.90.111
(MedEnv) asuran@asuran:~/Downloads/projects/MedScript$ kubectl get deployments -n medscript
NAME          READY   UP-TO-DATE   AVAILABLE   AGE
gke-backend   1/1     1            1           34m