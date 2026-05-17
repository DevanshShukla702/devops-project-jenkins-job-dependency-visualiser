import os
import logging
import requests
import yaml
from requests.auth import HTTPBasicAuth

logger = logging.getLogger("flowtrace.jenkins")

CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
)

try:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
except FileNotFoundError:
    config = {}

class JenkinsClient:
    """Encapsulates Jenkins API communication with connection pooling."""
    
    def __init__(self):
        self.url = os.environ.get("JENKINS_URL", config.get("jenkins", {}).get("url", "http://localhost:8080")).rstrip('/')
        username = os.environ.get("JENKINS_USERNAME", config.get("jenkins", {}).get("username", ""))
        token = os.environ.get("JENKINS_TOKEN", config.get("jenkins", {}).get("token", ""))
        
        # Connection pooling for high-throughput API requests
        self.session = requests.Session()
        if username and token:
            self.session.auth = HTTPBasicAuth(username, token)
        else:
            logger.warning("Jenkins credentials missing. Operating unauthenticated.")
            
        self.session.headers.update({"Accept": "application/json"})
        self.timeout = (5, 15) # (Connect, Read)

    def get_all_jobs(self):
        try:
            response = self.session.get(f"{self.url}/api/json", timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("jobs", [])
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Jenkins at {self.url}")
            raise ConnectionError(f"Cannot reach Jenkins server at {self.url}")
        except requests.exceptions.Timeout:
            logger.error(f"Jenkins request timed out: {self.url}")
            raise TimeoutError("Jenkins server took too long to respond")
        except requests.exceptions.RequestException as e:
            logger.error(f"Jenkins connection error: {e}")
            raise

    def get_job_details(self, job_name):
        job_encoded = requests.utils.quote(job_name, safe="")
        try:
            response = self.session.get(f"{self.url}/job/{job_encoded}/api/json", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            return {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch job {job_name}: {e}")
            return {}
