import base64
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import os
import json

def save_record_to_json(record, filename="records.json"):
    """Save or append the patient record to a JSON file."""
    if os.path.exists(filename):
        with open(filename, "r") as json_file:
            records = json.load(json_file)
    else:
        records = []

    records.append(record)

    with open(filename, "w") as json_file:
        json.dump(records, json_file, indent=4)

def parse_patient_record(text):
    """Parse the Patient Record section into the desired format."""
    patient_record = {}
    
    # Remove any markdown formatting
    text = text.replace('**', '')
    
    lines = text.strip().split('\n')
    for line in lines:
        if line.startswith('- ') and ':' in line:
            # Remove the leading "- " and split on first colon
            key, value = line[2:].split(':', 1)
            key = key.strip()
            value = value.strip()
            patient_record[key] = value
    
    return patient_record

def parse_diagnosis_report(text):
    """Parse the Diagnosis Report section into the desired format."""
    diagnosis_report = {
        "Possible Diagnoses": {
            "Primary Diagnosis": "",
            "Differential Diagnoses": []
        },
        "Reasoning Process": "",
        "Recommended Tests or Examinations": "",
        "Potential Treatment Options": "",
        "Immediate Precautions or Recommendations": "",
        "Follow-up Plan": ""
    }
    
    # Split by section headers
    sections = text.split('#')
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # Identify section type
        if section.startswith('Possible Diagnoses'):
            lines = section.split('\n')
            for line in lines:
                if "Primary Diagnosis:" in line:
                    diagnosis = line.split("Primary Diagnosis:", 1)[1]
                    diagnosis_report["Possible Diagnoses"]["Primary Diagnosis"] = (
                        diagnosis.replace('**', '').strip()
                    )
                elif "Differential Diagnoses:" in line:
                    diagnoses = line.split("Differential Diagnoses:", 1)[1]
                    # Split by semicolon or comma and clean up each diagnosis
                    diff_list = [
                        d.replace('**', '').strip() 
                        for d in diagnoses.split(',')
                    ]
                    diagnosis_report["Possible Diagnoses"]["Differential Diagnoses"] = diff_list
                    
        elif section.startswith('Reasoning Process'):
            content = section.replace('Reasoning Process', '').strip()
            diagnosis_report["Reasoning Process"] = content.replace('**', '')
            
        elif section.startswith('Recommended Tests'):
            content = section.replace('Recommended Tests or Examinations', '').strip()
            diagnosis_report["Recommended Tests or Examinations"] = content.replace('**', '')
            
        elif section.startswith('Potential Treatment'):
            content = section.replace('Potential Treatment Options', '').strip()
            diagnosis_report["Potential Treatment Options"] = content.replace('**', '')
            
        elif section.startswith('Immediate Precautions'):
            content = section.replace('Immediate Precautions or Recommendations', '').strip()
            diagnosis_report["Immediate Precautions or Recommendations"] = content.replace('**', '')
            
        elif section.startswith('Follow-up Plan'):
            content = section.replace('Follow-up Plan', '').strip()
            diagnosis_report["Follow-up Plan"] = content.replace('**', '')
    
    return diagnosis_report

def generate():
    sa_path = "../data_pipeline/secrets/medscript-sa.json"
    credentials = service_account.Credentials.from_service_account_file(sa_path)
    
    vertexai.init(project="medscript-437117", location="us-east4", credentials=credentials)
    
    model = GenerativeModel("gemini-1.5-flash-002")
    
    total_records = 1000
    for patient_id in range(552, total_records + 1):
        print(f"Generating record {patient_id}/{total_records}")
        
        response = model.generate_content(
            [text1],
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False
        )
        
        # Split into Patient Record and Diagnosis Report sections
        full_text = response.text.replace('\n\n', '\n').strip()
        
        # Extract Patient Record section
        if "#Patient Record" in full_text:
            parts = full_text.split("#Patient Record")
            if len(parts) > 1:
                record_part = parts[1].split("#Diagnosis Report")[0].strip()
                diagnosis_part = parts[1].split("#Diagnosis Report")[1].strip()
        else:
            # Alternative format
            parts = full_text.split("# Patient Record")
            if len(parts) > 1:
                record_part = parts[1].split("# Diagnosis Report")[0].strip()
                diagnosis_part = parts[1].split("# Diagnosis Report")[1].strip()
        
        # Parse sections into desired format
        patient_record = parse_patient_record(record_part)
        diagnosis_report = parse_diagnosis_report(diagnosis_part)
        
        # Create final record
        record = {
            "patientId": str(patient_id),
            "patientRecord": patient_record,
            "diagnosisReport": diagnosis_report
        }
        
        save_record_to_json(record)
    
    print("Record generation completed.")

text1 = """Please generate medical records with high diversity across these dimensions:
    1. Demographics:
    - Mix of genders (male, female)
    - Ages ranging from 5 to 95
    - Various occupations and lifestyle factors

    2. Medical Presentations:
    - Mix of acute and chronic conditions
    - Various body systems (cardiovascular, gastrointestinal, genitourinary, neurologic, respiratory, orthopedic, skeletal etc. use less of cough/pneumonia)
    - Different severity levels (mild, moderate, severe)
    - Both simple and complex cases

    3. Medical History:
    - Various existing conditions (use less of hypertension/diabetes)
    - Different medication profiles
    - Range of allergies
    - Different visit histories

    4. Diagnoses:
    - Mix of common and rare conditions
    - Various specialties involved
    - Different levels of diagnostic certainty
    
    Generate a single detailed male patient record and a diagnosis report with the following structure:

        #Patient Record
        - Gender
        - Age
        - Height(in cm numbers only no units)
        - Weight(in kg numbers only no units)
        - Blood type
        - Detailed symptoms (at least 3)
        - Duration of the symptoms (example 3 days, 2 weeks, 1 month)
        - Severity (mild, moderate, severe)
        - Existing medical conditions (varying diverse Existing medical conditions)
        - Allergies (if any, show variations)
        - Current medications (if any)
        - Number of previous visits

        #Diagnosis Report
        ## Possible Diagnoses
        - **Primary Diagnosis:** [State the most likely diagnosis]
        - **Differential Diagnoses:** [List other possible diagnoses]

        ## Reasoning Process
        - [For each diagnosis, explain why it's being considered and how symptoms support or contradict it]

        ## Recommended Tests or Examinations
        - [List and explain rationale for each recommended test]

        ## Potential Treatment Options
        - [Suggest treatments for the most likely diagnoses and explain reasoning]

        ## Immediate Precautions or Recommendations
        - [Provide urgent advice and explain its importance]

        ## Follow-up Plan
        - [Suggest follow-up timeline and what to monitor]

        Ensure the content is clear, concise, and aligns with the patient’s symptoms and medical history. Do not include any "Notes" section, "Physician Signature," or "Date" fields in the output."""

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 2,
    "top_p": 0.95,
}

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

if __name__ == "__main__":
    generate()
