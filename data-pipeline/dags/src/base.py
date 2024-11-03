import requests
import json

# TODO: Move to a config file!
BASE_API_URL = "http://fastapi:8000/"

def get_data(url: str) -> dict:
    """
    Helper function to get data from the specified url.
    
    Parameters:
        url (str): The URL of the API endpoint to get data from.
        
    Returns:
        dict: The JSON response data from the API.

    Raises:
        ValueError: If the API request fails.
    """
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # TODO: Remove, for testing purpose only
        with open(f'/tmp/url.json', 'w') as f:
            json.dump(data, f)
        return data
    else:
        raise ValueError(f"Failed to fetch data from {url}")

def get_summary(patient_id: int) -> dict:
    """
    Fetches summary for a patient with the given patient id and returns the data.

    Returns: The JSON data
    """
    # url = BASE_API_URL + "/api/v1/{patient_id}/summary"
    url = BASE_API_URL + "health"
    return get_data(url)


def preprocess_data(data: dict) -> dict:
    print("Preprocess:", data)
    return data