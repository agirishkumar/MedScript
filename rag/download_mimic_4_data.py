import subprocess
from google.cloud import storage
import os
import sys
from dotenv import load_dotenv

# # from google.cloud.exceptions import GoogleCloudError
# # Define the path to the parent directory
# parent_directory = os.path.abspath('.')

# # Add the parent directory to sys.path
# sys.path.append(parent_directory)

# from app.core.logging import logger


import time 

load_dotenv()

username = os.getenv("WGET_USERNAME")
password = os.getenv("WGET_PASSWORD")


# command = f"wget -r -N -np --user {username} --password {password} --header='Range: bytes=0-1048576' -O part1.zip https://physionet.org/files/labelled-notes-hospital-course/1.1.0/"
# os.system(command)


# def download_and_upload_to_gcs(dataset_url, bucket_name, destination_blob_name):
#     # Initialize the Google Cloud Storage client
#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(destination_blob_name)

#     # Download the dataset in chunks
#     response = requests.get(dataset_url, stream=True)
#     response.raise_for_status()

#     # Create a resumable upload session
#     upload = blob.create_resumable_upload_session()

#     # Upload the dataset in chunks
#     for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
#         if chunk:
#             upload.transmit_next_chunk(chunk)

#     print(f"Dataset downloaded and uploaded to gs://{bucket_name}/{destination_blob_name}")

def download_dataset(download_url, destination_filename):
    wget_command = f"wget -r -N -np --user {username} --password {password} -O {destination_filename} {download_url}"

    start_time = time.time()

    try:
        result = subprocess.run(wget_command, shell=True, check=True)

        # process_time = time.time() - start_time

        print(f"Dataset downloaded successfully: {destination_filename}")
        # logger.info(f"Dataset downloaded successfully: {destination_filename}")


        # logger.info(f"Successfully downloaded dataset from {download_url}")
        # logger.info(f"Output dataset file: {destination_filename}")
        # logger.info(f"Command output: {result.stdout}")

    except subprocess.CalledProcessError as e:
        
        print(f"Error downloading dataset: {e}")

        # process_time = time.time() - start_time

        # log_dict = {
        #     "returncode": e.returncode,
        #     "output": e.output,
        #     "stderr output": e.stderr,
        #     "process_time": f"{process_time:.2f}s",
        #     "error": str(e)
        # }

        # log_msg = f"Request: {log_dict['method']} {log_dict['path']} | " \
        #             f"Status: {log_dict['status_code']} | " \
        #             f"Process Time: {log_dict['process_time']} | " \
        #             f"Request ID: {log_dict['request_id']} | Error: {log_dict['error']}"


        # log_msg = f"Error downloading dataset: {e}"

        # logger.error(log_msg)
        

def upload_to_bucket(bucket_name, destination_blob_name, source_path, destination_path=""):
    """ Upload data to a bucket"""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_path + destination_blob_name)

    blob.upload_from_filename(source_path)

    # try:
    #     blob.upload_from_filename(source_path)
    #     logger.info(
    #         f"File {source_path} uploaded to {destination_blob_name} in bucket {bucket_name} successfully.")
        
    # except GoogleCloudError as e:
    #     logger.error(f"Failed to upload file {source_path} to GCS bucket {bucket_name}. Error: {e}")
    #     print(f"Dataset uploaded to gs://{bucket_name}/{destination_blob_name}")

    # # Remove the local file
    os.remove(source_path)
    # print(f"Local Dataset removed: {source_path}")


if __name__ == "__main__":
    # # URL of the dataset to download
    dataset_url = "https://physionet.org/files/labelled-notes-hospital-course/1.1.0/mimic-iv-bhc.csv"

    # # Google Cloud Storage bucket name and base filename for storage
    gcs_bucket_name = "medscript-mimic4-dataset"
    base_filename = "mimic4-dataset.csv"
    local_path = os.path.join('datasets', base_filename)


    download_dataset(dataset_url, local_path)
    upload_to_bucket(gcs_bucket_name, base_filename, local_path, 'raw_data/')

    # print(parent_directory)
    # print(sys.path)
    # parent_dir_name = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    # print(parent_dir_name)
    # sys.path.append(parent_dir_name + "app") 
    # import app
    # app.core.logging.logger.info("logged")
