from qdrant_client import QdrantClient
from transformers import BertTokenizer, BertModel
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
gparent = os.path.dirname(os.path.dirname(current))

sys.path.append(gparent)
from data_pipeline.dags.constants import QDRANT_COLLECTION, QDRANT_PORT, VECTORSTORE_IP, EMBEDDING_MODEL_PATH,SERVICE_ACCOUNT_FILEPATH
from data_pipeline.dags.create_embedding import embed
import torch
import os
from add_to_vectorstore import get_qdrant_instance_ip
from airflow.utils.log.logging_mixin import LoggingMixin


class VectorStore(LoggingMixin):
    def __init__(self):
        self.client = QdrantClient(host=get_qdrant_instance_ip(), port=QDRANT_PORT)
        self.collection_name = QDRANT_COLLECTION
        self.pretrained_model_str = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"
        self.tokenizer = BertTokenizer.from_pretrained(self.pretrained_model_str)
        self.model = BertModel.from_pretrained(self.pretrained_model_str)

    def get_relevant_records(self, query: str, top_k: int = 3):
        if not self.validate_collection():
            return []
        
        # Generate the query embedding
        query_embedding = embed(query, self.tokenizer, self.model, device="cpu")
        self.log.info("Query embedding generated successfully.")
        
        query_embedding = query_embedding.flatten().tolist()
        self.log.info("Embedding flattened.")

        # Perform the search
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k
        )
        self.log.info(f"Search completed. Number of results: {len(search_results)}")
        self.log.info(f"Search results: {search_results}")
        return search_results

    def validate_collection(self) -> bool:
        try:
            if self.client.collection_exists(collection_name=self.collection_name):
                self.log.info(f"Qdrant collection {self.collection_name} exists")
                return True
        except Exception as e:
            self.log.error(f"Error checking collection existence: {e}")
        self.log.warning(f"Qdrant Collection '{self.collection_name}' doesn't exist.")
        return False


vector_store = VectorStore()


def get_relevant_points(query, tokenizer, model, client, collection_name, top_k=5, device='cpu'):
    """
    Finds the top_k most similar points to a query string in Qdrant.
    """
    try:
        if client.collection_exists(collection_name=collection_name):
            print(f"Qdrant collection {collection_name} exists")
        else:
            print(f"Qdrant Collection '{collection_name}' doesn't exist.")
            return None

        # Generate query embedding
        query_embedding = embed(query, tokenizer, model, device=device)
        print("Query embedding generated successfully.")

        # Flatten and convert to list of floats
        query_embedding = query_embedding.flatten().tolist()
        print("Embedding flattened.")

        # Search in Qdrant
        search_results = client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=top_k
        )
        print(f"Search completed. Number of results: {len(search_results)}")
        return search_results

    except Exception as e:
        print(f"Error during query processing: {e}")
        return None


if __name__ == '__main__':
    port = QDRANT_PORT
    ip = get_qdrant_instance_ip()
    client = QdrantClient(host=ip, port=port)
    collection_name = QDRANT_COLLECTION

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILEPATH

    tokenizer = BertTokenizer.from_pretrained(
        "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
    model = BertModel.from_pretrained(
        "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")

    query = "Patient Information: \n Age: 26 \n Gender: Female \n Medical History: No significant past \n medical issues Allergies: None known \n Current Medications: None \n Reported Symptoms: - Migraine - Cough - Chest Tightness - Rash"
    results = get_relevant_points(
        query, tokenizer, model, client, collection_name, top_k=3)

    if results is not None:
        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(f"ID: {result.id}, Score: {result.score}, Payload: {result.payload}")
    else:
        print("No results retrieved")
