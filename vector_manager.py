import chromadb
import uuid
import logging
from typing import Optional, List

# הגדרת logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# שלב 1: הגדרת פונקציית Embedding מקומית (עוקף סינון)
# ---------------------------------------------------------
class SimpleLocalEmbedding:
    """
    Embedding מקומי פשוט לעוקף מגבלות רשת.
    
    בעתיד, כדאי להחליף ב-SentenceTransformer:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('msmarco-distilbert-base-tas-b')
    """
    
    def name(self) -> str:
        """שם ה-embedding"""
        return "SimpleLocal"

    def __call__(self, input: List[str]) -> List[List[float]]:
        """
        יצירת וקטורים embedding.
        כרגע מחזירים וקטורים ריקים - זה סתם placeholder.
        
        Args:
            input: רשימת טקסטים
        
        Returns:
            רשימת וקטורים (כל אחד באורך 384)
        """
        if not input:
            return []
        return [[0.0] * 384 for _ in input]


# ---------------------------------------------------------
# שלב 2: אתחול מסד הנתונים הוקטורי
# ---------------------------------------------------------
try:
    client = chromadb.PersistentClient(path="./sentinel_db")
    logger.info("מסד נתונים וקטורי אותחל בהצלחה")
except Exception as e:
    logger.error(f"שגיאה באתחול ChromaDB: {str(e)}")
    raise

# יצירת אוסף (Collection)
try:
    collection = client.get_or_create_collection(
        name="sentinel_knowledge",
        embedding_function=SimpleLocalEmbedding()
    )
    logger.info("Collections ה-'sentinel_knowledge' אותחל")
except Exception as e:
    logger.error(f"שגיאה ביצירת collection: {str(e)}")
    raise


# ---------------------------------------------------------
# שלב 3: פונקציית עיבוד ואחסון (The Ingestion Pipeline)
# ---------------------------------------------------------
def process_and_store(text: str, chunk_size: int = 500) -> str:
    """
    עיבוד וחסן של טקסט ב-Vector Database.
    
    הפונקציה חותכת טקסט ארוך לנתחים ושומרת אותם ב-Chroma.
    
    Args:
        text: הטקסט הגולמי (מ-PDF או TXT)
        chunk_size: גודל כל נתח בתווים (ברירת מחדל: 500)
    
    Returns:
        הודעת סטטוס על התהליך
    
    Raises:
        ValueError: אם הטקסט ריק
        Exception: שגיאה בדיסק או בנתונים
    """
    if not text or not text.strip():
        logger.warning("ניסיון להעביר טקסט ריק")
        raise ValueError("לא ניתן לעבד טקסט ריק")

    try:
        # חיתוך הטקסט ל-chunks בגודל נחמד
        chunks: List[str] = [
            text[i:i + chunk_size].strip()
            for i in range(0, len(text), chunk_size)
            if text[i:i + chunk_size].strip()  # דילוג על chunks ריקים
        ]

        if not chunks:
            raise ValueError("לא היו chunks תק אחרי עיבוד")

        # יצירת מזהים ייחודיים
        ids: List[str] = [str(uuid.uuid4()) for _ in chunks]

        # הוספה למסד הנתונים
        collection.add(documents=chunks, ids=ids)
        
        logger.info(f"הוספו {len(chunks)} chunks בהצלחה ל-DB")
        return f"✓ עובדו {len(chunks)} chunks בהצלחה"

    except Exception as e:
        logger.error(f"שגיאה בעיבוד/אחסון: {str(e)}")
        raise


# ---------------------------------------------------------
# שלב 4: פונקציית שליפה (The Retrieval Pipeline)
# ---------------------------------------------------------
def query_database(question: str, n_results: int = 3) -> str:
    """
    חיפוש בווקטור DB לטקסט רלוונטי.
    
    Args:
        question: שאלת החיפוש
        n_results: כמה תוצאות להחזיר (ברירת מחדל: 3)
    
    Returns:
        הטקסט הרלוונטי ביותר, או מחרוזת ריקה אם לא נמצא
    """
    if not question or not question.strip():
        logger.warning("שאלה ריקה הועברה לחיפוש")
        return ""

    try:
        # חיפוש במסד הנתונים
        results = collection.query(
            query_texts=[question.strip()],
            n_results=n_results
        )

        # חילוץ התוצאות
        if results and results.get("documents") and results["documents"][0]:
            # חיתוך התוצאות לשתי תוצאות ראשונות
            relevant_docs = results["documents"][0][:2]
            combined_context = " ".join(relevant_docs)
            
            logger.info(f"נמצאו {len(relevant_docs)} תוצאות רלוונטיות")
            return combined_context

        logger.info("לא נמצאו תוצאות רלוונטיות")
        return ""

    except Exception as e:
        logger.error(f"שגיאה בחיפוש: {str(e)}")
        raise


def clear_database() -> None:
    """
    ניקוי מלא של מסד הנתונים (למטרות בדיקה).
    """
    try:
        # מחיקת כל המסמכים מהקולקציה
        all_ids = collection.get()["ids"]
        if all_ids:
            collection.delete(ids=all_ids)
            logger.info(f"נמחקו {len(all_ids)} דוקומנטים")
    except Exception as e:
        logger.error(f"שגיאה בניקוי: {str(e)}")
        raise
