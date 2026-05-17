import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, "..")))

import logging
from api import create_app

app = create_app()

if __name__ == "__main__":
    is_dev = os.environ.get("FLASK_ENV", "development") != "production"
    port = int(os.environ.get("PORT", 5000))

    logger = logging.getLogger("flowtrace")
    if is_dev:
        logger.info(f"Starting FlowTrace in DEVELOPMENT mode on port {port}")
        app.run(debug=True, host="127.0.0.1", port=port)
    else:
        logger.info(f"Starting FlowTrace in PRODUCTION mode on port {port}")
        app.run(debug=False, host="0.0.0.0", port=port)