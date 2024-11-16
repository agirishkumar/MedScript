import unittest
from unittest.mock import patch, MagicMock
from google.cloud import storage
from io import StringIO
import os
import subprocess
import sys
from data_pipeline.utils.download_mimic_4_data import download_dataset, upload_to_bucket

class TestDatasetFunctions(unittest.TestCase):
    @patch("subprocess.run")
    def test_download_dataset_success(self, mock_run):
        # Mock a successful subprocess run
        mock_run.return_value = MagicMock(returncode=0)
        
        # Call download_dataset
        download_url = "https://example.com/file.zip"
        destination_filename = "test_file.zip"
        result = download_dataset("username", "password", download_url, destination_filename)
        
        mock_run.assert_called_once_with(
            f"wget -r -N -np --user username --password password -O {destination_filename} {download_url}",
            shell=True,
            check=True
        )
        print("Test download_dataset_success passed.")
    
    @patch("subprocess.run")
    def test_download_dataset_failure(self, mock_run):
        # Mock a failed subprocess run with an exception
        mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd="wget")
        
        # Call download_dataset and expect an exception
        download_url = "https://example.com/file.zip"
        destination_filename = "test_file.zip"
        
        with self.assertRaises(subprocess.CalledProcessError):
            download_dataset("username", "password", download_url, destination_filename)
        
        print("Test download_dataset_failure passed.")

    @patch("google.cloud.storage.Client")
    @patch("os.remove")
    def test_upload_to_bucket_success(self, mock_remove, mock_storage_client):
        # Mock storage client and blob
        mock_client_instance = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value = mock_client_instance
        mock_client_instance.get_bucket.return_value.blob.return_value = mock_blob

        bucket_name = "test_bucket"
        destination_blob_name = "test_blob.zip"
        source_path = "test_file.zip"
        
        upload_to_bucket(bucket_name, destination_blob_name, source_path, "raw_data/")

        mock_storage_client.return_value.get_bucket.assert_called_once_with(bucket_name)
        mock_client_instance.get_bucket.return_value.blob.assert_called_once_with("raw_data/" + destination_blob_name)
        mock_blob.upload_from_filename.assert_called_once_with(source_path)
        mock_remove.assert_called_once_with(source_path)

        print("Test upload_to_bucket_success passed.")

    @patch("google.cloud.storage.Client")
    def test_upload_to_bucket_failure(self, mock_storage_client):
        # Simulate a failure in the upload process
        mock_client_instance = MagicMock()
        mock_blob = MagicMock()
        mock_blob.upload_from_filename.side_effect = Exception("Upload error")
        mock_storage_client.return_value = mock_client_instance
        mock_client_instance.get_bucket.return_value.blob.return_value = mock_blob
        
        bucket_name = "test_bucket"
        destination_blob_name = "test_blob.zip"
        source_path = "test_file.zip"
        
        with self.assertRaises(Exception):
            upload_to_bucket(bucket_name, destination_blob_name, source_path, "raw_data/")
        
        print("Test upload_to_bucket_failure passed.")

if __name__ == "__main__":
    unittest.main()
