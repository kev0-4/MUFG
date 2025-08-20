import os
from dotenv import load_dotenv

load_dotenv()

FINANCIAL_SERVER_URL = os.getenv("FINANCIAL_SERVER_URL", "http://localhost:8001")
NLP_SERVER_URL = os.getenv("NLP_SERVER_URL", "http://localhost:8000")
ANALYTICS_SERVER_URL = os.getenv("ANALYTICS_SERVER_URL", "http://localhost:8002")