from qdrant_client import QdrantClient
from transformers import BertTokenizer, BertModel
from constants import QDRANT_COLLECTION, QDRANT_PORT, VECTORSTORE_IP, EMBEDDING_MODEL_PATH,SERVICE_ACCOUNT_FILEPATH
from create_embedding import embed
import torch
import numpy as np
import os
from add_to_vectorstore import get_qdrant_instance_ip

def get_relevant_points(query, tokenizer, model, client, collection_name, top_k=5, device='cpu'):
    """
    Finds the top_k most similar points to a query string in Qdrant.

    Args:
        query (str): The query string to search for.
        tokenizer (transformers.BertTokenizer): The tokenizer to use for the query.
        model (transformers.BertModel): The model to use for the query.
        client (qdrant_client.QdrantClient): The Qdrant client to use for the query.
        collection_name (str): The name of the collection to query.
        top_k (int): The number of most similar points to return.
        device (str): The device to use for the query.

    Returns:
        A list of qdrant_client.ScoredPoint objects representing the search results.
    """
    try:
        if client.collection_exists(collection_name=collection_name):
            print(f"Qdrant collection {collection_name} exists")
    except Exception:
        print(f"Qdrant Collection '{collection_name}' doesn't exist.")
        return None

    # Ensure the embedding is a flat list of floats
    query_embedding = embed(query, tokenizer, model, device=device)
    print("Query embedding is done ")
    query_embedding = query_embedding.flatten().tolist()  # Flatten and convert to list of floats
    print("Flatten embedding is done ")

    search_results = client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        limit=top_k
    )
    print("Search is done, length ", len(search_results))
    return search_results

if __name__ == '__main__':
    port = QDRANT_PORT
    ip = get_qdrant_instance_ip()
    client = QdrantClient(host=ip, port=port)
    collection_name = QDRANT_COLLECTION
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILEPATH
    # Load a pre-trained transformer model (e.g., Sentence-BERT) for embeddings
    tokenizer = BertTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
    model = BertModel.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
    
    # Example Usage
    query = "What are the symptoms of hemophilia?" 
    results = get_relevant_points(query, tokenizer, model, client, collection_name, top_k=3)

    # Display results
    if results is not None:
        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(f"ID: {result.id}, Score: {result.score}, Payload: {result.payload}")
    else:
        print("No results retrieved")