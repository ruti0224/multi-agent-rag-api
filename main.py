from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from agent import get_sentinel_response, clear_chat_history
from vector_manager import process_and_store, query_database
from fastapi.middleware.cors import CORSMiddleware
from config import MAX_FILE_SIZE_BYTES
import io
import logging
from typing import Dict
from pypdf import PdfReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sentinel Intelligence API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # מאפשר לכל מקור (כולל Streamlit) לגשת
    allow_credentials=True,
    allow_methods=["*"],  # מאפשר את כל סוגי הבקשות (POST, GET וכו')
    allow_headers=["*"],  # מאפשר את כל סוגי ה-Headers
)
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
ENCODING = "utf-8"


@app.post("/analyze")
async def analyze_file(question: str = Form(...), file: UploadFile = File(...)) -> Dict[str, str]:
    """
    ניתוח קובץ וענתי לשאלה על תוכנו.
    
    Args:
        question: השאלה של המשתמש
        file: הקובץ להעלאה (PDF או TXT)
    
    Returns:
        תשובה מ-Sentinel
    
    Raises:
        HTTPException: באם קובץ לא תקין או שגיאה בעיבוד
    """
    try:
        file_extension = next(
            (ext for ext in ALLOWED_EXTENSIONS if file.filename.endswith(ext)),
            None
        )
        if not file_extension:
            logger.warning(f"סוג קובץ לא תומך: {file.filename}")
            raise HTTPException(400, f"סוג קובץ לא תומך. אנא העלה PDF או TXT")

        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            logger.warning(f"קובץ גדול מדי: {len(content)} bytes")
            raise HTTPException(413, f"קובץ גדול מדי. מקסימום: {MAX_FILE_SIZE_BYTES} bytes")

        if not content:
            raise HTTPException(400, "קובץ ריק. בדוק את הקובץ שהעלית")

        try:
            if file_extension == ".pdf":
                pdf_reader = PdfReader(io.BytesIO(content))
                if len(pdf_reader.pages) == 0:
                    raise ValueError("ה-PDF לא מכיל דפים")
                text = "".join([page.extract_text() or "" for page in pdf_reader.pages])
            else:  # .txt
                text = content.decode(ENCODING)
        except UnicodeDecodeError:
            logger.error(f"שגיאת קידוד ב-{file.filename}")
            raise HTTPException(400, "לא ניתן לקרוא את הקובץ. בדוק שזה UTF-8")
        except Exception as e:
            logger.error(f"שגיאה בקריאת קובץ: {str(e)}")
            raise HTTPException(400, f"שגיאה בקריאת קובץ: {str(e)}")

        if not text.strip():
            raise HTTPException(400, "הקובץ לא מכיל טקסט")

        try:
            process_and_store(text)
            logger.info(f"עובדו {len(text)} תווים בהצלחה")
        except Exception as e:
            logger.error(f"שגיאה בעיבוד הקובץ: {str(e)}")
            raise HTTPException(500, f"שגיאה בעיבוד הקובץ: {str(e)}")

        try:
            context = query_database(question)
        except Exception as e:
            logger.error(f"שגיאה בחיפוש בDB: {str(e)}")
            raise HTTPException(500, f"שגיאה בחיפוש: {str(e)}")

        try:
            answer = get_sentinel_response(question, context)
            logger.info("תשובה הוחזרה בהצלחה")
        except Exception as e:
            logger.error(f"שגיאה בקבלת תשובה: {str(e)}")
            raise HTTPException(500, f"שגיאה בקבלת תשובה: {str(e)}")

        return {"answer": answer, "status": "success"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"שגיאה לא צפויה: {str(e)}")
        raise HTTPException(500, f"שגיאה פנימית בשרת")


@app.post("/reset")
async def reset() -> Dict[str, str]:
    """
    איפוס היסטוריית השיחה.
    
    Returns:
        הודעת סטטוס
    """
    try:
        clear_chat_history()
        logger.info("היסטוריית השיחה אופסה")
        return {"status": "History cleared", "success": True}
    except Exception as e:
        logger.error(f"שגיאה באיפוס: {str(e)}")
        raise HTTPException(500, f"שגיאה באיפוס היסטוריה: {str(e)}")


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """בדיקת בריאות של ה-API"""
    return {"status": "healthy", "version": "1.0.0"}
