import os
import requests
import logging
from typing import List, Dict
from config import API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_NAME = "models/gemini-1.5-flash"
API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
chat_history: List[Dict] = []


def get_sentinel_response(user_question: str, context: str) -> str:
    global chat_history
    url = f"{API_URL_TEMPLATE.format(model=MODEL_NAME)}?key={API_KEY}"

    system_instruction = f"Base your answer ONLY on this content: {context}"

    payload = {
        "contents": chat_history + [{
            "role": "user",
            "parts": [{"text": f"{system_instruction}\n\nQuestion: {user_question}"}]
        }]
    }

    response = requests.post(url, json=payload, timeout=30)

    if response.status_code == 200:
        answer = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        chat_history.append({"role": "user", "parts": [{"text": user_question}]})
        chat_history.append({"role": "model", "parts": [{"text": answer}]})
        return answer
    return "Error connecting to AI service."


def clear_chat_history():
    global chat_history
    chat_history.clear()