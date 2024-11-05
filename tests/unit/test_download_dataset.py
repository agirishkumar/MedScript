import unittest
from unittest.mock import patch, mock_open, call
import os
from data
from data-pipeline.src.preprocessing.download_mimic_4_dataset import download_dataset, upload_to_bucket


@patch("subprocess.run")
def test_download_csv(self, mock_run):
    # Set up mock for subprocess.run
    mock_run.return_value.returncode = 0  # Simulate successful download

    # Run the function
    download_csv("username", "password", "http://example.com/file.csv", "local_file.csv")

    # Assert subprocess was called with correct wget command
    mock_run.assert_called_with(
        ["wget", "--user=username", "--password=password", "-O", "local_file.csv", "http://example.com/file.csv"],
        check=True
    )
