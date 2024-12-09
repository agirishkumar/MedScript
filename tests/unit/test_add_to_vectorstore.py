import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from io import StringIO
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import ast
# from data_pipeline.dags.add_to_vectorstore import chunk_points, add_to_vectordb, setup_qdrant_collection, update_to_vectordb, get_qdrant_instance_ip

class TestVectorStoreFunctions(unittest.TestCase):

    @patch("data_pipeline.dags.add_to_vectorstore.models.PointStruct")
    @patch("data_pipeline.dags.src.credential_helper.get_service_account_path")
    def test_chunk_points(self, MockPointStruct, mockServiceAccountPath):
        from data_pipeline.dags.add_to_vectorstore import chunk_points
        points = [MockPointStruct(id=i, vector=[0.1, 0.2], payload={"note_id": i}) for i in range(250)]
        chunks = list(chunk_points(points, chunk_size=100))
        self.assertEqual(len(chunks), 3)
        self.assertEqual(len(chunks[0]), 100)
        self.assertEqual(len(chunks[-1]), 50)


    @patch("data_pipeline.dags.add_to_vectorstore.QdrantClient")
    @patch("data_pipeline.dags.src.credential_helper.get_service_account_path")
    def test_setup_qdrant_collection_exists(self, MockQdrantClient, mockServiceAccountPath):
        from data_pipeline.dags.add_to_vectorstore import setup_qdrant_collection
        client = MockQdrantClient()
        client.get_collection = MagicMock()
        setup_qdrant_collection(client, "test_collection")
        client.get_collection.assert_called_once_with("test_collection")

    @patch("data_pipeline.dags.add_to_vectorstore.QdrantClient")
    @patch("data_pipeline.dags.src.credential_helper.get_service_account_path")
    def test_setup_qdrant_collection_create(self, MockQdrantClient, mockServiceAccountPath):
        from data_pipeline.dags.add_to_vectorstore import setup_qdrant_collection
        client = MockQdrantClient()
        client.get_collection.side_effect = Exception("Collection does not exist")
        client.create_collection = MagicMock()
        setup_qdrant_collection(client, "new_collection")
        client.create_collection.assert_called_once()

    
    # @patch("data_pipeline.dags.add_to_vectorstore.discovery.build")
    # @patch("data_pipeline.dags.src.credential_helper.setup_google_credentials")
    # @patch("data_pipeline.dags.src.credential_helper.get_service_account_path")
    # def test_get_qdrant_instance_ip(self, mock_discovery_build, mockGoogleCredentialHelper, mockServiceAccountPath):
    #     mockServiceAccountPath.return_value = ""
    #     mockGoogleCredentialHelper.return_value = True
    #     from data_pipeline.dags.add_to_vectorstore import get_qdrant_instance_ip
    #     mock_instance = mock_discovery_build().instances().get().execute
    #     mock_instance.return_value = {
    #         'networkInterfaces': [
    #             {'accessConfigs': [{'natIP': '192.168.1.1'}]}
    #         ]
    #     }
        
    #     ip_address = get_qdrant_instance_ip()
    #     self.assertEqual(ip_address, "192.168.1.1")

if __name__ == "__main__":
    unittest.main()