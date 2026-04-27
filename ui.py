import streamlit as st
import requests
import logging
from typing import Optional
from config import API_URL

# הגדרת לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# הגדרות עמוד
st.set_page_config(
    page_title="Sentinel AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# עיצוב מותאם אישית (CSS)
st.markdown("""
    <style>
    .stChatMessage { 
        border-radius: 15px; 
        padding: 15px; 
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

# אתחול משתני Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_file" not in st.session_state:
    st.session_state.current_file = None

# כותרת ראשית
st.title("🛡️ Sentinel Intelligence System")
st.markdown("_ניתוח מסמכים חכם מבוסס בינה מלאכותית_")

# סרגל צד (Sidebar)
with st.sidebar:
    st.header("📂 מקורות מידע")

    uploaded_file = st.file_uploader(
        "העלה מסמך (PDF או TXT)",
        type=["pdf", "txt"],
        help="בחר קובץ כדי להתחיל בניתוח"
    )

    if uploaded_file:
        # הצגת פרטי הקובץ
        col1, col2 = st.columns(2)
        with col1:
            st.metric("גודל קובץ", f"{len(uploaded_file.getvalue()) / 1024:.1f} KB")
        with col2:
            st.metric("סוג", uploaded_file.name.split(".")[-1].upper())

        # לוגיקת איפוס בעת החלפת קובץ (שלב 5 בתוכנית)
        if st.session_state.current_file != uploaded_file.name:
            try:
                # קריאה לשרת לביצוע Reset מלא (ניקוי DB והיסטוריה)
                with st.spinner("מכין סביבה לקובץ חדש..."):
                    requests.post(f"{API_URL}/reset", timeout=5)

                st.session_state.current_file = uploaded_file.name
                st.session_state.messages = []
                st.success(f"המסמך {uploaded_file.name} נטען בהצלחה")
                st.rerun()
            except Exception as e:
                logger.error(f"Error during auto-reset: {e}")
                st.error("שגיאה בחיבור לשרת לצורך איפוס")

    st.divider()

    # כפתור איפוס ידני
    if st.button("🔄 נקה שיחה", use_container_width=True):
        try:
            response = requests.post(f"{API_URL}/reset", timeout=5)
            if response.status_code == 200:
                st.session_state.messages = []
                st.success("השיחה אופסה")
                st.rerun()
        except Exception as e:
            st.error("לא ניתן להתחבר לשרת")

    st.caption("Sentinel v1.0 | Powered by Gemini API")

# תצוגת הצ'אט
st.subheader("💬 שיחה עם Sentinel")

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# קלט מהמשתמש
if prompt := st.chat_input("שאל שאלה על המסמך..."):
    # הצגת שאלת המשתמש
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    if not uploaded_file:
        st.warning("⚠️ אנא העלה מסמך לפני שליחת שאלה.")
    else:
        with st.chat_message("assistant", avatar="🤖"):
            try:
                with st.spinner("מנתח את המסמך..."):
                    # הכנת הנתונים לשליחה
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    data = {"question": prompt}

                    response = requests.post(
                        f"{API_URL}/analyze",
                        files=files,
                        data=data,
                        timeout=45
                    )

                    if response.status_code == 200:
                        result = response.json()
                        answer = result.get("answer", "לא התקבלה תשובה מהשרת")

                        st.markdown(answer)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer
                        })
                    else:
                        st.error(f"שגיאת שרת: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("🔌 שגיאת חיבור: וודא ששרת ה-API רץ (Uvicorn)")
            except Exception as e:
                st.error(f"🚨 שגיאה בלתי צפויה: {str(e)}")

# שורת סטטוס תחתונה
st.divider()
st.caption(f"📊 הודעות בשיחה: {len(st.session_state.messages)} | מערכת מאובטחת")