# data_pipeline/dags/src/base.py
import os
import requests
import json
from datetime import datetime
from logger import *

BASE_API_URL = "http://fastapi:8000/"

def get_data(url: str) -> dict:
    """
    Helper function to get data from the specified url.
    
    Parameters:
        url (str): The URL of the API endpoint to get data from.
        
    Returns:
        dict: The JSON response data from the API.
    """
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        logger.info("data:", data)
        return data
    else:
        raise

def get_summary(patient_id: int) -> dict:
    """
    Fetches summary for a patient with the given patient id and returns the data.

    Returns: The JSON data
    """
    url = BASE_API_URL + f"/api/v1/patient_summary/{patient_id}"
    return get_data(url)

def preprocess_data(data: dict) -> dict:
    """
    Processes and organizes patient data into a structured dictionary format.

    Parameters:
        data (dict): dictionary containing patient information and visit details.

    Returns:
        dict: A dictionary with processed data organized "User information" with patient details and "Symptoms"
    """
    if not data: 
        raise
    
    processed_data = {}
    processed_data["User information"] = extract_patient_details(data["patient"])
    processed_data["Symptoms"] = extract_symptoms(data["visits"])
    logger.info(processed_data)
    return processed_data

def calculate_age(date_of_birth: str) -> int:
    """
    Helper function to calculate age from the date of birth

    Parameters:
        date_of_birth (str): A string representing the date of birth 

    Returns:
        int: The calculated age
    """
    birthdate = datetime.strptime(date_of_birth, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

def calculate_bmi(weight, height_cm):
    """
    Helper function to calculate BMI using weight and height.

    Parameters:
        weight (float): The weight in kilograms.
        height_cm (float): The height in centimeters.

    Returns:
        float: The calculated BMI value
    """
    height_m = height_cm / 100 
    bmi = weight / (height_m ** 2)
    return bmi

def extract_patient_details(patient: dict) -> str:
    """
    Helper function to extract and format detailed patient information.

    Parameters:
        patient (dict): A dictionary containing patient information.

    Returns:
        str: A formatted string containing the extracted patient details.
    """

    age = calculate_age(patient['DateOfBirth'])
    gender = patient['Gender']
    bmi = calculate_bmi(patient['Weight'], patient["Height"])
    patient_details = f"""
            Age: {age}
            Gender: {gender}
            BloodType: {patient['BloodType']}
            BMI: {bmi}
            Medical History: No significant past medical issues
            Allergies: None known
            Current Medications: None
        """    
    return patient_details

def extract_symptoms(visits: dict) -> str:
    """
    Helper function to extract and format symptom descriptions from a list of patient visits.

    Args:
        visits (dict): A dictionary containing visit records, each with associated symptoms.

    Returns:
        str: A formatted string listing each symptom description from the visits.
    """
    symptoms_list = []
    for visit in visits:
        visit_symptoms = visit["symptoms"][0]
        symptoms_list.append(visit_symptoms["SymptomDescription"])
    
    symptoms = "\n".join([f"- {symptom}" for symptom in symptoms_list])
    return symptoms

def query_vector_database(data: dict) -> str:
    """
    Queries a vector database to fetch relevant records based on provided patient information and symptoms.

    Args:
        data (dict): A dictionary containing patient information and reported symptoms.

    Returns:
        str: Query string that includes patient information, reported symptoms, and any relevant context retrieved from the vector store.
    
    Raises:
        ValueError: If the input `data` is empty or invalid.
    """
    from query_vectorstore import vector_store
    if not data:
        logger.log_error("Data is empty or invalid.")
        raise ValueError("Data is empty or invalid.")
    
    query = f"""
    Patient Information: {data["User information"]}
    Reported Symptoms: {data["Symptoms"]}
    """

    # Fetch relevant records from the vector store
    relevant_results = vector_store.get_relevant_records(query=query)
    context = []
    if relevant_results:
        for i, result in enumerate(relevant_results):
            context_entry = result.payload.get('input')
            if context_entry:
                context.append(context_entry)
    if context:
        context_text = "\n".join(context)
        query += f"\n\nContext:\n{context_text}"
    else:
        logger.info("No relevant context found for this query.")
    
    logger.info(f"Final Prompt with Context: {query}")
    return query

def generate_prompt(query: str) -> str:
    """
    Generates a comprehensive prompt based on the given query string

    Args:
        query (str): A query string that includes patient information and symptoms.

    Returns:
        str: A formatted string containing a diagnostic report template with the provided query.
    """
     
    report_template = report_template = """
    # Comprehensive Diagnostic Report

    ## 1. Initial Impression
    [Provide a summary of key points from patient information and symptoms]

    ## 2. Possible Diagnoses
    ### Primary Diagnosis:
    [State the most likely diagnosis]

    ### Differential Diagnoses:
    [List other possible diagnoses]

    ## 3. Reasoning Process
    [For each diagnosis, explain why it's being considered and how symptoms support or contradict it]

    ## 4. Recommended Tests or Examinations
    [List and explain rationale for each recommended test]

    ## 5. Potential Treatment Options
    [Suggest treatments for the most likely diagnoses and explain reasoning]

    ## 6. Immediate Precautions or Recommendations
    [Provide urgent advice and explain its importance]

    ## 7. Follow-up Plan
    [Suggest follow-up timeline and what to monitor]

    ## 8. Summary
    [Provide a concise summary of likely diagnosis, key next steps, and important patient instructions]
    """

    prompt = f"""{query}
        Please provide a comprehensive diagnostic report following these steps:
        {report_template}

        Please fill in each section of the report template with relevant information based on the patient's symptoms and medical history. Provide clear and detailed explanations throughout your chain of reasoning."""
    
    return prompt

# def check_hf_permissions():
#     hf_home = os.getenv("HF_HOME", "/tmp/huggingface")
#     print(f"Checking permissions for HF_HOME directory at: {hf_home}")
#     if os.path.exists(hf_home):
#         for root, dirs, files in os.walk(hf_home):
#             print(f"\nDirectory: {root}")
#             for name in files:
#                 filepath = os.path.join(root, name)
#                 try:
#                     # Check read permission
#                     with open(filepath, "rb") as f:  # Use "rb" for binary-safe mode
#                         f.read(1024)  # Read first 1KB to confirm access
#                     print(f"Read permission OK for file: {filepath}")
#                 except PermissionError:
#                     print(f"Permission error for file: {filepath}")
#                 except UnicodeDecodeError:
#                     print(f"File is binary, read as binary successful: {filepath}")
#                 except Exception as e:
#                     print(f"Unexpected error for file {filepath}: {e}")
#     else:
#         print(f"HF_HOME directory does not exist at {hf_home}")


# def test_model_load():
#     try:
#         # Use the environment variable for HF_HOME as configured
#         hf_home = os.getenv("HF_HOME", "/tmp/huggingface")
#         print(f"Testing model load from HF_HOME: {hf_home}")
        
#         # Load tokenizer and model
#         tokenizer = BertTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
#         model = BertModel.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")

#         # Test model by running a simple embedding operation
#         inputs = tokenizer("Test sentence for loading model", return_tensors="pt")
#         outputs = model(**inputs)

#         # Check the shape of the output to ensure the model runs
#         print(f"Model loaded successfully. Output shape: {outputs.last_hidden_state.shape}")
#     except Exception as e:
#         print(f"Model load test failed: {e}")

# def check_hf_home():
#     hf_home = os.getenv("HF_HOME", "/root/.cache/huggingface")  # default path if HF_HOME isn't set
#     if os.path.exists(hf_home):
#         print(f"Checking contents of HF_HOME directory at: {hf_home}")
        
#         for root, dirs, files in os.walk(hf_home):
#             # Display the current directory
#             print(f"\nDirectory: {root}")
#             if not files and not dirs:
#                 print("  (Empty)")
            
#             # List files with details
#             for file in files:
#                 file_path = os.path.join(root, file)
#                 file_size = os.path.getsize(file_path)
#                 print(f"  File: {file} | Size: {file_size / 1024:.2f} KB")
                
#             # List subdirectories
#             for dir in dirs:
#                 print(f"  Subdirectory: {dir}")
#     else:
#         print(f"HF_HOME directory does not exist at {hf_home}")