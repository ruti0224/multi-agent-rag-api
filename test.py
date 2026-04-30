import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    print("מנסה להתחבר ל-OpenAI...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "תגיד שלום במילה אחת."}]
    )
    print("הצליח! התשובה:", response.choices[0].message.content)
except Exception as e:
    print("שגיאת תקשורת:", e)