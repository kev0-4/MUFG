import logging
from datetime import datetime
import json
from typing import Any

logging.basicConfig(
    filename='api_gateway.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def log_metadata(metadata: dict[str, Any]):
    metadata["timestamp"] = datetime.utcnow().isoformat()
    logging.info(json.dumps(metadata))