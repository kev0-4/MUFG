import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
if not REDIS_PASSWORD:
    raise ValueError("REDIS_PASSWORD not found in .env file")

FINANCIAL_SERVER_URL = os.getenv("FINANCIAL_SERVER_URL", "http://localhost:8001")
NLP_SERVER_URL = os.getenv("NLP_SERVER_URL", "http://localhost:8000")
AUTH_API = os.getenv("AUTH_API", "http://localhost:8002/api")

FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH')