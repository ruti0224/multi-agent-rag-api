import os
import logging
from openai import AsyncOpenAI
from app.infrastructure.vector_store import vector_store
from dotenv import load_dotenv

# טעינת הגדרות
load_dotenv()
logger = logging.getLogger("Engine")

# אתחול הלקוח של OpenAI
# הערה: בסביבת נטפרי/Restricted, ודאי שאין חסימת SSL ל-api.openai.com
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_document_summary(filename: str):
    """
    מייצר תקציר מנהלים אוטומטי וכללי עבור כל סוג מסמך.
    """
    try:
        # שאילתת חיפוש כללית להבאת תוכן מרכזי
        search_results = await vector_store.search(
            query="executive summary main points overview key details",
            filename=filename,
            n_results=5
        )
        context = search_results.get("context", "")

        if not context:
            return "לא ניתן היה לחלץ מספיק מידע מהמסמך לצורך סיכום."

        # פרומפט כללי שמתאים לכל מסמך
        prompt = f"""You are Sentinel AI, an elite document analyst.
        Your task is to provide a concise Executive Summary in HEBREW for the document: {filename}.

        Focus on:
        1. Document type and its main purpose.
        2. Key entities involved (people, companies, organizations).
        3. Main topics, important dates, or crucial data points.

        Answer in 3-4 professional bullet points.

        CONTEXT:
        {context}"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Summary generation failed for {filename}: {e}")
        return "אירעה שגיאה בניתוח האוטומטי של המסמך."
    
async def sentinel_rag_flow(question: str, filename: str):
    """
    ניהול זרימת ה-RAG: שליפה מה-Vector DB ויצירת תשובה זורמת (Streaming).
    """
    try:
        # חיפוש סמנטי מוגבל למסמך הנוכחי למניעת ערבוב נתונים
        search_results = await vector_store.search(
            query=question,
            filename=filename,
            n_results=3
        )

        context = search_results.get("context", "")
        sources = search_results.get("sources", [])

        system_prompt = f"""You are Sentinel AI, a professional analyst.
        Answer the user's question ONLY based on the provided context.
        If the information is not in the context, state that you don't know based on this document.

        DOCUMENT NAME: {filename}

        CONTEXT:
        {context}

        Answer in Hebrew clearly and accurately."""
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            stream=False
        )

        # החזרת הטקסט המלא
        return response.choices[0].message.content, sources
        return stream, sources
    except Exception as e:
        logger.error(f"RAG flow failed: {e}")
        raise e