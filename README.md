# 🛡️ Sentinel Intelligence System

מערכת ניתוח מסמכים חכמה המשלבת RAG (Retrieval-Augmented Generation) עם GenAI.

## 📋 תכנונים ופתרונות (Code Review Results)

### ✅ בעיות שתוקנו

#### 🔴 חמורות (Critical)
1. **חשיפת API Key** - הועבר ל-.env
2. **קוד כפול ב-ui.py** - דדופליקציה מלאה
3. **API Key בחוקי** - עוקב מ-config.py

#### 🟠 בינוניות (Medium)
1. **ללא error handling** - הוסף try-except בכל המודולים
2. **ללא Type Hints** - הוסף לכל הפונקציות
3. **ללא Logging** - הוסף logging comprehensible
4. **File validation** - הוסף בדיקות גודל וסוג קובץ
5. **Response validation** - בדיקת תוכן התגובה מ-API

#### 🔵 Minor
1. **Hardcoded URLs** - העבר ל-config
2. **ללא docstrings** - הוסף דוקומנטציה
3. **ללא requirements.txt** - יצור फ़יל תלויות

---

## 🚀 התחלה מהירה

### 1️⃣ התקנה

```bash
# שכפל את המחסן
git clone <repo-url>
cd Sentinel-AI

# צור virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# או: source venv/bin/activate  # macOS/Linux

# התקן תלויות
pip install -r requirements.txt
```

### 2️⃣ הגדרות

העתק את `.env.example` ל-`.env` והגדר:

```bash
cp .env .env
```

ערוך את `.env`:
```env
GOOGLE_API_KEY=your_actual_api_key_here
API_URL=http://127.0.0.1:8000
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=50
```

### 3️⃣ הרצה

#### בשני terminal חלונות נפרדים:

**Terminal 1 - FastAPI Server:**
```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Streamlit UI:**
```bash
streamlit run ui.py
```

הממשק פתח באופן אוטומטי ב-`http://localhost:8501`

---

## 📁 מבנה הפרויקט

```
Sentinel-AI/
├── main.py              # FastAPI endpoint עבור ניתוח
├── agent.py             # שיטות האינטליגנציה (Gemini)
├── vector_manager.py    # ניהול Vector Database (ChromaDB)
├── ui.py                # ממשק Streamlit
├── config.py            # הגדרות וקבועים
├── requirements.txt     # תלויות Python
├── .env.example         # דוגמת משתנים סביבה
├── .gitignore          # קבצים להתעלם
└── sentinel_db/        # (יצור אוטומטית) ChromaDB storage
```

---

## 🔍 זרימת התהליך

```
User Upload (PDF/TXT)
         ↓
    FastAPI Processing
         ↓
    PDF/TXT Extraction
         ↓
    Vector Chunking (500 chars each)
         ↓
    ChromaDB Storage
         ↓
    Semantic Search (Query → Retrieve)
         ↓
    Prompt Engineering
         ↓
    Google Gemini API
         ↓
    Response to User
         ↓
    Chat History Management
```

---

## 🛡️ עקרונות אבטחה

- ✅ **ללא hardcoded keys** - משתמש ב-.env
- ✅ **Type hints** - בדיקה סטטית של types
- ✅ **Error handling** - כל שגיאה מטופלת
- ✅ **Logging** - ניטור מלא של אירועים
- ✅ **File validation** - בדיקת גודל וסוג
- ✅ **Response validation** - בדיקת JSON structures

---

## 📊 תכונות עדכניות

### ✨ שיפורים ב-Code Review

1. **Type Hints על כל הפונקציות**
   ```python
   def process_and_store(text: str, chunk_size: int = 500) -> str:
   ```

2. **Comprehensive Error Handling**
   ```python
   try:
       # עיבוד
   except CustomError as e:
       logger.error(...) 
       raise HTTPException(...)
   ```

3. **Logging System**
   ```python
   logger.info("Message uploaded successfully")
   logger.error(f"Error occurred: {str(e)}")
   ```

4. **Configuration Management**
   - Environment variables
   - Centralized config.py
   - Constants definitions

5. **API Documentation**
   - Docstrings on all functions
   - Type hints in parameters
   - Return value documentation

---

## 🔧 פונקציות API

### POST `/analyze`
ניתוח מסמך וענתי לשאלה

**Request:**
```json
{
  "question": "מי היה הנושא הראשי?",
  "file": <binary PDF/TXT>
}
```

**Response:**
```json
{
  "answer": "התשובה של סנטינל...",
  "status": "success"
}
```

### POST `/reset`
איפוס היסטוריית השיחה

**Response:**
```json
{
  "status": "History cleared",
  "success": true
}
```

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

