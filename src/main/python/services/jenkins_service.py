import os
import logging
import requests
import yaml
from requests.auth import HTTPBasicAuth

logger = logging.getLogger("flowtrace.jenkins")

CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
)

with open(CONFIG_PATH, encoding="utf-8") as f:
    config = yaml.safe_load(f)

# Environment variables take priority over config.yaml
JENKINS_URL = os.environ.get("JENKINS_URL", config.get("jenkins", {}).get("url", "http://localhost:8080"))
USERNAME = os.environ.get("JENKINS_USERNAME", config.get("jenkins", {}).get("username", ""))
TOKEN = os.environ.get("JENKINS_TOKEN", config.get("jenkins", {}).get("token", ""))

if not USERNAME or not TOKEN:
    logger.warning("Jenkins credentials not configured. Set JENKINS_USERNAME and JENKINS_TOKEN env vars.")

auth = HTTPBasicAuth(USERNAME, TOKEN)

# Connection timeout settings
CONNECT_TIMEOUT = 5
READ_TIMEOUT = 15


def get_all_jobs():
    """Fetch all jobs from Jenkins."""
    url = f"{JENKINS_URL}/api/json"
    try:
        response = requests.get(url, auth=auth, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        response.raise_for_status()
        return response.json().get("jobs", [])
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to Jenkins at {JENKINS_URL}")
        raise ConnectionError(f"Cannot reach Jenkins server at {JENKINS_URL}")
    except requests.exceptions.Timeout:
        logger.error(f"Jenkins request timed out: {url}")
        raise TimeoutError("Jenkins server took too long to respond")
    except requests.exceptions.HTTPError as e:
        logger.error(f"Jenkins HTTP error: {e.response.status_code}")
        raise


def get_job_details(job_name):
    """Fetch details for a specific Jenkins job."""
    job_name_encoded = requests.utils.quote(job_name, safe="")
    url = f"{JENKINS_URL}/job/{job_name_encoded}/api/json"

    try:
        response = requests.get(url, auth=auth, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        if response.status_code != 200:
            logger.warning(f"Job details unavailable for '{job_name}': HTTP {response.status_code}")
            return {}
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching job '{job_name}': {e}")
        return {}