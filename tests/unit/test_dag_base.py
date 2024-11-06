import unittest
from unittest.mock import patch, Mock, MagicMock
import requests
from data_pipeline.dags.src.base import *
from data_pipeline.dags.logger import *

class TestGetData(unittest.TestCase):
    def test_get_data_success(self):
        with patch('requests.get') as mock_request, patch("data_pipeline.dags.logger") as mock_logger:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"key": "value"}
            mock_request.return_value = mock_response
            url = "https://api.example.com/data"
            result = get_data(url)

            # Assertions
            mock_request.assert_called_once_with(url)
            self.assertEqual(result, {"key": "value"})
    
    def test_get_data_failure(self):
        with patch('requests.get') as mock_request, patch("data_pipeline.dags.logger") as mock_logger:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_request.return_value = mock_response
            url = "https://api.example.com/data"
            with self.assertRaises(Exception):
                get_data(url)

    def test_get_data_invalid_json(self):
        with patch('requests.get') as mock_request, patch("data_pipeline.dags.logger") as mock_logger:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_request.return_value = mock_response
            url = "https://api.example.com/data"
            with self.assertRaises(ValueError):
                get_data(url)

    def test_get_data_logging(self):
        with patch('requests.get') as mock_request, patch("data_pipeline.dags.logger") as mock_logger:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"key": "value"}
            mock_request.return_value = mock_response
            url = "https://api.example.com/data"
            data = get_data(url)
            self.assertTrue(data["key"] == "value")
                

class TestPreprocessData(unittest.TestCase):
    def test_preprocess_data_success(self):
        input_data = {
            "patient": {
                "FirstName": "Emily",
                "LastName": "King",
                "DateOfBirth": "1998-08-24",
                "Gender": "Female",
                "Address": "505 Walnut St",
                "ContactNumber": "890-123-4567",
                "Email": "emilyking@example.com",
                "Height": 155.0,
                "Weight": 50.0,
                "BloodType": "AB-",
                "PatientID": 9,
                "CreatedAt": "2024-11-02T01:56:45.143993"
            },
            "visits": [{"symptoms": [{'SymptomDescription': "headache"}]}, {"symptoms": [{'SymptomDescription': "nausea"}]}]
        }
       
        expected_output = {
            "User information": "\n            Age: 26\n"
                "            Gender: Female\n"
                "            BloodType: AB-\n"
                "            BMI: 20.811654526534856\n"
                "            Medical History: No significant past medical issues\n"
                "            Allergies: None known\n"
                "            Current Medications: None\n        ",
            "Symptoms": "- headache\n- nausea"
        }
        
        
        with patch("data_pipeline.dags.logger") as mock_logger:
            result = preprocess_data(input_data)
            print(result)
            self.assertEqual(result, expected_output) 
    

class TestGeneratePrompt(unittest.TestCase):
    def test_generate_prompt_valid_input(self):
        query = """
            Patient Information:
            Age: 26
            Gender: Female
            BloodType: AB-
            BMI: 20.81
            Medical History: No significant past medical issues
            Allergies: None known
            Current Medications: None

        Reported Symptoms:
            - Migraine
            - Cough
            - Chest Tightness
            - Rash
        """
    
        result = generate_prompt(query)
        
        assert isinstance(result, str), "Result should be a string"
        assert "Comprehensive Diagnostic Report" in result, "Report template is missing"
        assert query in result, "Input query is not included in the result"

