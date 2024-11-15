# import requests

# url = "http://localhost:8088/predict"
# data = {
#     "user_info": "Age: 35\nGender: Female\nMedical History: No significant past medical issues\nHeight: 5'6\" (168 cm)\nWeight: 140 lbs (63.5 kg)\nAllergies: None known\nCurrent Medications: None",
#     "symptoms": "- Severe headache for the past 3 days\n- Sensitivity to light and sound\n- Nausea and vomiting (twice yesterday)\n- Blurred vision in the right eye, started about 24 hours ago\n- Dizziness when standing up quickly\n- Slight neck stiffness",
#     "report_template": "## Comprehensive Diagnostic Report\n## 1. Initial Impression\n[...]"
# }

# response = requests.post(url, json=data)

# print("Status Code:", response.status_code)
# print("Response Text:", response.text)

# try:
#     print("JSON Response:", response.json())
# except requests.JSONDecodeError:
#     print("Response is not in JSON format.")

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import json

def create_session_with_retries():
    """Create a session with retry strategy"""
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[408, 429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def test_medical_endpoint():
    # Configuration
    url = "http://localhost:8088/predict"  # Changed from 0.0.0.0 to localhost
    
    # Test data
    data = {
        "user_info": """Age: 35
Gender: Female
Medical History: No significant past medical issues
Height: 5'6" (168 cm)
Weight: 140 lbs (63.5 kg)
Allergies: None known
Current Medications: None""",
        
        "symptoms": """- Severe headache for the past 3 days
- Sensitivity to light and sound
- Nausea and vomiting (twice yesterday)
- Blurred vision in the right eye, started about 24 hours ago
- Dizziness when standing up quickly
- Slight neck stiffness""",
        
        "report_template": """# Comprehensive Diagnostic Report

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
[Provide a concise summary of likely diagnosis, key next steps, and important patient instructions]"""
    }
    
    # Create session with retry logic
    session = create_session_with_retries()
    
    print("Testing Medical Diagnosis Endpoint")
    print(f"URL: {url}")
    print("\nSending request with following data structure:")
    print(f"- User Info Length: {len(data['user_info'])} characters")
    print(f"- Symptoms Length: {len(data['symptoms'])} characters")
    print(f"- Template Length: {len(data['report_template'])} characters")
    
    try:
        # Wait briefly for server readiness
        time.sleep(2)
        
        # Send request with timeout
        print("\nSending request...")
        response = session.post(url, json=data, timeout=180)  # 3-minute timeout
        
        # Print response details
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                print("\nSuccessful Response:")
                print(json.dumps(json_response, indent=2))
                return json_response
            except json.JSONDecodeError:
                print("\nWarning: Response is not JSON format")
                print("Raw Response Text:")
                print(response.text[:1000] + "..." if len(response.text) > 1000 else response.text)
        else:
            print(f"\nError Response (Status {response.status_code}):")
            print(response.text)
            
    except requests.exceptions.ConnectionError as e:
        print("\nConnection Error!")
        print("Make sure the server is running and accessible at", url)
        print("Error details:", str(e))
    except requests.exceptions.Timeout as e:
        print("\nRequest Timeout!")
        print("The server took too long to respond (timeout: 180 seconds)")
        print("Error details:", str(e))
    except Exception as e:
        print("\nUnexpected Error!")
        print("Error type:", type(e).__name__)
        print("Error details:", str(e))
        raise

if __name__ == "__main__":
    test_medical_endpoint()