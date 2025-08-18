import os
from dotenv import load_dotenv

load_dotenv()

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
if not REDIS_PASSWORD:
    raise ValueError("REDIS_PASSWORD not found in .env file")

NLP_SERVER_URL = os.getenv("NLP_SERVER_URL", "http://localhost:8000")