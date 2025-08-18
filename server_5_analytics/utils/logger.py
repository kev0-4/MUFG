import logging
from datetime import datetime
import json

logging.basicConfig(
    filename='ai_analytics_server.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)


def log_metadata(metadata: dict):
    metadata["timestamp"] = datetime.utcnow().isoformat()
    logging.info(json.dumps(metadata))
