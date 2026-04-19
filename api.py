import os
import boto3
from fastapi import FastAPI
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

def get_api_key():
    # For local development, store the API key in an environment variable or .env file
    local_key = os.environ.get('ANTHROPIC_API_KEY')
    if local_key:
        return local_key
    
    # For Lambda, fetch the API key from AWS SSM Parameter Store instead of environment variables, for better security
    ssm = boto3.client('ssm', region_name='ap-southeast-2')  # Creates a connection to the AWS SSM service in the Sydney region
    response = ssm.get_parameter(
        Name='/intake-chatbot/anthropic-api-key',            
        WithDecryption=True                                  # WithDecryption=True is required because it was stored as SecureString
    )
    return response['Parameter']['Value']

client = Anthropic(api_key=get_api_key())      # Create a connection to the Anthropic service
app = FastAPI()           # A FastAPI instance that will listen for incoming requests

QUESTIONS = [
    "What is your name?",
    "Can you describe the problem you are having?",
    "How urgent is this for you? (low / medium / high)",
]

class ChatRequest(BaseModel):       # Define the incoming chat requests i.e. a list of text responses from user inputs
    answers: list[str]

class ChatResponse(BaseModel):      # Define what will reply back
    category: str
    confidence: int
    reason: str
    routed_to: str

@app.get("/questions")
def get_questions():
    return {"questions": QUESTIONS}

@app.post("/classify")
def classify(request: ChatRequest):
    # print("Received answers: ", request.answers)        # ['Tiff', "didn't get the invoice", 'high']
    
    answers = []
    for i in range(len(QUESTIONS)):
        answers.append(f"Q: {QUESTIONS[i]}\nA: {request.answers[i]}")

    conversation = "\n".join(answers)
    # print("Conversation: ", conversation)

    prompt = f"""
        You are a triage assistant. Based on the client answers below, do two things:

        1. Classify their problem into ONE of these categories:
        - billing
        - technical support
        - account access
        - general enquiry

        2. Give a confidence score from 0 to 100 showing how sure you are.

        Respond in this exact format:
        CATEGORY: <category>
        CONFIDENCE: <number>
        REASON: <one sentence>

        Client answers:
        {conversation}
    """

    response = client.messages.create(
        model="claude-haiku-4-5",                           # just simple classification for this example, so we can use a smaller model
        max_tokens=200,                                     # stop after 200 tokens at most
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.content[0].text.strip().split("\n")
    # print("Result: ", result)                             # ['CATEGORY: billing', 'CONFIDENCE: 92', 'REASON: The client explicitly states they did not receive an invoice, which is a billing-related issue.']

    category = ""
    confidence = 0
    reason = ""

    for line in result:
        if line.startswith("CATEGORY:"):
            category = line.replace("CATEGORY:", "").strip()
        if line.startswith("CONFIDENCE:"):
            confidence = int(line.replace("CONFIDENCE:", "").strip())
        if line.startswith("REASON:"):
            reason = line.replace("REASON:", "").strip()

    THRESHOLD = 70
    if confidence >= THRESHOLD:
        routed_to = f"{category} team"
    else:
        routed_to = "human review"

    return ChatResponse(
        category=category,
        confidence=confidence,
        reason=reason,
        routed_to=routed_to
    )


from mangum import Mangum
handler = Mangum(app)