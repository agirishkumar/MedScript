from qdrant_client import QdrantClient, models
import pandas as pd
from constants import MIMIC_DATASET_BUCKET_NAME, QDRANT_COLLECTION, QDRANT_PORT, EMBEDDING_SIZE, VECTORSTORE_IP, SERVICE_ACCOUNT_FILEPATH
import pandas as pd
from io import StringIO
from google.cloud import storage
import os
import ast

def add_to_vectordb(df, client, collection_name=QDRANT_COLLECTION):

    df['input'] = df['input'].apply(lambda x: ast.literal_eval(x))
    df['embedding'] = df['embedding'].apply(lambda x: ast.literal_eval(x))

    ind = 0
    points = []

    for i in range(0, len(df)):

        for j in range(len(df.iloc[i]['embedding'])):
            point = models.PointStruct(
                id = ind, vector = df.iloc[i]['embedding'][j], 
                payload = {"note_id": df.iloc[i]['note_id'], "input": df.iloc[i]['input'][j]}
            )

            ind += 1
            points.append(point)
         
    #Upload to Qdrant
    client.upsert(collection_name=collection_name, points=points)

if __name__ == '__main__':
    ip = "34.134.169.70" #VECTORSTORE_IP
    client = QdrantClient(host=ip, port=QDRANT_PORT)
    collection_name = QDRANT_COLLECTION

    try:
        if client.get_collection(collection_name):
            print(f"Qdrant Collection '{collection_name}' already exists.")
    except Exception:
        print(f"Qdrant Collection '{collection_name}' doesnt exists. Creating it...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=EMBEDDING_SIZE, distance=models.Distance.COSINE)
        )
        print(f"Qdrant Collection '{collection_name}' created successfully.")


    print("Successfully connected to Qdrant Vectorstore")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILEPATH

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(MIMIC_DATASET_BUCKET_NAME)

    download_blob = bucket.blob('processed_data/tmp_embeddings.csv')
    data = download_blob.download_as_text()
    data_io = StringIO(data)
    df = pd.read_csv(data_io) 

    print("Downloaded Embeddings to local from bucket")

    add_to_vectordb(df, client, collection_name)

    print("Added Embeddings to VectorStore")
