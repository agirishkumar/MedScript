import requests

url = "http://0.0.0.0:8081/predict"
data = {
    "user_info": "Age: 35\nGender: Female\nMedical History: No significant past medical issues\nHeight: 5'6\" (168 cm)\nWeight: 140 lbs (63.5 kg)\nAllergies: None known\nCurrent Medications: None",
    "symptoms": "- Severe headache for the past 3 days\n- Sensitivity to light and sound\n- Nausea and vomiting (twice yesterday)\n- Blurred vision in the right eye, started about 24 hours ago\n- Dizziness when standing up quickly\n- Slight neck stiffness",
    "report_template": "## Comprehensive Diagnostic Report\n## 1. Initial Impression\n[...]"
}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response Text:", response.text)

try:
    print("JSON Response:", response.json())
except requests.JSONDecodeError:
    print("Response is not in JSON format.")
