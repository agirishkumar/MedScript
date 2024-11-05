from qdrant_client import QdrantClient
from transformers import BertTokenizer, BertModel
from constants import QDRANT_COLLECTION, QDRANT_PORT, VECTORSTORE_IP, EMBEDDING_MODEL_PATH,SERVICE_ACCOUNT_FILEPATH
from create_embedding import embed
import torch
import numpy as np
import os
import access_vectorstore_instance as avi

# def get_embedding(query, tokenizer, model):
#     inputs = tokenizer(query, return_tensors="pt", truncation=True, padding=True, max_length=512)
#     with torch.no_grad():
#         outputs = model(**inputs)
#     embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
#     return embeddings

def get_relevant_points(query, tokenizer, model, client, collection_name, top_k=5):
    try:
        if client.collection_exists(collection_name=collection_name):
            print(f"Qdrant collection {collection_name} exists")
    except Exception:
        print(f"Qdrant Collection '{collection_name}' doesnt exists.")
        return None
    # try:
    #     if client.get_collection(collection_name):
    #         print(f"Qdrant collection {collection_name} exists")
    # except Exception:
    #     print(f"Qdrant Collection '{collection_name}' doesnt exists.")
    #     return None

    query_embedding = embed(query, tokenizer, model)

    # print(type(query_embedding), "; ", type(query_embedding.tolist()))
    # print(type(query_embedding[0]), "; ", type(query_embedding.tolist()[0]))
    # print(type(query_embedding[0][0]), "; ", type(query_embedding.tolist()[0][0]))
    # print(query_embedding)
    search_results = client.search(
        collection_name=collection_name,
        query_vector=query_embedding.tolist(),
        limit=top_k
    )
    return search_results
    # return None

if __name__ == '__main__':
    port = QDRANT_PORT
    # ip = "34.134.169.70" #VECTORSTORE_IP
    ip = avi.get_vectorstore_ip()#get_vectorstore_ip()
    print(f"IP: {ip}")
    client = QdrantClient(host=ip, port=port)
    collection_name = QDRANT_COLLECTION
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILEPATH
    # Load a pre-trained transformer model (e.g., Sentence-BERT) for embeddings
    tokenizer = BertTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
    model = BertModel.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")

    # model = BertModel.from_pretrained(EMBEDDING_MODEL_PATH)
    # tokenizer = BertTokenizer.from_pretrained(EMBEDDING_MODEL_PATH)

    # try:
    #     if client.get_collection(collection_name):
    #         print(f"Qdrant collection {collection_name} exists")
    # except Exception:
    #     print(f"Qdrant Collection '{collection_name}' doesnt exists.")

    
    # Example Usage
    query = "What are the symptoms of hemophilia?" 
    results = get_relevant_points(query, tokenizer, model, client, collection_name)

    # Display results
    if results is not None:
        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(f"ID: {result.id}, Score: {result.score}, Payload: {result.payload}")
    else:
        print("No results retrieved")