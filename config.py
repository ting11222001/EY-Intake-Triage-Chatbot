import os
from dotenv import load_dotenv

load_dotenv()

# Switch between "local" and "aws" here
ENV = os.getenv("ENV", "local")

URLS = {
    "local": "http://localhost:8000",
    "aws": "https://<my-lambda-url>.amazonaws.com/prod",
}

API_URL = URLS[ENV]