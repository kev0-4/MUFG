import json
from datetime import datetime
from typing import Dict


def log_metadata(metadata: Dict[str, any]) -> None:
    """
    Log metadata to a file for debugging and compliance.

    Args:
        metadata (Dict[str, any]): Metadata to log (e.g., endpoint, user_id, error).
    """
    try:
        metadata["timestamp"] = datetime.utcnow().isoformat()
        with open("nlp_server.log", "a") as f:
            f.write(json.dumps(metadata) + "\n")
    except Exception as e:
        print(f"Logging error: {str(e)}")
