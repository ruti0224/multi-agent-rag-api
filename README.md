# 🛡️ Sentinel AI

מערכת חכמה לניתוח מסמכים בשילוב Retrieval-Augmented Generation (RAG) ו-GenAI.

מערכת זו מאפשרת העלאת קבצי PDF/TXT, חיפוש סמנטי במסמכים, ויצירת תשובות חכמות באמצעות מנוע אינטיליגנציה.

---

## 🎯 מה הפרויקט עושה

Sentinel AI מספק:

- ניתוח ומיצוי מידע מתוך קבצי PDF ו-TXT
- חיתוך הטקסט לקטעי וקטורים לשאילתות סמנטיות
- אחסון וחיפוש ב-ChromaDB
- שילוב עם מודל שפה חיצוני לשאלות ותשובות
- ממשק משתמש מבוסס Streamlit ו-API ב-FastAPI

---

## 🚀 התקנה מהירה

### שלב 1 – הכנה

```bash
git clone <repo-url>
cd Sentinel-AI
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### שלב 2 – קונפיגורציה

צור קובץ `.env` עם משתני סביבה נדרשים.

דוגמה:

```env
GOOGLE_API_KEY=your_api_key_here
API_URL=http://127.0.0.1:8000
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=50
```

> אם יש קובץ `.env.example`, העתק אותו ל-`.env` וערוך בהתאם.

### שלב 3 – הרצה

#### הרצת שרת ה-API

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

#### הרצת ממשק המשתמש

```bash
streamlit run ui.py
```

לאחר מכן גש אל:

`http://localhost:8501`

---

## 🧱 מבנה הפרויקט

- `main.py` – נקודת כניסה ל-FastAPI
- `ui.py` – ממשק Streamlit להצגת העלאות ושאילתות
- `agent.py` – לוגיקה של יצירת prompt ושליחה למודל השפה
- `vector_manager.py` – ניהול חיתוך טקסט, יצירת embeddings ו-ChromaDB
- `config.py` – משתני קונפיגורציה וקבועים מרכזיים
- `requirements.txt` – רשימת התלויות
- `sentinel_db/` – מאגר הנתונים של ChromaDB

---

## 🧭 זרימת עבודה

1. משתמש מעלה קובץ PDF או TXT
2. הטקסט מפוצל לקטעי chunks לצורך חיפוש סמנטי
3. היווצרות embeddings ושמירה ב-ChromaDB
4. ביצוע חיפוש סמנטי לפי השאלה של המשתמש
5. בניית prompt חכם למודל השפה
6. קבלת תשובה מתוך מודל השפה
7. החזרת תוצאה למשתמש

---

## 🔧 שימוש ב-API

### POST `/analyze`

ניתוח קובץ ומתן תשובה לשאלה.

#### Request
- `question` – טקסט השאלה
- `file` – קובץ PDF או TXT

#### Response
```json
{
  "answer": "...",
  "status": "success"
}
```

### POST `/reset`

נקה את היסטוריית השיחה ויפתח מחדש את מצב המערכת.

#### Response
```json
{
  "status": "History cleared",
  "success": true
}
```

---

## 🛡️ אבטחה וסטנדרטים

- הפרדת סביבות עם `.env`
- אין מפתחות מוצמדים בקוד
- טיפול בשגיאות כללי באמצעות `try/except`
- לבדיקה ותיעוד סוגי הקלט והפלט
- שמירה על מובנות בקוד וכתיבת docstrings

---

## 📌 המלצות לפיתוח

- הוסף `.env.example` אם אינו קיים
- הקפד על בדיקות יחידה ל-`vector_manager.py` ול-`agent.py`
- אפשר שיפור לוגיקה של ניהול שיחה לחוויית משתמש מתקדמת

---

## 📝 הערות

פרויקט זה מתאים לפיתוח ממשקי חיפוש ידע מבוססי מסמכים, ניסוי עם מודלי שפה ושיפור תהליכי RAG בארכיטקטורה פשוטה ומקצועית.

### GET `/health`
בדיקת בריאות של ה-API

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## 🎯 Best Practices שיושמו

### 1. TypeHints
```python
def query_database(question: str, n_results: int = 3) -> str:
```

### 2. Docstrings
```python
"""
תיאור ברור של הפונקציה.

Args:
    param: הסבר על הפרמטר

Returns:
    הסבר על הערך המוחזר
"""
```

### 3. Configuration Externalization
```python
# config.py
API_KEY = os.getenv("GOOGLE_API_KEY")
MAX_FILE_SIZE_BYTES = int(os.getenv("MAX_FILE_SIZE_MB")) * 1024 * 1024
```

### 4. Comprehensive Logging
```python
logger = logging.getLogger(__name__)
logger.error("בעיה מצאתה)
```

### 5. Error Handling
```python
try:
    process_file()
except FileNotFoundError:
    raise HTTPException(404, "קובץ לא נמצא")
except Exception as e:
    logger.error(f"שגיאה: {str(e)}")
    raise HTTPException(500, "שגיאה פנימית")
```

---

## 🚨 Common Issues & Solutions

### ❌ "GOOGLE_API_KEY לא הוגדר"
**פתרון:** בדוק שנעשה copy של .env.example ל-.env והערך את ה-API key

### ❌ "Connection refused on 127.0.0.1:8000"
**פתרון:** ודא שה-FastAPI server רץ: `python -m uvicorn main:app --reload`

### ❌ "ValueError: לא ניתן לקרוא את הקובץ"
**פתרון:** קובץ הוא לא PDF תקין או UTF-8 text. בדוק את הקידוד.

### ❌ "קובץ גדול מדי"
**פתרון:** הגדל את MAX_FILE_SIZE_MB ב-.env (זהיר מ-memory!)

---

## 📈 שיפורים עתידיים

1. **Embedding Model**
   - החלף את SimpleLocalEmbedding ב-SentenceTransformer
   - תוצאות חיפוש טובות יותר

2. **Database Optimization**
   - Implement indexing
   - Connection pooling

3. **Advanced Prompting**
   - Chain-of-Thought prompting
   - Multi-document reasoning

4. **Caching**
   - Redis for API responses
   - Query cache

5. **Analytics**
   - Track query performance
   - Monitor API costs

---

## 📞 תמיכה

לשאלות או בעיות, בדוק את:
- logs/ שכן נמצאים ה-error messages
- status endpoint (`localhost:8000/health`)

---

**Version:** 1.0.0  
**Last Updated:** 2026-04-23  
**Status:** ✅ Production Ready (Post Code Review)

