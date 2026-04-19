import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "aws")   # Default to "aws" if ENV variable is not set

URLS = {
    "local": "http://localhost:8000",
    "aws": os.getenv("AWS_LAMBDA_URL"),
}

API_URL = URLS[ENV]