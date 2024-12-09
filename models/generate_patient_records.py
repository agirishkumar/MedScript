import base64
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import os
import json
import random

def load_existing_records(filename="records.json"):
    """Load existing records to analyze distributions."""
    try:
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, "r") as json_file:
                return json.load(json_file)
    except json.JSONDecodeError:
        print(f"Warning: {filename} is not properly formatted. Starting fresh.")
    except Exception as e:
        print(f"Warning: Error reading {filename}: {str(e)}. Starting fresh.")
    return []

def save_record_to_json(record, filename="records.json"):
    """Save or append the patient record to a JSON file."""
    try:
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, "r") as json_file:
                records = json.load(json_file)
        else:
            records = []
    except (json.JSONDecodeError, Exception) as e:
        print(f"Warning: Error reading existing records: {str(e)}. Starting fresh.")
        records = []

    records.append(record)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    
    try:
        with open(filename, "w") as json_file:
            json.dump(records, json_file, indent=4)
    except Exception as e:
        print(f"Error saving record: {str(e)}")
        # Optionally, create a backup file with just this record
        backup_filename = f"record_{record['patientId']}.json"
        with open(backup_filename, "w") as backup_file:
            json.dump([record], backup_file, indent=4)
        print(f"Saved record to backup file: {backup_filename}")



def analyze_distributions(records):
    """Analyze current distributions of key attributes."""
    if not records:  # Handle empty records case
        return {
            'age_groups': {'0-18': 0, '19-40': 0, '41-65': 0, '65+': 0},
            'conditions_count': {},
            'gender_count': {'Male': 0, 'Female': 0}
        }
        
    distributions = {
        'age_groups': {'0-18': 0, '19-40': 0, '41-65': 0, '65+': 0},
        'conditions_count': {},
        'gender_count': {'Male': 0, 'Female': 0},
    }
    
    for record in records:
        try:
            # Analyze age distribution
            age = int(record['patientRecord']['Age'])
            if age <= 18:
                distributions['age_groups']['0-18'] += 1
            elif age <= 40:
                distributions['age_groups']['19-40'] += 1
            elif age <= 65:
                distributions['age_groups']['41-65'] += 1
            else:
                distributions['age_groups']['65+'] += 1
                
            # Analyze conditions
            conditions = record['patientRecord'].get('Existing medical conditions', '').split(',')
            for condition in conditions:
                condition = condition.strip()
                if condition:
                    distributions['conditions_count'][condition] = distributions['conditions_count'].get(condition, 0) + 1
            
            # Analyze gender
            gender = record['patientRecord']['Gender']
            distributions['gender_count'][gender] = distributions['gender_count'].get(gender, 0) + 1
        except (KeyError, ValueError) as e:
            print(f"Warning: Error processing record: {str(e)}. Skipping.")
            continue
    
    return distributions

def generate_prompt_constraints(distributions, patient_id):
    """Generate specific constraints based on current distributions."""
    age_groups = distributions['age_groups']
    total_records = sum(age_groups.values())
    
    # For the first record or when no records exist, use default distributions
    if total_records == 0:
        target_age_group = "between 19 and 40"  # Start with middle age range
        gender_preference = "any gender"
        common_conditions = []
    else:
        # Determine which age group is underrepresented
        percentages = {k: v/total_records for k, v in age_groups.items()}
        if percentages.get('0-18', 0) < 0.15:
            target_age_group = "between 5 and 18"
        elif percentages.get('19-40', 0) < 0.35:
            target_age_group = "between 19 and 40"
        elif percentages.get('41-65', 0) < 0.35:
            target_age_group = "between 41 and 65"
        elif percentages.get('65+', 0) < 0.15:
            target_age_group = "above 65"
        else:
            target_age_group = "varied"

        # Adjust gender balance
        gender_preference = None
        if distributions['gender_count'].get('Male', 0) > distributions['gender_count'].get('Female', 0):
            gender_preference = "Female"
        elif distributions['gender_count'].get('Female', 0) > distributions['gender_count'].get('Male', 0):
            gender_preference = "Male"
        else:
            gender_preference = "any gender"

        # Avoid common conditions
        common_conditions = [cond for cond, count in distributions['conditions_count'].items() 
                           if count > total_records * 0.1]

    constraints = f"""Please generate a medical record with these specific constraints:
    1. Patient age should be {target_age_group}
    2. Gender should be {gender_preference}
    3. Please avoid these common conditions that are overrepresented: {', '.join(common_conditions) if common_conditions else 'None yet'}
    4. For record #{patient_id}, ensure high uniqueness in:
        - Height (vary between 150-190 cm for adults, adjust appropriately for children)
        - Weight (vary appropriately based on height and age)
        - Blood type (maintain realistic distribution)
        - Symptoms (avoid repetition from common patterns)
        
    {text1}
    """
    return constraints

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
    for patient_id in range(1, total_records + 1):
        print(f"Generating record {patient_id}/{total_records}")
        
        # Load and analyze existing records
        existing_records = load_existing_records()
        distributions = analyze_distributions(existing_records)
        
        # Generate constraints based on current distributions
        constrained_prompt = generate_prompt_constraints(distributions, patient_id)
        
        try:
            response = model.generate_content(
                [constrained_prompt],
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=False
            )
            
            # Rest of your parsing logic remains the same
            full_text = response.text.replace('\n\n', '\n').strip()
            
            if "#Patient Record" in full_text:
                parts = full_text.split("#Patient Record")
                if len(parts) > 1:
                    record_part = parts[1].split("#Diagnosis Report")[0].strip()
                    diagnosis_part = parts[1].split("#Diagnosis Report")[1].strip()
            else:
                parts = full_text.split("# Patient Record")
                if len(parts) > 1:
                    record_part = parts[1].split("# Diagnosis Report")[0].strip()
                    diagnosis_part = parts[1].split("# Diagnosis Report")[1].strip()
            
            patient_record = parse_patient_record(record_part)
            diagnosis_report = parse_diagnosis_report(diagnosis_part)
            
            record = {
                "patientId": str(patient_id),
                "patientRecord": patient_record,
                "diagnosisReport": diagnosis_report
            }
            
            save_record_to_json(record)
            
        except Exception as e:
            print(f"Error generating record {patient_id}: {str(e)}")
            continue
    
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
    
    Generate a single detailed patient record and a diagnosis report with the following structure:

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
    "temperature": 1.3,
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
