import unittest
from unittest.mock import patch, MagicMock
import re
from rag.preprocess_dataset import (
    get_section_names, segment_by_sections, remove_irrelevant_information,
    replace_blanks, numbers_to_array, ordered_list_to_string, sex,
    discharge_condition, preprocess, flatten_dict, chunk_json_string,
    transform_text
)


class TestPreprocessDataset(unittest.TestCase):

    def test_get_section_names(self):
        dataset = ["<SEX> M <ALLERGIES> None <SOCIAL HISTORY> Smoker <ATTENDING> Dr. Smith"]
        expected_sections = ['ALLERGIES', 'SEX']
        result = get_section_names(dataset)
        self.assertEqual(sorted(result), sorted(expected_sections))

    def test_segment_by_sections(self):
        text = "<SEX> F <CHIEF COMPLAINT> Chest pain <MEDICAL HISTORY> Asthma"
        section_names = ["SEX", "CHIEF COMPLAINT", "MEDICAL HISTORY"]
        expected_output = {
            "SEX": "F",
            "CHIEF COMPLAINT": "Chest pain",
            "MEDICAL HISTORY": "Asthma"
        }
        result = segment_by_sections(text, section_names)
        self.assertEqual(result, expected_output)

    def test_remove_irrelevant_information(self):
        text = "Patient has SOB. <SEX> F <AGE> 45"
        with patch('preprocess_dataset.ABBREVIATIONS', {'SOB': 'shortness of breath'}):
            result = remove_irrelevant_information(text)
            expected_text = "Patient has shortness of breath. <SEX> F <AGE> 45"
            self.assertEqual(result, expected_text)

    def test_replace_blanks(self):
        text = "Patient has _____ symptoms."
        result = replace_blanks(text)
        expected_text = "Patient has symptoms."
        self.assertEqual(result, expected_text)

    def test_numbers_to_array(self):
        text = "1. Hypertension 2. Diabetes"
        expected_output = (["Hypertension", "Diabetes"], False)
        result, no_numbers = numbers_to_array(text)
        self.assertEqual((result, no_numbers), expected_output)

    def test_ordered_list_to_string(self):
        text = "1. Take medication 2. Visit doctor"
        expected_output = "['Take medication', 'Visit doctor']"
        result = ordered_list_to_string(text)
        self.assertEqual(result, expected_output)

    def test_sex(self):
        self.assertEqual(sex("F"), "female")
        self.assertEqual(sex("M"), "male")

    def test_discharge_condition(self):
        text = "Mental Status: Clear Level of Consciousness: Alert Activity Status: Ambulatory"
        expected_output = {
            "Mental Status": "Clear",
            "Level of Consciousness": "Alert",
            "Activity Status": "Ambulatory"
        }
        result = discharge_condition(text)
        self.assertEqual(result, expected_output)

    def test_flatten_dict(self):
        nested_dict = {"section1": {"sub1": "value1"}, "section2": "value2"}
        expected_output = {"section1.sub1": "value1", "section2": "value2"}
        result = flatten_dict(nested_dict)
        self.assertEqual(result, expected_output)

    def test_chunk_json_string(self):
        flattened_data = {"section1": "value1", "section2": "value2"}
        max_chunk_size = 50  # Size limit for testing purposes
        result = chunk_json_string(flattened_data, max_chunk_size)
        self.assertTrue(len(result) > 0)
        for chunk in result:
            self.assertTrue(len(chunk) <= max_chunk_size)

    @patch('preprocess_dataset.remove_irrelevant_information')
    @patch('preprocess_dataset.segment_by_sections')
    def test_preprocess(self, mock_segment_by_sections, mock_remove_irrelevant_information):
        mock_remove_irrelevant_information.return_value = "processed text"
        mock_segment_by_sections.return_value = {"SEX": "F", "DISCHARGE INSTRUCTIONS": "Follow up"}
        section_names = ["SEX", "DISCHARGE INSTRUCTIONS"]

        result = preprocess("sample text", section_names)

        expected_output = {
            "SEX": "female",
            "DISCHARGE INSTRUCTIONS": "Follow up"
        }
        self.assertEqual(result, expected_output)
        mock_remove_irrelevant_information.assert_called_once()
        mock_segment_by_sections.assert_called_once_with("processed text", section_names)

    @patch('preprocess_dataset.preprocess')
    def test_transform_text(self, mock_preprocess):
        mock_preprocess.return_value = {"SEX": "F", "CHIEF COMPLAINT": "Headache"}
        section_names = {"SEX", "CHIEF COMPLAINT"}

        result = transform_text("sample text", section_names, chunk_size=50)

        self.assertTrue(len(result) > 0)
        for chunk in result:
            self.assertTrue(len(chunk) <= 50)
        mock_preprocess.assert_called_once_with("sample text", section_names)


if __name__ == '__main__':
    unittest.main()
