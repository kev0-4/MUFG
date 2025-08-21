import logging
import json
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S,%s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def log_metadata(data: dict):
    logging.info(json.dumps(data))