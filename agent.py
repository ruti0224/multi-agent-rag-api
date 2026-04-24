import os
from dotenv import load_dotenv

load_dotenv()

# הגדרת התעודה גם עבור צד העיצוב
os.environ['REQUESTS_CA_BUNDLE'] = r"C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt"
os.environ['SSL_CERT_FILE'] = r"C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt"
import requests
import logging
from typing import Dict, List, Optional
from config import API_KEY

# הגדרת logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# קבועים
MODEL_NAME = "models/gemini-1.5-flash"
API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
CONTENT_TYPE = "application/json"
MAX_HISTORY_LENGTH = 10
REQUEST_TIMEOUT = 30
CA_BUNDLE = os.getenv("REQUESTS_CA_BUNDLE")
chat_history: List[Dict] = []


def _get_system_instruction(context: str) -> str:
    """
    יצירת הנחיית המערכת עבור ה-AI.
    
    Args:
        context: תוכן המסמך שנעבר
    
    Returns:
        הנחייה מותאמת
    """
    return f"""You are Sentinel, a senior intelligence analyst with expertise in document analysis.
Your mission is to provide accurate information based ONLY on the provided DOCUMENT CONTENT.

CRITICAL RULES:
1. If the answer is in the document, be concise and professional.
2. If the answer is NOT in the document, state: "I cannot find this information in the source files."
3. Use the conversation history to understand context and maintain coherence.
4. Always cite the relevant parts of the document when answering.
5. Do not hallucinate or invent information not in the document.

DOCUMENT CONTENT:
{context}"""


def get_sentinel_response(user_question: str, context: str) -> str:
    """
    מייצר תשובה חכמה המשלבת את תוכן המסמך עם היסטוריית השיחה.
    
    Args:
        user_question: שאלת המשתמש
        context: תוכן רלוונטי מהמסמך
    
    Returns:
        תשובה מ-Sentinel
    
    Raises:
        Exception: באם חל כשל בחיבור ל-API
    """
    global chat_history

    if not API_KEY:
        logger.error("API_KEY לא הוגדר")
        return "שגיאה: מפתח ה-API לא הוגדר. בדוק את קובץ .env"

    try:
        url = f"{API_URL_TEMPLATE.format(model=MODEL_NAME)}?key={API_KEY}"
        logger.info(f"DEBUG: URL is ready (Key length: {len(API_KEY) if API_KEY else 0})")
        logger.info(f"DEBUG: CA_BUNDLE path: {CA_BUNDLE}")
        system_instruction = _get_system_instruction(context)

        payload = {
            "contents": chat_history + [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_instruction}\n\nUSER QUESTION: {user_question}"}]
                }
            ]
        }

        headers = {"Content-Type": CONTENT_TYPE}

        logger.info(f"שולח בקשה ל-Google Gemini API...")
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            verify=CA_BUNDLE if CA_BUNDLE else True,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            try:
                result = response.json()
                
                if not result.get("candidates"):
                    logger.error("תגובה ריקה מה-API")
                    return "שגיאה: תגובה לא תקינה מה-API"
                
                answer = result["candidates"][0]["content"]["parts"][0]["text"]
                logger.info("קבלת תשובה בהצלחה")

                chat_history.append({"role": "user", "parts": [{"text": user_question}]})
                chat_history.append({"role": "model", "parts": [{"text": answer}]})

                if len(chat_history) > MAX_HISTORY_LENGTH:
                    chat_history[:] = chat_history[-MAX_HISTORY_LENGTH:]
                    logger.debug(f"היסטוריה תורבתה ל-{MAX_HISTORY_LENGTH} הודעות")

                return answer

            except (KeyError, IndexError, ValueError) as e:
                logger.error(f"שגיאה בפarsing תגובת ה-API: {str(e)}")
                return f"שגיאה: תגובה לא תקינה מה-API - {str(e)}"

        elif response.status_code == 401:
            logger.error("אי-ררחור: בדוק את ה-API key")
            return "שגיאה: מפתח ה-API לא תקין"
        elif response.status_code == 429:
            logger.error("Rate limit: יותר מדי בקשות")
            return "שגיאה: יותר מדי בקשות. נסה שוב בעוד דקה"
        else:
            logger.error(f"שגיאת API: {response.status_code}")
            return f"שגיאת API: {response.status_code}"

    except requests.Timeout:
        logger.error("Timeout: ה-API לא הגיב בזמן")
        return "שגיאה: Service timeout. נסה שוב"
    except requests.ConnectionError as e:
        logger.error(f"שגיאת חיבור: {str(e)}")
        return "שגיאה: לא ניתן להתחבר לשירות ה-API"
    except Exception as e:
        logger.error(f"שגיאה לא צפויה: {str(e)}")
        return f"שגיאת מערכת: {str(e)}"


def clear_chat_history() -> None:
    """
    אופס את היסטוריית השיחה.
    שימושי עם עיבוד מסמך חדש.
    """
    global chat_history
    chat_history.clear()
    logger.info("היסטוריית השיחה אופסה")
