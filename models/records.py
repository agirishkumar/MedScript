import os
from google.cloud import storage
import json

# Get the existing path from the environment variable
env_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Append the filename if the path is a directory
if os.path.isdir(env_credentials_path):
    full_credentials_path = os.path.join(env_credentials_path, "medscript-sa.json")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = full_credentials_path

# Initialize the client
client = storage.Client()

# Define your bucket name and file name
bucket_name = 'dataset-records'
file_name = 'records.json'

# Get the bucket and blob (file) from GCS
bucket = client.get_bucket(bucket_name)
blob = bucket.blob(file_name)

# Download the file's content as a string
file_content = blob.download_as_text()

# Parse the JSON content
records = json.loads(file_content)

# Sample two records from the dataset
sampled_records = records[:2]

# Print the sampled records
print(json.dumps(sampled_records, indent=2))
