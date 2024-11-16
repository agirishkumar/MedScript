# data_pipeline/dags/add_to_vectorstore.py

'''
Uploads embeddings from Google Cloud Storage to Qdrant with batch processing and retry logic.
'''

from googleapiclient import discovery
from google.oauth2 import service_account
from qdrant_client import QdrantClient, models
import pandas as pd
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
gparent = os.path.dirname(os.path.dirname(current))

sys.path.append(gparent)
from data_pipeline.dags.constants import (
    MIMIC_DATASET_BUCKET_NAME, 
    QDRANT_COLLECTION, 
    QDRANT_PORT, 
    EMBEDDING_SIZE,
    SERVICE_ACCOUNT_FILEPATH,
    PROJECT_ID,
    QDRANT_INSTANCE_NAME,
    QDRANT_INSTANCE_ZONE
)
from google.cloud import storage

import ast
from google.cloud import storage
from typing import List
import time
from tqdm import tqdm
from io import StringIO

def chunk_points(points: List[models.PointStruct], chunk_size: int = 100):
    """Split points into smaller chunks for batch processing."""
    for i in range(0, len(points), chunk_size):
        yield points[i:i + chunk_size]

def add_to_vectordb(df: pd.DataFrame, 
                   client: QdrantClient, 
                   collection_name: str = QDRANT_COLLECTION,
                   chunk_size: int = 100,
                   max_retries: int = 3,
                   retry_delay: float = 1.0):
    """
    Add vectors to Qdrant with batch processing and retry logic.
    """

    df['input'] = df['input'].apply(ast.literal_eval)
    df['embedding'] = df['embedding'].apply(ast.literal_eval)
    print("Converted Input and Embedding to List from String")

    points = []
    ind = 0
    
    # Prepare all points silently
    for i in range(len(df)):
        embeddings = df.iloc[i]['embedding']
        if isinstance(embeddings[0], float):
            embeddings = [embeddings]
            
        for j in range(len(embeddings)):
            if isinstance(embeddings[j], list):
                point = models.PointStruct(
                    id=ind,
                    vector=embeddings[j],
                    payload={
                        "note_id": df.iloc[i]['note_id'],
                        "input": df.iloc[i]['input'][j]
                    }
                )
                points.append(point)
                ind += 1
    print("Created VectorStore Points for Insertion")

    # Process points in chunks with minimal logging
    total_chunks = (len(points) + chunk_size - 1) // chunk_size
    with tqdm(total=total_chunks, desc="Uploading vectors") as pbar:
        for chunk in chunk_points(points, chunk_size):
            retries = 0
            while retries < max_retries:
                try:
                    client.upsert(
                        collection_name=collection_name,
                        points=chunk
                    )
                    break
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        raise Exception(f"Upload failed after {max_retries} attempts")
                    time.sleep(retry_delay * retries)
            pbar.update(1)
    print("Successfully uploaded VectorStore Points")

def setup_qdrant_collection(client: QdrantClient, collection_name: str):
    """Set up Qdrant collection with minimal logging."""
    try:
        client.get_collection(collection_name)
        print(f"'{collection_name}' collection exists.")
    except Exception:
        print(f"Collection '{collection_name}' doesnt exist")
        print(f"Creating collection '{collection_name}'...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=EMBEDDING_SIZE, 
                distance=models.Distance.COSINE
            )
        )

def update_to_vectordb(qdrant_host): 
    # Qdrant connection settings
    QDRANT_HOST = qdrant_host
    
    # Initialize Qdrant client
    client = QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_PORT,
        timeout=60
    )
    
    # Setup collection silently
    setup_qdrant_collection(client, QDRANT_COLLECTION)
    print("Connected to collection: ", QDRANT_COLLECTION)

    # Set up Google Cloud credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILEPATH
    storage_client = storage.Client()
    
    # Download data from Google Cloud Storage
    bucket = storage_client.get_bucket(MIMIC_DATASET_BUCKET_NAME)
    blob = bucket.blob('processed_data/embeddings_100/embed_df_10k.csv')
    data = blob.download_as_text()
    data_io = StringIO(data)
    df = pd.read_csv(data_io) 
    print("Downloaded embeddings from bucket to insert into vectorstore")
    
    # df = pd.read_csv(blob.download_as_text())
    
    # Upload to Qdrant
    add_to_vectordb(
        df,
        client,
        QDRANT_COLLECTION,
        chunk_size=100,
        max_retries=3,
        retry_delay=1.0
    )
    print("Uploaded Vector Points to VectorStore")

def get_qdrant_instance_ip():
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILEPATH)
    compute = discovery.build('compute', 'v1', credentials=credentials)
    instance = compute.instances().get(project=PROJECT_ID, zone=QDRANT_INSTANCE_ZONE, instance=QDRANT_INSTANCE_NAME).execute()
    ip_address = instance['networkInterfaces'][0]['accessConfigs'][0]['natIP']
    print(f"Instance IP: {ip_address}")
    return ip_address

if __name__ == '__main__':
    update_to_vectordb(qdrant_host=get_qdrant_instance_ip())