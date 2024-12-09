# data_pipeline/dags/query_vectorstore.py

'''
The file defines a VectorStore class for generating and searching embeddings in Qdrant.
'''

from qdrant_client import QdrantClient
from transformers import BertTokenizer, BertModel
import sys
import os

import sys
from pathlib import Path
current_file = Path(__file__).resolve()
project_dir = current_file.parent.parent
sys.path.append(str(project_dir))

from constants import QDRANT_COLLECTION, QDRANT_PORT, VECTORSTORE_IP, EMBEDDING_MODEL_PATH,SERVICE_ACCOUNT_FILEPATH
from create_embedding import embed
import torch
import os
from add_to_vectorstore import get_qdrant_instance_ip
from logger import logger

class VectorStore():
    def __new__(cls, *args, **kw):
         if not hasattr(cls, '_instance'):
             orig = super(VectorStore, cls)
             cls._instance = orig.__new__(cls, *args, **kw)
         return cls._instance
    
    def __init__(self):
        # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILEPATH
        self.client = QdrantClient(host=get_qdrant_instance_ip(), port=QDRANT_PORT)
        self.collection_name = QDRANT_COLLECTION
        self.pretrained_model_str = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"
        self.tokenizer = BertTokenizer.from_pretrained(self.pretrained_model_str)
        self.model = BertModel.from_pretrained(self.pretrained_model_str)

    def get_relevant_records(self, query: str, top_k: int = 3, device="cpu"):
        if not self.validate_collection():
            return []
        
        # Generate the query embedding
        query_embedding = embed(query, self.tokenizer, self.model, device=device)
        logger.info("Query embedding generated successfully.")
        
        query_embedding = query_embedding.flatten().tolist()
        logger.info("Embedding flattened.")

        # Perform the search
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k
        )
        logger.info(f"Search completed. Number of results: {len(search_results)}")
        logger.info(f"Search results: {search_results}")
        return search_results

    def validate_collection(self) -> bool:
        try:
            if self.client.collection_exists(collection_name=self.collection_name):
                logger.info(f"Qdrant collection {self.collection_name} exists")
                return True
        except Exception as e:
            logger.info(f"Error checking collection existence: {e}")
        logger.log_warning(f"Qdrant Collection '{self.collection_name}' doesn't exist.")
        return False


vector_store = VectorStore()

