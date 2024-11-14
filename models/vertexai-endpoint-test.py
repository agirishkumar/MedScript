import os
from google.cloud import aiplatform
from google.oauth2 import service_account
import json
import requests
from google.auth.transport.requests import Request

# Set path to service account JSON
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sa_path = "../data_pipeline/secrets/medscript-sa.json"

def test_endpoint_raw():
    """Test endpoint using raw REST API"""
    print("\nTesting endpoint using raw REST API...")
    
    try:
        # Get credentials and token
        credentials = service_account.Credentials.from_service_account_file(
            sa_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(Request())
        
        # API endpoint URL
        url = "https://us-east4-aiplatform.googleapis.com/v1/projects/946534278700/locations/us-east4/endpoints/3236139797474967552:predict"
        
        # Headers
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

        medical_case = """Given the following patient information, provide a detailed diagnosis and treatment plan:

[Patient Information]
Gender: Female
Chief Complaint: Worsening ABD distension and pain
History of Present Illness: HCV cirrhosis casebook with ascites, HIV on ART, history of IVDU, COPD, bipolar, PTSD. Patient presented from OSH ED with worsening abd distension over past week. Self-discontinued lasix and spironolactone. Labs show Tbili1.6, WBC 5K, platelet 77, INR 1.6.

Past Medical History: 
- HCV Cirrhosis
- HIV on ART
- COPD
- Bipolar disorder and PTSD
- History of cocaine and heroin use

Current Symptoms:
- Worsening abdominal distension and discomfort
- Gum bleeding
- Brief periods of confusion
- No edema, SOB, or orthopnea

Required Analysis:
1. Most likely diagnosis:
2. Differential diagnoses:
3. Recommended treatment plan:"""
        

        # Try different input formats
        payloads = [
            # Format 1: Simple inputs
            {
                "instances": [{"inputs": medical_case}]
            },
            # Format 2: Text format
            {
                "instances": [{"text": medical_case}]
            },
            # Format 3: Prompt format
            {
                "instances": [{
                    "prompt": medical_case,
                    "max_tokens": 1000,
                    "temperature": 0.7
                }]
            }
        ]
        
        # Try each payload format
        for i, payload in enumerate(payloads, 1):
            # print(f"\nTrying payload format {i}...")
            # print(f"Request Headers: {json.dumps(headers, indent=2)}")
            # print(f"Request Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, headers=headers, json=payload)
            
            print(f"\nResponse Status Code: {response.status_code}")
            # print(f"Response Headers: {dict(response.headers)}")
            print("\nResponse Body:")
            print("=" * 80)
            
            try:
                response_json = response.json()
                print(json.dumps(response_json, indent=2))
                
                # Save response if successful
                if response.status_code == 200:
                    output_file = os.path.join(current_dir, f"prediction_output_format_{i}.txt")
                    with open(output_file, "w") as f:
                        json.dump(response_json, f, indent=2)
                    print(f"\nResponse saved to: {output_file}")
                
            except json.JSONDecodeError:
                print("Raw response text:")
                print(response.text)
            
            print("=" * 80)
            
            if response.status_code == 200:
                print(f"Format {i} successful!")
                break
        
    except Exception as e:
        print(f"Error in raw endpoint test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing Vertex AI endpoint with detailed debugging...")
    test_endpoint_raw()