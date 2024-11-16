# import json
# import os
# from google.cloud import aiplatform
# from google.auth import credentials
# from google.oauth2 import service_account
# import concurrent.futures

# class Med42Processor:
#     def __init__(self):
#         # Load credentials
#         sa_path = "../data_pipeline/secrets/medscript-sa.json"
#         self.credentials = service_account.Credentials.from_service_account_file(sa_path)
        
#         # Endpoint configurations
#         self.endpoints = {
#             "odd": {
#                 "project": "946534278700",
#                 "endpoint_id": "8522239860101087232",
#                 "location": "us-east4"
#             },
#             "even": {
#                 "project": "946534278700",
#                 "endpoint_id": "6570031676217360384",
#                 "location": "us-central1"
#             }
#         }
        
#         self.init_endpoints()

#     def init_endpoints(self):
#         # Initialize endpoints
#         for config in self.endpoints.values():
#             aiplatform.init(
#                 project=config["project"],
#                 location=config["location"],
#                 credentials=self.credentials
#             )

#     def format_prompt(self, patient_record):
#         """Format the patient record into a concise prompt"""
#         prompt = f"""Patient Information:
# Gender: {patient_record['Gender']}
# Age: {patient_record['Age']}
# Symptoms: {patient_record['Detailed symptoms']}
# Duration: {patient_record['Duration of the symptoms']}
# Severity: {patient_record['Severity']}
# Medical History: {patient_record['Existing medical conditions']}
# Medications: {patient_record['Current medications']}
# Allergies: {patient_record['Allergies']}

# Based on the above information, provide a detailed diagnosis report following this exact structure:
# #Diagnosis Report
# ## Possible Diagnoses
# - Primary Diagnosis:
# - Differential Diagnoses:
# ## Reasoning Process
# ## Recommended Tests or Examinations
# ## Potential Treatment Options
# ## Immediate Precautions or Recommendations
# ## Follow-up Plan"""
#         return prompt

#     def call_endpoint(self, endpoint_type, instance):
#         """Call the appropriate endpoint based on patient ID"""
#         config = self.endpoints[endpoint_type]
        
#         endpoint = aiplatform.Endpoint(
#             endpoint_name=f"projects/{config['project']}/locations/{config['location']}/endpoints/{config['endpoint_id']}"
#         )
        
#         response = endpoint.predict(instances=[{"prompt": instance}])
#         return response.predictions[0]

#     def process_record(self, record):
#         """Process a single patient record"""
#         patient_id = int(record["patientId"])
#         endpoint_type = "odd" if patient_id % 2 != 0 else "even"
        
#         # Format the prompt
#         prompt = self.format_prompt(record["patientRecord"])
        
#         try:
#             # Get model prediction
#             med42_response = self.call_endpoint(endpoint_type, prompt)
            
#             # Parse the response using the existing diagnosis report parser
#             med42_diagnosis = parse_diagnosis_report(med42_response)
            
#             # Add the med42 diagnosis to the record
#             record["med42_diagnosis"] = med42_diagnosis
            
#             return record
#         except Exception as e:
#             print(f"Error processing patient ID {patient_id}: {str(e)}")
#             return None

#     def process_all_records(self):
#         """Process all records in the JSON file"""
#         # Load records
#         with open("records.json", "r") as f:
#             records = json.load(f)
        
#         updated_records = []
        
#         # Process records in parallel
#         with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
#             future_to_record = {executor.submit(self.process_record, record): record 
#                               for record in records}
            
#             for future in concurrent.futures.as_completed(future_to_record):
#                 record = future_to_record[future]
#                 try:
#                     processed_record = future.result()
#                     if processed_record:
#                         updated_records.append(processed_record)
#                 except Exception as e:
#                     print(f"Error processing record {record['patientId']}: {str(e)}")

#         # Save updated records
#         with open("records_with_med42.json", "w") as f:
#             json.dump(updated_records, f, indent=4)

# def parse_diagnosis_report(text):
#     """Parse the diagnosis report text into structured format"""
#     diagnosis_report = {
#         "Possible Diagnoses": {
#             "Primary Diagnosis": "",
#             "Differential Diagnoses": []
#         },
#         "Reasoning Process": "",
#         "Recommended Tests or Examinations": "",
#         "Potential Treatment Options": "",
#         "Immediate Precautions or Recommendations": "",
#         "Follow-up Plan": ""
#     }
    
#     sections = text.split('#')
    
#     for section in sections:
#         section = section.strip()
#         if not section:
#             continue
            
#         if section.startswith('Possible Diagnoses'):
#             lines = section.split('\n')
#             for line in lines:
#                 if "Primary Diagnosis:" in line:
#                     diagnosis = line.split("Primary Diagnosis:", 1)[1]
#                     diagnosis_report["Possible Diagnoses"]["Primary Diagnosis"] = (
#                         diagnosis.replace('**', '').strip()
#                     )
#                 elif "Differential Diagnoses:" in line:
#                     diagnoses = line.split("Differential Diagnoses:", 1)[1]
#                     diff_list = [d.replace('**', '').strip() 
#                                for d in diagnoses.split(',')]
#                     diagnosis_report["Possible Diagnoses"]["Differential Diagnoses"] = diff_list
                    
#         elif section.startswith('Reasoning Process'):
#             content = section.replace('Reasoning Process', '').strip()
#             diagnosis_report["Reasoning Process"] = content.replace('**', '')
            
#         elif section.startswith('Recommended Tests'):
#             content = section.replace('Recommended Tests or Examinations', '').strip()
#             diagnosis_report["Recommended Tests or Examinations"] = content.replace('**', '')
            
#         elif section.startswith('Potential Treatment'):
#             content = section.replace('Potential Treatment Options', '').strip()
#             diagnosis_report["Potential Treatment Options"] = content.replace('**', '')
            
#         elif section.startswith('Immediate Precautions'):
#             content = section.replace('Immediate Precautions or Recommendations', '').strip()
#             diagnosis_report["Immediate Precautions or Recommendations"] = content.replace('**', '')
            
#         elif section.startswith('Follow-up Plan'):
#             content = section.replace('Follow-up Plan', '').strip()
#             diagnosis_report["Follow-up Plan"] = content.replace('**', '')
    
#     return diagnosis_report

# if __name__ == "__main__":
#     processor = Med42Processor()
#     processor.process_all_records()

import json
import os
from google.cloud import aiplatform
from google.auth import credentials
from google.oauth2 import service_account
import concurrent.futures
from tqdm import tqdm
import threading

class Med42Processor:
    def __init__(self):
        sa_path = "../data_pipeline/secrets/medscript-sa.json"
        self.credentials = service_account.Credentials.from_service_account_file(sa_path)
        
        # Endpoint configurations
        self.endpoints = {
            "odd": {
                "project": "946534278700",
                "endpoint_id": "8522239860101087232",
                "location": "us-east4"
            },
            "even": {
                "project": "946534278700",
                "endpoint_id": "6570031676217360384",
                "location": "us-central1"
            }
        }
        
        self.init_endpoints()
        # Add a lock for thread-safe file operations
        self.file_lock = threading.Lock()
        self.output_file = "records_with_med42.json"

    def init_endpoints(self):
        for config in self.endpoints.values():
            aiplatform.init(
                project=config["project"],
                location=config["location"],
                credentials=self.credentials
            )

    def format_prompt(self, patient_record):
        prompt = f"""Generate a detailed medical diagnosis report for the following patient:
Patient Information:
Gender: {patient_record['Gender']}
Age: {patient_record['Age']}
Symptoms: {patient_record['Detailed symptoms']}
Duration: {patient_record['Duration of the symptoms']}
Severity: {patient_record['Severity']}
Medical History: {patient_record['Existing medical conditions']}
Medications: {patient_record['Current medications']}
Allergies: {patient_record['Allergies']}

Provide a diagnosis report following this EXACT format and headings:
#Diagnosis Report
## Possible Diagnoses
- Primary Diagnosis: [single most likely diagnosis]
- Differential Diagnoses:
  - [diagnosis 1]
  - [diagnosis 2]
  - [diagnosis 3]
## Reasoning Process
[Explain reasoning for primary and differential diagnoses]
## Recommended Tests or Examinations
[List specific tests needed]
## Potential Treatment Options
[List treatment options]
## Immediate Precautions or Recommendations
[List immediate advice]
## Follow-up Plan
[Specify follow-up timeline and monitoring]

Use only the sections listed above. Format using markdown with dashes (-) for lists."""
        return prompt

    def parse_med42_response(self, text):
        """Parse and format med42 response to match existing diagnosis report structure"""
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
        
        # Split by sections
        sections = text.split('##')
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            if section.startswith('Possible Diagnoses'):
                lines = [line.strip() for line in section.split('\n') if line.strip()]
                
                # Parse Primary Diagnosis
                for line in lines:
                    if 'Primary Diagnosis:' in line:
                        diagnosis_report["Possible Diagnoses"]["Primary Diagnosis"] = (
                            line.split('Primary Diagnosis:', 1)[1].strip()
                        )
                
                # Parse Differential Diagnoses
                differentials = []
                capture_diff = False
                for line in lines:
                    if 'Differential Diagnoses:' in line:
                        capture_diff = True
                        continue
                    if capture_diff and line.strip().startswith('-'):
                        diff = line.strip('- ').strip()
                        if diff:
                            differentials.append(diff)
                diagnosis_report["Possible Diagnoses"]["Differential Diagnoses"] = differentials
                
            elif section.startswith('Reasoning Process'):
                diagnosis_report["Reasoning Process"] = (
                    section.replace('Reasoning Process', '').strip()
                )
                
            elif section.startswith('Recommended Tests'):
                diagnosis_report["Recommended Tests or Examinations"] = (
                    section.replace('Recommended Tests or Examinations', '').strip()
                )
                
            elif section.startswith('Potential Treatment'):
                diagnosis_report["Potential Treatment Options"] = (
                    section.replace('Potential Treatment Options', '').strip()
                )
                
            elif section.startswith('Immediate Precautions'):
                diagnosis_report["Immediate Precautions or Recommendations"] = (
                    section.replace('Immediate Precautions or Recommendations', '').strip()
                )
                
            elif section.startswith('Follow-up Plan'):
                diagnosis_report["Follow-up Plan"] = (
                    section.replace('Follow-up Plan', '').strip()
                )
        
        return diagnosis_report
    
    def save_record(self, record):
        """Thread-safe method to save a single record to file"""
        with self.file_lock:
            existing_records = []
            if os.path.exists(self.output_file):
                with open(self.output_file, 'r') as f:
                    try:
                        existing_records = json.load(f)
                    except json.JSONDecodeError:
                        existing_records = []
            
            # Check if record already exists and update/append accordingly
            record_exists = False
            for i, existing_record in enumerate(existing_records):
                if existing_record['patientId'] == record['patientId']:
                    existing_records[i] = record
                    record_exists = True
                    break
            
            if not record_exists:
                existing_records.append(record)
            
            with open(self.output_file, 'w') as f:
                json.dump(existing_records, f, indent=4)

    def call_endpoint(self, endpoint_type, prompt):
        config = self.endpoints[endpoint_type]
        
        endpoint = aiplatform.Endpoint(
            endpoint_name=f"projects/{config['project']}/locations/{config['location']}/endpoints/{config['endpoint_id']}"
        )
        
        instance = {
            "inputs": prompt
        }
        
        print(f"\nSending request to {endpoint_type} endpoint:")
        print(f"Prompt:\n{prompt}\n")
        
        response = endpoint.predict(instances=[instance])
        print(f"Response received:\n{response.predictions[0]}\n")
        
        formatted_response = self.parse_med42_response(response.predictions[0])
        print(f"Formatted Response:\n{json.dumps(formatted_response, indent=2)}\n")
        
        return formatted_response
    
    def process_single_record(self, record):
        """Process a single record and save it"""
        try:
            patient_id = record["patientId"]
            endpoint_type = "odd" if int(patient_id) % 2 != 0 else "even"
            
            prompt = self.format_prompt(record["patientRecord"])
            
            # Call endpoint
            config = self.endpoints[endpoint_type]
            endpoint = aiplatform.Endpoint(
                endpoint_name=f"projects/{config['project']}/locations/{config['location']}/endpoints/{config['endpoint_id']}"
            )
            
            instance = {"inputs": prompt}
            response = endpoint.predict(instances=[instance])
            
            # Parse and format response
            formatted_response = self.parse_med42_response(response.predictions[0])
            
            # Add med42 diagnosis to record
            record["med42_diagnosis"] = formatted_response
            
            # Save the processed record
            self.save_record(record)
            
            print(f"✓ Successfully processed patient ID: {patient_id}")
            return record
            
        except Exception as e:
            print(f"✗ Error processing patient ID {record['patientId']}: {str(e)}")
            return None

    def process_records(self, num_records=2):
        """Process records and append them to file as they are completed"""
        output_file = "test_records_with_med42.json"
        
        # Load existing records if file exists
        existing_records = []
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                try:
                    existing_records = json.load(f)
                    print(f"\nFound existing file with {len(existing_records)} records")
                except json.JSONDecodeError:
                    print("\nExisting file is empty or corrupted, starting fresh")
                    existing_records = []
        
        # Get processed patient IDs
        processed_ids = set(str(record['patientId']) for record in existing_records)
        
        # Load and process new records
        with open("records.json", "r") as f:
            all_records = json.load(f)
        
        records_to_process = []
        for record in all_records[:num_records]:
            if record['patientId'] not in processed_ids:
                records_to_process.append(record)
        
        print(f"\nFound {len(records_to_process)} new records to process")
        
        for i, record in enumerate(records_to_process, 1):
            patient_id = record["patientId"]
            print(f"\n[{i}/{len(records_to_process)}] Processing patient ID: {patient_id}")
            
            endpoint_type = "odd" if int(patient_id) % 2 != 0 else "even"
            prompt = self.format_prompt(record["patientRecord"])
            
            try:
                print(f"Calling {endpoint_type} endpoint...")
                med42_response = self.call_endpoint(endpoint_type, prompt)
                record["med42_diagnosis"] = med42_response
                
                # Append to existing records
                existing_records.append(record)
                
                # Save after each successful processing
                with open(output_file, "w") as f:
                    json.dump(existing_records, f, indent=4)
                
                print(f"✓ Successfully processed and saved patient ID: {patient_id}")
                
            except Exception as e:
                print(f"✗ Error processing patient ID {patient_id}: {str(e)}")
                continue
        
        total_processed = len(existing_records)
        print(f"\nProcessing completed:")
        print(f"- Total records processed: {total_processed}")
        print(f"- Results saved to: {output_file}")

    def process_all_records(self):
        """Process all records in parallel"""
        # Load all records
        with open("records.json", "r") as f:
            all_records = json.load(f)
        
        # Get already processed records
        processed_ids = set()
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r') as f:
                try:
                    processed_records = json.load(f)
                    processed_ids = set(str(record['patientId']) for record in processed_records)
                except json.JSONDecodeError:
                    processed_ids = set()
        
        # Filter records that need processing
        records_to_process = [r for r in all_records if r['patientId'] not in processed_ids]
        
        print(f"\nTotal records to process: {len(records_to_process)}")
        print(f"Already processed: {len(processed_ids)}")
        
        # Process records in parallel with progress bar
        with tqdm(total=len(records_to_process), desc="Processing records") as pbar:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                # Submit all tasks
                future_to_record = {
                    executor.submit(self.process_single_record, record): record 
                    for record in records_to_process
                }
                
                # Process completed tasks as they finish
                for future in concurrent.futures.as_completed(future_to_record):
                    record = future_to_record[future]
                    try:
                        result = future.result()
                        if result:
                            pbar.update(1)
                    except Exception as e:
                        print(f"\nError processing record {record['patientId']}: {str(e)}")
        
        print("\nProcessing completed!")
        
        # Print final statistics
        with open(self.output_file, 'r') as f:
            final_records = json.load(f)
            print(f"Total records processed successfully: {len(final_records)}")

    def process_single_patient(self, patient_id):
        """Process a single patient by ID and add/update in the output file"""
        print(f"\nProcessing patient ID: {patient_id}")
        
        # Load original record
        try:
            with open("records.json", "r") as f:
                all_records = json.load(f)
                record = next((r for r in all_records if r['patientId'] == str(patient_id)), None)
                
            if not record:
                print(f"✗ Patient ID {patient_id} not found in records.json")
                return False
                
        except Exception as e:
            print(f"✗ Error loading records: {str(e)}")
            return False
        
        try:
            # Determine endpoint
            endpoint_type = "odd" if int(patient_id) % 2 != 0 else "even"
            print(f"Using {endpoint_type} endpoint...")
            
            # Format prompt
            prompt = self.format_prompt(record["patientRecord"])
            
            # Call endpoint
            config = self.endpoints[endpoint_type]
            endpoint = aiplatform.Endpoint(
                endpoint_name=f"projects/{config['project']}/locations/{config['location']}/endpoints/{config['endpoint_id']}"
            )
            
            instance = {"inputs": prompt}
            print("Calling model endpoint...")
            response = endpoint.predict(instances=[instance])
            
            # Parse and format response
            formatted_response = self.parse_med42_response(response.predictions[0])
            record["med42_diagnosis"] = formatted_response
            
            # Save/update record
            print("Saving result...")
            self.save_record(record)
            
            print(f"✓ Successfully processed and saved patient ID: {patient_id}")
            print(f"\nDiagnosis Summary:")
            print(f"Primary Diagnosis: {formatted_response['Possible Diagnoses']['Primary Diagnosis']}")
            print("Differential Diagnoses:")
            for diff in formatted_response['Possible Diagnoses']['Differential Diagnoses']:
                print(f"- {diff}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error processing patient ID {patient_id}: {str(e)}")
        return False

    def process_all_records(self, start_id=1000, end_id=368):
        """Process records from start_id to end_id in descending order"""
        try:
            # Load all records
            with open("records.json", "r") as f:
                all_records = json.load(f)
            
            # Get already processed records
            processed_ids = set()
            if os.path.exists(self.output_file):
                with open(self.output_file, 'r') as f:
                    try:
                        processed_records = json.load(f)
                        processed_ids = set(str(record['patientId']) for record in processed_records)
                    except json.JSONDecodeError:
                        processed_ids = set()
            
            # Filter and sort records in reverse order
            records_to_process = [
                r for r in all_records 
                if (str(r['patientId']) not in processed_ids and 
                    end_id <= int(r['patientId']) <= start_id)
            ]
            records_to_process.sort(key=lambda x: int(x['patientId']), reverse=True)
            
            print(f"\nTotal records to process: {len(records_to_process)}")
            print(f"Already processed: {len(processed_ids)}")
            print(f"Processing records from ID {start_id} to {end_id}")
            
            # Process records in parallel with progress bar
            with tqdm(total=len(records_to_process), desc="Processing records") as pbar:
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    # Submit tasks in reverse order
                    future_to_record = {
                        executor.submit(self.process_single_record, record): record 
                        for record in records_to_process
                    }
                    
                    # Process completed tasks as they finish
                    for future in concurrent.futures.as_completed(future_to_record):
                        record = future_to_record[future]
                        try:
                            result = future.result()
                            if result:
                                pbar.update(1)
                                pbar.set_description(
                                    f"Processing records (Current ID: {record['patientId']})"
                                )
                        except Exception as e:
                            print(f"\nError processing record {record['patientId']}: {str(e)}")
            
            print("\nProcessing completed!")
            
            # Print final statistics
            with open(self.output_file, 'r') as f:
                final_records = json.load(f)
                print(f"Total records processed successfully: {len(final_records)}")
                
        except Exception as e:
            print(f"Error in process_all_records: {str(e)}")

if __name__ == "__main__":
    processor = Med42Processor()
    # processor.process_single_patient(1)
    # processor.process_all_records()
    processor.process_all_records(start_id=1000, end_id=368)


