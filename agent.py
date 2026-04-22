import os
import ssl
import google.generativeai as genai
from config import API_KEY, MODEL_NAME

os.environ['CURL_CA_BUNDLE'] = ''
ssl._create_default_https_context = ssl._create_unverified_context

genai.configure(api_key=API_KEY, transport="rest")

model = genai.GenerativeModel("gemini-1.5-flash")

def get_sentinel_response(user_question: str):
    prompt = f"You are Sentinel. Answer: {user_question}"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error connecting to AI: {str(e)}"