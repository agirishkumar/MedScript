import pandas as pd
import json
from evaluation import evaluate_metrics
from google.cloud import storage
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
gparent = os.path.dirname(current)

sys.path.append(gparent)
from data_pipeline.dags.constants import DATASET_BUCKET_NAME, SERVICE_ACCOUNT_FILEPATH

def download_json_from_gcs(bucket_name, source_blob_name, destination_file_name):
    """
    Downloads a JSON file from Google Cloud Storage, parses it, and saves it to a local file.

    Args:
        bucket_name (str): The name of the Google Cloud Storage bucket.
        source_blob_name (str): The name of the blob (file) in the bucket.
        destination_file_name (str): The local file path to write the JSON data to.

    Returns:
        dict: The parsed JSON data as a Python dictionary.
    """
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(source_blob_name)

    json_content = blob.download_as_text()

    json_data = json.loads(json_content)
    
    # Save the JSON data to a local file
    with open(destination_file_name, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    
    print(f"Downloaded and saved JSON from gs://{bucket_name}/{source_blob_name} to {destination_file_name}")
    
    # Return the JSON data as a Python dictionary
    return json_data

def json_to_df(json_data):
    # Prepare a list to hold rows for the dataframe
    """
    Converts a list of JSON objects containing diagnosis data into a pandas DataFrame.

    Args:
        json_data (list of dict): List of JSON objects where each object contains
            'diagnosisReport' and 'med42_diagnosis' keys, each having 'Possible Diagnoses'
            which includes 'Primary Diagnosis' and 'Differential Diagnoses'.

    Returns:
        pd.DataFrame: A DataFrame with columns 'true' and 'prediction', where each row
            contains the primary and differential diagnoses from the true and predicted data.
    """
    rows = []
    
    for data in json_data:
        true_diagnosis = data["diagnosisReport"]["Possible Diagnoses"]
        prediction_diagnosis = data["med42_diagnosis"]["Possible Diagnoses"]
        
        row = {
            "true": f"{true_diagnosis['Primary Diagnosis']} - " + ', '.join(true_diagnosis['Differential Diagnoses']),
            "prediction": f"{prediction_diagnosis['Primary Diagnosis']} - " + ', '.join(prediction_diagnosis['Differential Diagnoses'])
        }
        
        rows.append(row)

    df = pd.DataFrame(rows)
    
    return df

def get_validation_metrics(json_data):
    """
    Get evaluation metrics for given JSON data

    Args:
        json_data (list of dict): List of JSON objects containing true and predicted diagnosis

    Returns:
        dict: Dictionary of evaluation metrics
    """
    json_df = json_to_df(json_data)

    eval_scores = evaluate_metrics(json_df['true'], json_df['prediction'])

    with open('models\\validation_evaluation_metrics.txt', 'w') as f:
        json.dump(eval_scores, f)
    
    print("Saved validation evaluation metrics to validation_evaluation_metrics.txt")

    return eval_scores

if __name__ == '__main__':
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILEPATH

    DATA_PATH = "models\\records_with_med42.json"
    SOURCE_BLOB_PATH = 'records_with_med42.json'

    json_data = download_json_from_gcs(DATASET_BUCKET_NAME, SOURCE_BLOB_PATH, DATA_PATH)

    # with open(DATA_PATH, 'r') as f:
    #     json_data = json.load(f)
    
    eval_scores = get_validation_metrics(json_data)

    print("Validation Evaluation Scores\n", eval_scores)

    