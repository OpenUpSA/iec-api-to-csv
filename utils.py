import requests
import os
import json


def get_json_from_endpoint(endpoint):
    bearer_token = os.getenv("IEC_API_TOKEN")
    if not bearer_token:
        raise ValueError("IEC_API_TOKEN environment variable not set")
    base_url = "https://api.elections.org.za/"
    url = base_url + endpoint
    print("Fetching:", url)
    response = requests.get(url, headers={"Authorization": "Bearer " + bearer_token})
    try:
        return response.json()
    except json.JSONDecodeError as e:
        print(f"Error decoding response from {base_url + endpoint}: {e}")
        return []


def save_json_to_file_in_directory(json_data, directory, filename):
    if not json_data:
        return
    directory = os.path.join(os.path.dirname(__file__), directory)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(f"{directory}/{filename}.json", "w") as file:
        json.dump(json_data, file)
