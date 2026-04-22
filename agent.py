import google.generativeai as genai
from config import API_KEY, MODEL_NAME

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(MODEL_NAME)
