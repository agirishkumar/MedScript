import re

from exceptiongroup import catch
from google.oauth2 import service_account
from constants import ABBREVIATIONS, SECTION_NAMES, MIMIC_DATASET_BUCKET_NAME, SERVICE_ACCOUNT_FILEPATH

import pandas as pd
import json
from io import StringIO
from google.cloud import storage
import os
# from rag.logging import data_logger

MAX_CHUNK_SIZE = 2500  # Define the number of keys per chunk

def get_section_names(dataset):
    """
    Extracts section names from a dataset
    Removes SOCIAL HISTORY and ATTENDING sections
    Args:
        dataset (list): list of strings

    Returns:
        list: list of section names
    """
    section_names = set()
    for text in dataset:
        names = re.findall("<([\w{2,}\s]+)>", text)
        section_names.update(names)
    
    # try:
    section_names.remove('ATTENDING')
    section_names.remove('SOCIAL HISTORY')
    # except KeyError as e:
        # data_logger.warning(f"Section not found for removal: {e}")

    
    section_names = list(section_names)
    section_names = [tag.upper() for tag in section_names]
    section_names.sort()
    return section_names

def segment_by_sections(text, section_names):
    """
    Segments a medical record into structured sections for easier processing and retrieval.
    """
    sections = {name: "None" for name in section_names}

    for tag in sections.keys():
        # try:
        pattern = f"<{tag.upper().replace('_', ' ')}> (.+?)(?=\s*<|$)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            sections[tag] = match.group(1).strip()
        # except Exception as e:
            # data_logger.warning(f"Could not segment medical record {tag}: {e}")

    return sections

def remove_irrelevant_information(text):
    """
    Removes placeholders and standardizes common abbreviations.
    """
    # text = re.sub(r'<[A-Z_]+>', '', text)  # Remove placeholders like <___>
    # try:
    for k, v in ABBREVIATIONS.items():
        text = text.replace(k, v)
    return text
    # except Exception as e:
        # data_logger.warning(f"Could not remove irrelevant information: {e}")

def replace_blanks(text):
    # print("Replace Blanks type: ", type(text))
    # print(text)
    # try:
    if text is not None:
        text = re.sub(r"_+", "", text)
        text = text.strip()
    return text
    # except Exception as e:
    #     data_logger.warning(f"Could not remove blanks: {e}")


def numbers_to_array(text):
    reg = r"\d+\.\s"
    text = re.split(reg, text)

    # if no numbers detected retain the text
    if len(text) == 1:
        text = text[0]
        no_numbers = True
    else:
        text = text[1:]
        text = [t.strip() for t in text]
        no_numbers = False

    text = str(text) #f"{text}"


    return text, no_numbers

def ordered_list_to_string(text):
    text, no_numbers = numbers_to_array(text)
    if no_numbers:
        reg = r"\s\-\s"
        text = re.split(reg, text)
        text[0] = re.sub(r"-\s", "", text[0])
        text = str(text)
    # data_logger.debug("Ordered list converted to string")

    return text


def sex(text):
    # print("Sex type: ", type(text))
    # print(text)
    if text.lower() == 'f':
        text = 'female'
    elif text.lower() == 'm':
        text = 'male'
    return text

def discharge_condition(text):
    # print("discharge_condition: ", type(text))
    # print(text)
    if text is None: return None
    reg = r"Mental Status: |Level of Consciousness: |Activity Status: "

    tmp = re.split(reg, text)

    if len(tmp) != 4:
        return text
    else:
        text = tmp[1:]
        text = dict(zip(["Mental Status", "Level of Consciousness", "Activity Status"], [t.strip() for t in text]))
        return text

def no_change(text):
    return text

def preprocess(text, section_names):
    text = remove_irrelevant_information(text)

    sections = segment_by_sections(text, section_names)

    # print("\n-------------------------------- Section --------------------------------")
    # print(sections)
    function_dict = {
        "DISCHARGE INSTRUCTIONS": [no_change],
        "PERTINENT RESULTS": [replace_blanks],
        "CHIEF COMPLAINT": [replace_blanks],
        "SERVICE": [replace_blanks],
        "MAJOR SURGICAL OR INVASIVE PROCEDURE": [replace_blanks],
        "FAMILY HISTORY": [replace_blanks],
        "MEDICATIONS ON ADMISSION": [ordered_list_to_string, replace_blanks],
        "HISTORY OF PRESENT ILLNESS": [no_change, replace_blanks],
        "PHYSICAL EXAM": [no_change, replace_blanks],
        "DISCHARGE MEDICATIONS": [replace_blanks, ordered_list_to_string],
        "FOLLOWUP INSTRUCTIONS": [replace_blanks],
        "DISCHARGE DISPOSITION": [replace_blanks],
        "DISCHARGE CONDITION": [replace_blanks, discharge_condition],
        "ALLERGIES": [replace_blanks],
        "DISCHARGE DIAGNOSIS": [replace_blanks],
        "SEX": [sex],
        "PAST MEDICAL HISTORY": [replace_blanks, ordered_list_to_string]
    }

    output_dict = {}

    for section_name, section_value in sections.items():
        # try:
            # print(f"____{section_name}______")
        if section_name in function_dict:
            result = section_value
            for func in function_dict[section_name]:
                result = func(result)
            output_dict[section_name] = result

            if section_name == "FOLLOWUP INSTRUCTIONS" and len(result)==0:
                output_dict[section_name] = "None"
            # output_dict[section_name] = function_dict[section_name](section_value)
        else:
            output_dict[section_name] = 'Function not defined'
        # except Exception as e:
        #     data_logger.warning(f"Could not preprocess {section_name}: {e}")

    return output_dict

def flatten_dict(d, parent_key='', sep='.'):
    """
    Flatten a nested dictionary.
    """
    items = []
    for k, v in d.items():
        # try:
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
        # except Exception as e:
        #     data_logger.warning(f"Could not flatten {k}: {e}")
    return dict(items)

def chunk_json_string(flattened_data, max_chunk_size):
    """
    Chunk the flattened dictionary into JSON string chunks, each within max_chunk_size limit.
    """
    chunks = []
    current_chunk = {}
    current_chunk_size = 0

    # Go through each key-value pair in the flattened dictionary
    for key, value in flattened_data.items():
        # Prepare a tentative chunk with the new key-value pair added
        tentative_chunk = current_chunk.copy()
        tentative_chunk[key] = value
        
        # Convert tentative chunk to JSON string to check its size
        tentative_chunk_string = json.dumps(tentative_chunk)
        tentative_chunk_size = len(tentative_chunk_string)

        # Check if adding this key-value pair exceeds the max chunk size
        if tentative_chunk_size > max_chunk_size:
            # If it exceeds, finalize the current chunk and start a new one
            chunks.append(json.dumps(current_chunk))
            current_chunk = {key: value}  # Start new chunk with the current pair
            current_chunk_size = len(json.dumps(current_chunk))
        else:
            # If it doesn't exceed, update current chunk and size
            current_chunk[key] = value
            current_chunk_size = tentative_chunk_size

    # Add the final chunk
    if current_chunk:
        chunks.append(json.dumps(current_chunk))

    return chunks

def transform_text(text, section_names, chunk_size=MAX_CHUNK_SIZE):
    """
    Preprocess the text, flattens dictionary and converts it into chunks
    Args:
        text (string): Medical Input
        section_names (set): Names of tags in the input
        chunk_size (int, optional): Defaults to MAX_CHUNK_SIZE.

    Returns:
        list: List of chunks
    """
    preprocessed_text = preprocess(text, section_names)
    flattened_data = flatten_dict(preprocessed_text)

    chunks = chunk_json_string(flattened_data, chunk_size)
    return chunks

if __name__ == '__main__':

    section_names = SECTION_NAMES

    local_processed_data_path = '../datasets/'
    processed_dataset_filename = 'preprocessed_dataset.csv'
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILEPATH

    # SERVICE_KEY_FILE = "D:/Rohan/Northeastern/Courses/MLOPS/GCP Service Keys/medscript-437117-e1e48d1242ef.json"
    CREDENTIALS = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILEPATH)

    storage_client = storage.Client(credentials=CREDENTIALS, project=CREDENTIALS.project_id)

    bucket = storage_client.get_bucket(MIMIC_DATASET_BUCKET_NAME)

    download_blob = bucket.blob('raw_data/mimic4-dataset.csv')
    data = download_blob.download_as_text()

    # Load the data into a DataFrame
    data_io = StringIO(data)

    df = pd.read_csv(data_io, encoding='utf-8', engine='python', on_bad_lines='warn')
    
    print("Succcessfully read dataset from bucket")

    df.drop('target', axis='columns', inplace=True)

    # df.to_csv('datasets/original.csv', index=False)
    # df = pd.read_csv('datasets/original.csv')

    df['input'] = df['input'].apply(lambda x: transform_text(x, section_names, MAX_CHUNK_SIZE))

    print("Succcessfully transformed dataset")

    df.to_csv(local_processed_data_path+processed_dataset_filename, index=False)
    
    print("Saved transformed dataset")

    upload_blob = bucket.blob('processed_data/' + processed_dataset_filename)

    upload_blob.upload_from_filename(local_processed_data_path+processed_dataset_filename)

    print("Uploaded transformed dataset to bucket")

    os.remove(local_processed_data_path+processed_dataset_filename)
    print("Deleted transformed dataset from local system")