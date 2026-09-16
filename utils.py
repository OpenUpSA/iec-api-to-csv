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
    if not response.ok:
        # A 401 here could mean the token has expired
        print(f"Error {response.status_code} from {url}: {response.text[:200]}")
        return []
    try:
        return response.json()
    except json.JSONDecodeError:
        # An empty body with a 200 means the IEC has nothing to serve yet
        body = response.text.strip()
        if not body:
            print(f"Empty response ({response.status_code}) from {url}")
        else:
            print(f"Non-JSON response ({response.status_code}) from {url}: {body[:200]}")
        return []


def save_json_to_file_in_directory(json_data, directory, filename):
    if not json_data:
        return
    directory = os.path.join(os.path.dirname(__file__), directory)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(f"{directory}/{filename}.json", "w") as file:
        json.dump(json_data, file)


def json_file_exists(directory, filename):
    directory = os.path.join(os.path.dirname(__file__), directory)
    return os.path.exists(f"{directory}/{filename}.json")


def load_json_from_file_in_directory(directory, filename):
    directory = os.path.join(os.path.dirname(__file__), directory)
    with open(f"{directory}/{filename}.json", "r") as file:
        return json.load(file)
