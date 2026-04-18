from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()      # Create a connection to the Anthropic service

QUESTIONS = [
    "What is your name?",
    "Can you describe the problem you are having?",
    "How urgent is this for you? (low / medium / high)",
]

def run_chat():
    print("Welcome to the intake chatbot. I will ask you a few questions.\n")

    answers = []
    for question in QUESTIONS:
        print(f"Bot: {question}")
        answer = input("You: ")
        answers.append(f"Q: {question}\nA: {answer}")
    
    conversation = "\n".join(answers)
    print("\nBot: Thank you. Let me review your answers...\n")

    classify(conversation)

def classify(conversation):
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

    # print(f"Bot: Here's what I found: {response}")

    result = response.content[0].text
    # print("Bot (internal):", result)
    route(result)

def route(result):
    lines = result.strip().split("\n")
    # print("Bot (debug):", lines)
    category = ""
    confidence = 0

    for line in lines:
        if line.startswith("CATEGORY:"):
            category = line.replace("CATEGORY:", "").strip()
        if line.startswith("CONFIDENCE:"):
            confidence = int(line.replace("CONFIDENCE:", "").strip())

    threshold = 70
    if confidence >= threshold:
        print(f"Bot: You will be routed to our {category} team.")
    else:
        print("Bot: I'm not confident enough to classify route you automatically.")
        print("Bot: A human agent will review your case and contact you shortly.")

if __name__ == "__main__":
    run_chat()