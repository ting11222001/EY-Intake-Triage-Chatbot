import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Use Streamlit secrets if available, otherwise fall back to config.py
if "AWS_LAMBDA_URL" in st.secrets:
    API_URL = st.secrets["AWS_LAMBDA_URL"]
else:
    from config import API_URL

st.title("Intake Triage Chatbot")
st.caption("Built as a portfolio project demonstrating Responsible AI principles.")
st.write("Answer a few questions and we will route you to the right team.")

questions_response = requests.get(f"{API_URL}/questions")   # {'questions': ['What is your name?', 'Can you describe the problem you are having?', 'How urgent is this for you? (low / medium / high)']}
questions = questions_response.json()["questions"]          # ['What is your name?', 'Can you describe the problem you are having?', 'How urgent is this for you? (low / medium / high)']

answers = []
with st.form("intake_form"):
    for question in questions:
        answer = st.text_input(question)
        answers.append(answer)
    submitted = st.form_submit_button("Submit")

if submitted:
    if any(answer.strip() == "" for answer in answers):
        st.warning("Please answer all questions before submitting.")
    else:
        with st.spinner("Analysing your answers..."):
            # print("Answers submitted by user:", answers)    # Answers submitted by user: ['Tiff', "Can't log into my account", 'high']
            response = requests.post(
                f"{API_URL}/classify",
                json={"answers": answers}
            )
            result = response.json()
            # print("Result:", result)    # Result: {'category': 'account access', 'confidence': 95, 'reason': 'The client explicitly states they cannot log into their account, which is a clear account access issue.', 'routed_to': 'account access team'}
        
        st.divider()

        col1, col2 = st.columns(2)
        col1.metric("Category", result["category"].title())
        col2.metric("Confidence", f"{result['confidence']}%")

        st.write(f"**Reason:** {result['reason']}")

        if result["routed_to"] == "human review":
            st.error("A human agent will review your case and contact you shortly.")
        else:
            st.success(f"Your request will be routed to the **{result['routed_to']}**.")