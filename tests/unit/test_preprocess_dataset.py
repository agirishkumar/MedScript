import unittest
from unittest.mock import patch, MagicMock

from data_pipeline.src.preprocessing.preprocess_dataset import (
    get_section_names, segment_by_sections, remove_irrelevant_information,
    replace_blanks, numbers_to_array, ordered_list_to_string, sex,
    discharge_condition, no_change, preprocess, flatten_dict, chunk_json_string
)

class TestTextProcessingFunctions(unittest.TestCase):

    def test_get_section_names(self):
        dataset = ["<SOCIAL HISTORY> text", "<ATTENDING> info", "<MEDICATIONS> meds info"]
        expected_output = ["MEDICATIONS"]

        result = get_section_names(dataset)
        self.assertEqual(result, expected_output)

    def test_segment_by_sections(self):
        text = "<HISTORY> Details here <DIAGNOSIS> Condition info"
        section_names = ["HISTORY", "DIAGNOSIS"]
        expected_output = {
            "HISTORY": "Details here",
            "DIAGNOSIS": "Condition info"
        }

        result = segment_by_sections(text, section_names)
        self.assertEqual(result, expected_output)

    def test_remove_irrelevant_information(self):
        text = "Patient c/o stomach pain"
        expected_output = "Patient complains of stomach pain"

        result = remove_irrelevant_information(text)
        self.assertEqual(result, expected_output)

    def test_replace_blanks(self):
        text = "Info___with___blanks___"
        expected_output = "Infowithblanks"

        result = replace_blanks(text)
        self.assertEqual(result, expected_output)

    def test_numbers_to_array_with_numbers(self):
        text = "1. First item 2. Second item"
        expected_output = ("['First item', 'Second item']", False)

        result = numbers_to_array(text)
        self.assertEqual(result, expected_output)

    def test_numbers_to_array_no_numbers(self):
        text = "Only text, no numbers here."
        expected_output = ("Only text, no numbers here.", True)

        result = numbers_to_array(text)
        self.assertEqual(result, expected_output)

    def test_ordered_list_to_string_with_numbers(self):
        text = "First item - Second item"
        expected_output = "['First item', 'Second item']"

        result = ordered_list_to_string(text)
        self.assertEqual(result, expected_output)

    def test_sex_female(self):
        text = "f"
        expected_output = "female"

        result = sex(text)
        self.assertEqual(result, expected_output)

    def test_discharge_condition_dict(self):
        text = "Mental Status: Stable Level of Consciousness: Alert Activity Status: Active"
        expected_output = {
            "Mental Status": "Stable",
            "Level of Consciousness": "Alert",
            "Activity Status": "Active"
        }

        result = discharge_condition(text)
        self.assertEqual(result, expected_output)

    def test_no_change(self):
        text = "No change text"
        expected_output = "No change text"

        result = no_change(text)
        self.assertEqual(result, expected_output)

    def test_preprocess(self):
        text = "<DISCHARGE INSTRUCTIONS> Rest and monitor condition"
        section_names = ["DISCHARGE INSTRUCTIONS"]
        expected_output = {
            "DISCHARGE INSTRUCTIONS": "Rest and monitor condition"
        }

        with patch("data_pipeline.src.preprocessing.preprocess_dataset.no_change", return_value="Rest and monitor condition"):
            result = preprocess(text, section_names)
            self.assertEqual(result, expected_output)

    def test_flatten_dict(self):
        nested_dict = {
            "section1": {"sub1": "data1", "sub2": "data2"},
            "section2": "data3"
        }
        expected_output = {
            "section1.sub1": "data1",
            "section1.sub2": "data2",
            "section2": "data3"
        }

        result = flatten_dict(nested_dict)
        self.assertEqual(result, expected_output)

    def test_chunk_json_string(self):
        data = {"section1": "data1", "section2": "data2", "section3": "data3"}
        max_chunk_size = 30
        expected_output = ['{"section1": "data1"}', '{"section2": "data2"}', '{"section3": "data3"}']

        result = chunk_json_string(data, max_chunk_size)
        self.assertEqual(result, expected_output)


if __name__ == "__main__":
    unittest.main()
