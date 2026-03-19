import os
import requests
import yaml
from requests.auth import HTTPBasicAuth

CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "config", "config.yaml")
)

with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

JENKINS_URL = config["jenkins"]["url"]
USERNAME = config["jenkins"]["username"]
TOKEN = config["jenkins"]["token"]

auth = HTTPBasicAuth(USERNAME, TOKEN)


def get_all_jobs():
    url = f"{JENKINS_URL}/api/json"
    response = requests.get(url, auth=auth, timeout=10)
    response.raise_for_status()
    return response.json().get("jobs", [])


def get_job_details(job_name):
    job_name_encoded = job_name.replace(" ", "%20")
    url = f"{JENKINS_URL}/job/{job_name_encoded}/api/json"

    response = requests.get(url, auth=auth, timeout=10)
    if response.status_code != 200:
        return {}

    return response.json()