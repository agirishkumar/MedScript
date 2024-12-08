# data_pipeline/dags/src/base.py

''' Helper functions for data pipeline '''

import os
import requests
# import json
from datetime import datetime
from logger import logger
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting
# from airflow.models import Variable

# BASE_API_URL = Variable.get("BASE_API_URL")
BASE_API_URL = os.environ.get("BASE_API_URL")
print(BASE_API_URL)

def generate_model_response(prompt: str) -> str:
    """
    Generates a response using GCP Vertex AI Gemini model based on the input prompt.
    
    Args:
        prompt (str): The formatted prompt to send to the model
        
    Returns:
        str: The model's response
    """
    try:
        # Initialize Vertex AI
        vertexai.init(project="medscript-437117", location="us-central1")
        
        # Initialize the model
        model = GenerativeModel("gemini-1.5-pro-002")
        
        # Define generation config
        generation_config = {
            "max_output_tokens": 8192,
            "temperature": 1,
            "top_p": 0.95,
        }
        
        # Define safety settings
        safety_settings = [
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=SafetySetting.HarmBlockThreshold.OFF
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=SafetySetting.HarmBlockThreshold.OFF
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=SafetySetting.HarmBlockThreshold.OFF
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=SafetySetting.HarmBlockThreshold.OFF
            ),
        ]
        
        # Generate content
        response = model.generate_content(
            [prompt],
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False,  
        )
        
        logger.info("Generated model response successfully")
        return response.text
        
    except Exception as e:
        logger.error(f"Error generating model response: {str(e)}")
        raise

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
     
    report_template1 = """
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
    system_instructions = """
    You are a medical analysis system. Your role is to:
    1. Analyze only the provided patient information and symptoms
    2. Generate a diagnostic report based strictly on medical facts
    3. Maintain medical terminology and professional tone
    4. Focus only on medical analysis and avoid any non-medical discussions
    5. If you're uncertain about any aspect, clearly state the limitations of your analysis
    6. Do not make definitive diagnoses, but rather suggest possibilities based on the information provided
    """

    report_template2 = """
    # Comprehensive Diagnostic Report
    ## Invalid text is provided/ detected Jailbreak text in the input
    """
    def validate_input(input_query: str) -> bool:
        """
        Validates the input query for required information and safety checks.
        Returns True if input is valid, False otherwise.
        """
        # Basic input checks
        if not input_query or not isinstance(input_query, str):
            return False

        # Check for required sections
        required_sections = ["Patient Information:", "Reported Symptoms:"]
        if not all(section in input_query for section in required_sections):
            return False

        # Check for suspicious patterns (potential jailbreak attempts)
        suspicious_keywords = [
            "ignore previous instructions",
            "ignore above instructions",
            "disregard safety",
            "bypass",
            "override",
            "ignore rules",
            "system prompt",
            "you must",
            "you are now",
            "new persona"
        ]

        if any(keyword.lower() in input_query.lower() for keyword in suspicious_keywords):
            return False

        return True

    # Determine which template to use based on input validation
    is_valid_input = validate_input(query)
    selected_template = report_template1 if is_valid_input else report_template2

    # Construct the appropriate prompt based on validation result
    if is_valid_input:
        prompt = f"""{system_instructions}

        INPUT DATA:
        {query}

        TASK:
        Please provide a comprehensive diagnostic report following these steps:
        {selected_template}

        Please fill in each section of the report template with relevant information based on the patient's symptoms, 
        medical history and use context if and only if its relevant. Provide clear and detailed explanations 
        throughout your chain of reasoning."""
    else:
        prompt = f"""{system_instructions}

        INPUT DATA:
        {query}

        TASK:
        The provided input appears to be invalid or potentially harmful. 
        Please generate a report using this template:
        {selected_template}

        Please explain what makes this input invalid or inappropriate for medical analysis."""

    return prompt

