import os
import yaml
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, "..")))

from flask_login import login_required
import services.mock_service as mock_service
from services.jenkins_client import JenkinsClient

CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "config", "config.yaml"))
try:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
except FileNotFoundError:
    config = {}

app_config = config.get("app", {})
DEMO_MODE = os.environ.get(
    "DEMO_MODE",
    os.environ.get("FLOWTRACE_DEMO_MODE", str(app_config.get("demo_mode", False)))
).lower() in ("true", "1", "yes")

AUTH_ENABLED = os.environ.get(
    "FLOWTRACE_AUTH_ENABLED",
    str(config.get("auth", {}).get("enabled", True))
).lower() in ("true", "1", "yes")

FLASK_ENV = os.environ.get("FLASK_ENV", "production")
IS_PRODUCTION = FLASK_ENV == "production"

# Singleton Jenkins Client
_jenkins_client = None

def get_service():
    if DEMO_MODE:
        return mock_service
    
    global _jenkins_client
    if _jenkins_client is None:
        _jenkins_client = JenkinsClient()
    return _jenkins_client

def require_auth(f):
    """Conditionally apply @login_required based on AUTH_ENABLED."""
    if AUTH_ENABLED:
        return login_required(f)
    return f
