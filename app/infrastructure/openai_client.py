import httpx
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# יצירת לקוח HTTP מותאם שעוקף את בעיית ה-SSL של נטפרי
# אנחנו מגדירים verify=False כדי שהספרייה לא תחסום את החיבור
http_client = httpx.AsyncClient(verify=False)

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=http_client
)

async def get_embedding(text: str):
    """קבלת וקטור מהטקסט תוך שימוש בלקוח המותאם"""
    try:
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding Error: {e}")
        raise e