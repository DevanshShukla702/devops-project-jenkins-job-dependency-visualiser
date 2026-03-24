import os
import json

MOCK_DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "config", "mock_data.json")
)

def get_all_jobs():
    with open(MOCK_DATA_PATH, "r") as f:
        data = json.load(f)
    return data

def get_job_details(job_name):
    jobs = get_all_jobs()
    for job in jobs:
        if job["name"] == job_name:
             return job["details"]
    return {}
