import unittest
from unittest.mock import patch, MagicMock
import subprocess
from google.cloud import storage
import os
from rag.download_mimic_4_data import *


class TestDownloadAndUpload(unittest.TestCase):

    @patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'wget'))
    def test_download_dataset_failure(self, mock_subprocess):
        """
        Test that `download_dataset` function handles errors when `wget` fails.
        """
        with self.assertRaises(subprocess.CalledProcessError):
            download_dataset("https://physionet.org/files/labelled-notes-hospital-course/1.1.0/mimic-iv-bhc.csv", "test.zip")

    @patch('google.cloud.storage.Client')
    @patch('os.remove')
    def test_upload_to_bucket_success(self, mock_remove, mock_storage_client):
        """
        Test that `upload_to_bucket` uploads a file to the correct bucket and deletes the local file after uploading.
        """
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        upload_to_bucket("test-bucket", "test-destination.zip", "test.zip", "test_folder/")

        mock_storage_client.assert_called_once()
        mock_bucket.blob.assert_called_once_with("test_folder/test-destination.zip")
        mock_blob.upload_from_filename.assert_called_once_with("test.zip")
        mock_remove.assert_called_once_with("test.zip")

    @patch('google.cloud.storage.Client')
    def test_upload_to_bucket_failure(self, mock_storage_client):
        """
        Test that `upload_to_bucket` raises an error when the upload fails.
        """
        mock_blob = MagicMock()
        mock_blob.upload_from_filename.side_effect = Exception("Upload failed")
        mock_bucket = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value.bucket.return_value = mock_bucket

        with self.assertRaises(Exception):
            upload_to_bucket("test-bucket", "test-destination.zip", "test.zip", "test_folder/")


if __name__ == "__main__":
    unittest.main()