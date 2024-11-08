# MedScript
AI assitant for diagnosis

Group Members: 
[Aishwariya Suryamindra](https://github.com/aishwarya-suyamindra) ,[Girish Kumar Adari](https://github.com/agirishkumar), [Mallika Gaikwad](https://github.com/MallikaGaikwad), [Om Mali](https://github.com/maliom939) , [Pramatha Bhat](https://github.com/pramathabhat), [Rohan Reddy](https://github.com/tantalum-73)


**Demo recordings** 
1. https://northeastern.zoom.us/rec/share/HFf1d277uKP9Kb9_2tgWFIjVbV6hyUSevlLwpkQwsSH-DSDlK-plGogxDqBTx1EJ.wokUQnQATvARIg8_?startTime=1730857443000
Passcode: 5jm=N*#!

2. https://northeastern.zoom.us/rec/share/HFf1d277uKP9Kb9_2tgWFIjVbV6hyUSevlLwpkQwsSH-DSDlK-plGogxDqBTx1EJ.wokUQnQATvARIg8_?startTime=1730857682000
Passcode: 5jm=N*#!

### Setup Instructions
Please confirm that **Python >= 3.8** or a later version is present on your system prior to installation. This application is designed to be compatible with Windows, Linux, and macOS platforms.

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
for Linux/Mac:
```bash
source MedEnv/bin/activate
```
for Windows:
```
MedEnv\Scripts\activate
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

**Step 5 :** Run the requirements.txt file to install all the required libraries 
```bash
pip install -r requirements.txt
```

**Step 6: Set up the .env file**
create a .env is main repo directory, refer to .env.example file for template.

**Step 7: Installing Docker**
- Ensure Docker is installed. To install, follow the instructions on [Docker website](https://docs.docker.com/engine/install/)

    ```bash
    docker --version
    docker-compose --version

**Step 8: Steps to try the app**
- change your directory to data_pipeline

``` cd data_pipeline ``

convert the initiate.sh file into executable and run it
```
 chmod +x initiate.sh```
```
```
./initiate.sh
```
this will setup the airflow, fastapi, setup the requirements for accessing gcloud and resources for RAG.
whenever this script is ran, it automatically removes the existing airflow containers, makes sure the ports are free

**Step 9: Accessing FastAPI & Airflow**

The Airflow UI will run on port `8080`. It can be accessed at `http://localhost:8080`. 

use username : admin, password: admin
to access the dashboard

The fastAPI UI will run on port `8000`. The API endpoints UI page can be accessed at `http://localhost:8000/docs`. 



### data_pipeline Folder structure

- **logs/**: Directory where logs for the Airflow tasks are stored.
- **dags/**: Contains files required for the workflow of the data pipeline.
  - **src/**: Directory has base.py file, which provides the helper functions to tasks.
  - **main.py**: Entry point for executing the data pipeline tasks.
  - other py files are related to RAG 
- **secrets/**: Contains Gcp keys
- **utils/**: Rag related utility files
- Docker-compose.yml file for building the containers required FAstApi and Airflow
- Dockerfile: Image thats used in the Docker compose file 

**MedScript Folder Structure**
 - data_pipeline: is already discussed above
 - app: Main backend application directory
      - api:  has the endpoints and dependencies code
      - core: has configuration and app logging code
      - db:  has crud , models, schemas defined in the respective folders
      - utils: has the authentication, http errors, middleware files
      - dockerfile: to run the backend in container
      - main.py: to run the backend
 - app-architecture-images: Contains diagrams of different functionality, workflow and components architecture
      - **DAG pipeline Image**
      - **DAG pipeline Gantt chart**
 -  tests:
      - unit: contains extensive unit tests for all the backend, db, Rag, Airflow 

**Run Unit Test**
```
pytest tests/unit/ --cov=app
```


Dataset that we used for RAG : URL: https://physionet.org/content/labelled-notes-hospital-course/1.1.0/

 License (for files):
PhysioNet Credentialed Health Data License 1.5.0

Data Use Agreement:
PhysioNet Credentialed Health Data Use Agreement 1.5.0

Required training:
CITI Data or Specimens Only Research 

-------------------------------------------------------------------------------

## Data Preprocessing

## MIMIC-4 Dataset Download and Upload to Google Cloud Storage Bucket

This script automates the process of downloading the MIMIC-4 dataset from PhysioNet and uploading it to a Google Cloud Storage (GCS) bucket. It includes error handling and logging features for streamlined data management. The script uses environment variables for secure access credentials.

## Data Preprocessing

This section processes clinical notes from the MIMIC-4 dataset to streamline structured data extraction, transformation, and analysis. We utilize Google Cloud Storage to store the preprocessed and transformed data, and each document section in the clinical notes is processed into meaningful, manageable chunks.

### Description

This pipeline preprocesses clinical notes from the MIMIC-4 dataset for machine learning applications. Key preprocessing tasks include:

- Cleaning and structuring clinical text data 
- Segmenting notes into predefined sections
- Replacing blanks, abbreviations, and placeholders
- Handling list formatting within the text
- Flattening nested data for storage
- Chunking large records into manageable JSON strings

### Steps in Preprocessing
#### 1. Download Dataset: 
- Load the dataset into memory using Python libraries (e.g., `pandas`, `csv`).
- Verify the data structure and check for missing or corrupt records.

#### 2. Text Segmentation: 
Clinical notes often contain multiple sections (e.g., patient history, diagnosis, medications). These sections should be properly segmented into smaller units for analysis.

Actions:

- Use sentence segmentation techniques to divide long clinical texts into sentences or paragraphs.
- Optionally, further divide by sections like “Patient History”, “Medications”, or “Diagnosis”.

#### 3. Data Flattening::

Sometimes, the data might have nested or hierarchical structures (e.g., multiple notes per patient or episode). Flattening simplifies the data by bringing everything into a consistent format.

Actions:

- Flatten the dataset such that each row corresponds to a single clinical note or text entry.
- This can be done by exploding nested columns or flattening JSON-like structures.

#### 4. Chunking Text:
Chunk long texts into manageable portions to avoid input size limitations in machine learning models.
Actions:

- Divide the text into smaller segments (chunks) based on the token count or paragraph length.
- Ensure that each chunk contains meaningful text and avoids cutting sentences in the middle.

#### 5. Removing Noise:
Remove irrelevant or noisy elements from the text to retain only useful data.

Actions:

- Remove non-text elements like headers, footers, or special characters.
- Eliminate any personal identifiers (e.g., patient names or ID numbers) using regex or a predefined list.


#### 8. Saving Preprocessed Data:
Save the preprocessed data in a structured format in csv


## Embedding Generator

`create_embedding.py` is a utility script designed to:
- Generate embeddings from text data (e.g., clinical notes) using a BERT model.
- Efficiently manage GPU memory for large-scale text data processing.
- Store the generated embeddings in Google Cloud Storage.

### Requirements
**Libraries**:
- `transformers` for the BERT model and tokenizer.
- `torch` for GPU-based tensor computations.
- `google-cloud-storage` for storing embeddings in GCS.
- `pandas`, `tqdm` for data handling and progress tracking.

## Qdrant Vector Database Integration

In this step we upload embedding vectors from a CSV file in Google Cloud Storage (GCS) to a Qdrant vector database. It handles downloading data from GCS, processing it in chunks, and uploading to Qdrant with retry logic for any failures.

### How It Works
1. Download Embedding Data: The script downloads a CSV file (embed_df_10k.csv) containing embeddings from Google Cloud Storage.

2. Setup Qdrant Collection: It checks if the specified collection exists in Qdrant and creates it if necessary.

3. Batch Processing: The embedding vectors are uploaded in batches (default chunk size: 100) to prevent memory overload and optimize performance.

4. Retry Logic: If uploading a batch fails, the script will automatically retry up to 3 times (with increasing delay between retries).

### Key Functions:

- **chunk_points**: Splits embedding points into smaller chunks for batch processing.
- **add_to_vectordb**: Uploads embeddings to Qdrant in batches with retry logic.
- **setup_qdrant_collection**: Ensures the Qdrant collection exists, creating it if not.
- **update_to_vectordb**: Main function to download data from GCS, process it, and upload to Qdrant.
- **get_qdrant_instance_ip**: Retrieves the IP address of the Qdrant instance on Google Cloud.


## Querying the Qdrant Vector Store

This step allows us to query a Qdrant vector database and retrieve the most relevant points to a given query. It uses a pre-trained transformer model ( PubMedBERT) to generate embeddings for the query and then searches for the most similar points in the Qdrant collection.

### How It Works
- **Query Embedding**: The query string is converted into a vector embedding using a pre-trained transformer model (PubMedBERT).
- **Search in Qdrant**: The generated embedding is used to search for the top `k` most similar vectors in the Qdrant collection. The search results are ranked based on similarity (cosine distance).
- **Display Results**: The top `k` results (default: 3) are returned, showing their IDs, similarity scores, and payload data.

The Data Pipeline is constructed like:
![MLOps Data Pipeline](https://github.com/user-attachments/assets/48db819b-cb65-4910-8ee7-e838c19d39aa)

## Pipeline Orchestration (Airflow DAGs):

The Base.py file consists the code to interact with a FastAPI backend to fetch patient summary data and process it for further analysis. The explanation:

1. **Imports and Setup**:
   - The code imports necessary libraries: `requests` for making HTTP requests, `json` for handling JSON data, and `datetime` for date manipulations.
   - A base API URL is defined for accessing the FastAPI service.

2. **Function Definitions**:
   - `get_data(url: str)`: A helper function that takes a URL as input, makes a GET request to that URL, and returns the JSON response if the request is successful. If the request fails, it raises an exception.
   - `get_summary(patient_id: int)`: This function constructs a URL to fetch a patient's summary by their ID and calls `get_data()` to retrieve the data.
   - `preprocess_data(data: dict)`: This function processes the data returned from the API. It extracts patient details and symptoms, raising an exception if no data is provided.
   - `calculate_age(date_of_birth: str)`: A helper function that calculates the age of a patient based on their date of birth.
   - `extract_patient_details(patient: dict)`: Extracts and formats details about the patient, including age, gender, medical history, and allergies.
   - `extract_symptoms(visits: dict)`: Compiles a list of reported symptoms from the patient's visits, formatting them for display.
   - `query_vector_database(data: dict)`: Generates a query string using the processed patient information and symptoms, and retrieves relevant records from a vector store database.
   - `generate_prompt(query: str)`: This function is defined but not implemented in the code. Its purpose would be to generate a prompt based on the query, possibly for further processing or interaction.

3. **Error Handling**:
   - In several places, the code includes checks to raise exceptions if the data is not valid or empty, ensuring that the subsequent operations have the required information.

Overall, the script fetches patient data from an API, processes it to extract relevant information, and prepares a query for further analysis or storage in a vector database.
There is a flowchart to explain the concept in more detail

```mermaid
graph TD;
  A[Start] --> B[BASE_API_URL Setup];
  B --> C[get_summary<br>Fetch data by patient ID];
  C --> D[get_data<br>Helper function<br>to make API request];
  D --> E{Response 200?};
  E -- Yes --> F[preprocess_data<br>Extracts relevant data];
  E -- No --> G[Error Handling<br>Raise error if not 200];
  F --> H[extract_patient_details<br>Extract age, gender];
  H --> I[extract_symptoms<br>Extract symptoms list];
  I --> J[query_vector_database<br>Creates query based on<br>patient info and symptoms];
  J --> K[vector_store.get_relevant_records<br>Search for similar records];
  K --> L[generate_prompt<br>Generate prompt from query];
  L --> M[End];
```

- The main.py orchestrates a sequence of tasks for processing patient data. 

**1. Imports:**
- The necessary modules and functions from Airflow and other libraries are imported, including DAG creation, Python tasks, email notifications, and triggering other DAGs.

**Default Arguments:**
- default_args specifies parameters for the DAG, including the number of retries and the delay between retries.

**DAG Definition:** 
The DAG is created with a unique identifier, description, and a start date.

**Tasks:**
Load Data Task: This task fetches the patient summary using the get_summary function for a specific patient ID.
Data Preprocessing Task: This task preprocesses the data retrieved from the previous task using the preprocess_data function.
Query Vector Database Task: This task queries the vector database for similarity searches using the processed data with the query_vector_database function.


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


## Data Versioning (DVC):
- DVC (Data Version Control) to manage and version control our datasets throughout the preprocessing pipeline
- Raw data is loaded from Google Cloud Storage (GCS), processed and cleaned using our Airflow pipeline, and the preprocessed data is then stored back to
![image](https://github.com/user-attachments/assets/b9dff95d-f960-4a23-83cf-3c83ac2e7520)


## Tests and Modules

The results of a test run for all the files in app/db. The testcases covers scenarios about creating patient details, updating it and deleting it. It also focuses on crud operations for all tables of doctor.py, patient.py, patient_details.py, patient_symptoms.py, patient_visits.py

**Test Results:**

* **Coverage:** The overall test coverage is 97%, which is a very good score and indicates a high degree of test coverage. 
151 tests were executed successfully.
149 passed and 2 kipped with 96% coverage


![image](https://github.com/user-attachments/assets/3324e65b-ac75-4b34-8ec8-b98d1e6877aa)


## Tracking and Logging
The logs file shows various operations related to patient details, doctor details and user login information, including fetching, creating, updating, and deleting patient and doctor records. There are several requests to the API, with status codes indicating successful (200, 201) and failed (404, 500) operations. Notable errors include an issue with inserting data due to a field value exceeding the character limit, and missing arguments in a function call.  Our pipeline is equipped with comprehensive logging to monitor progress and detect errors during data processing. We utilize Python’s logging library to create a custom logger that records key information at each step of the pipeline.

**Key Features:**
- **Progress Tracking**: Logs are generated at every stage, covering all functions in the pipeline.
- **Error Monitoring**: Errors are logged with detailed context, making issue identification and resolution quicker.
- **Custom Log Path**: All logs are stored in `MedScript/dev/logs/app.log` for easy access and troubleshooting.

<img width="1437" alt="image" src="https://github.com/user-attachments/assets/89339036-8dec-44c8-87a9-04ecdb5fba0e">

## Pipeline Flow Optimization

![image](https://github.com/user-attachments/assets/72023722-9ec1-4d72-85bd-8a3149c31dad)

The figure shows the Gantt chart from an Airflow DAG run, visualizing the execution timeline of tasks within the data_pipeline. It includes four tasks: load_data_task, data_preprocessing_task, query_vectorDB_task, and generate_prompt_task.

Each task's execution duration is represented by bars, with different segments indicating stages of the task's progress. load_data_task and data_preprocessing_task took the longest time to complete, while query_vectorDB_task and generate_prompt_task were shorter in duration. The pipeline appears to be running multiple iterations or instances, with several successful executions marked in green, showing consistent task completion across these runs.

![image](https://github.com/user-attachments/assets/38421e23-2fda-43f7-8b1d-e816e7e28bd5)

The figure shows task dependency graph of an Airflow DAG 'data_pipeline'. The pipeline consists of four tasks, each represented by a box, arranged sequentially from left to right:

1. `load_data_task`
2. `data_preprocessing_task`
3. `query_vectorDB_task`
4. `generate_prompt_task`

Each task has a "success" status, indicated by the green outline and check mark. This setup implies that each task depends on the completion of the previous one, following a linear workflow. All tasks are implemented using the `PythonOperator`.




