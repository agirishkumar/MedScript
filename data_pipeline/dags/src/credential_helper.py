import os

import sys
from pathlib import Path
current_file = Path(__file__).resolve()
project_dir = current_file.parent.parent
sys.path.append(str(project_dir))
from logger import logger

def get_service_account_path():
    """
    Get the correct service account path based on the execution environment.
    
    Returns:
        str: Absolute path to the service account JSON file
    """
    # Inside Airflow container
    if os.path.exists('/opt/airflow/secrets/medscript-sa.json'):
        return '/opt/airflow/secrets/medscript-sa.json'
    
    # Local development - relative to data_pipeline directory
    base_path = Path(__file__).parent.parent  # Goes up from src to data_pipeline
    local_path = base_path / 'secrets' / 'medscript-sa.json'
    
    if local_path.exists():
        return str(local_path)
    
    raise FileNotFoundError(
        "Service account file not found. Expected at:\n"
        "1. /opt/airflow/secrets/medscript-sa.json (container)\n"
        f"2. {local_path} (local development)"
    )

def setup_google_credentials():
    """
    Set up Google credentials environment variable with better error handling.
    """
    try:
        service_account_path = get_service_account_path()
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_path
        return True
    except FileNotFoundError as e:
        logger.error(f"Failed to setup Google credentials: {str(e)}")
        raise