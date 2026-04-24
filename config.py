import os
from dotenv import load_dotenv

# טעון משתנים סביבה מ-.env
load_dotenv()

# חשוב: אל תחשוף את המפתח ישירות בקוד!
API_KEY = os.getenv("GOOGLE_API_KEY", "")
API_URL = os.getenv("API_URL", "http://localhost:8000")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# בדיקה שהמפתח הועמס
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY לא הוגדר. בדוק קובץ .env")
