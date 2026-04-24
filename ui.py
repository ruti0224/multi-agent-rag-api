"""
ממשק Streamlit עבור Sentinel Intelligence System.

זהו ממשק משתמש אינטראקטיבי לניתוח מסמכים באמצעות RAG.
"""
import os
# ביטול בדיקת SSL לצד הלקוח כדי שנטפרי לא תחסום תקשורת פנימית במחשב
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['no_proxy'] = 'localhost,127.0.0.1'
import streamlit as st
import requests
import logging
from typing import Optional, Dict
from config import API_URL

# הגדרת logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# קונפיג של הדף
st.set_page_config(
    page_title="Sentinel AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# עיצוב CSS
st.markdown("""
    <style>
    .stChatMessage { 
        border-radius: 15px; 
        padding: 15px; 
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .main { background-color: #f5f7f9; }
    .sidebar { background-color: #e8ecf1; }
    </style>
    """, unsafe_allow_html=True)

# כותרת הדף
st.title("🛡️ Sentinel Intelligence System")
st.markdown("_Intelligent Document Analysis with AI_")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages: list = []

if "current_file" not in st.session_state:
    st.session_state.current_file: Optional[str] = None


# ----- תפריט הצד (Sidebar) -----
with st.sidebar:
    st.header("📂 Intelligence Sources")
    
    # העלאת קובץ
    uploaded_file = st.file_uploader(
        "Upload a document (PDF or TXT)",
        type=["pdf", "txt"],
        help="Choose a file to analyze"
    )
    
    # הצגת פרטי הקובץ שהועלה
    if uploaded_file:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("File Size", f"{len(uploaded_file.getvalue()) / 1024:.1f} KB")
        with col2:
            st.metric("File Type", uploaded_file.name.split(".")[-1].upper())
        
        # בדיקה אם קובץ חדש הועלה
        if st.session_state.current_file != uploaded_file.name:
            st.session_state.current_file = uploaded_file.name
            st.session_state.messages = []  # ניקוי היסטוריה עם קובץ חדש
            st.info(f"✓ Document loaded: {uploaded_file.name}")
    
    st.divider()
    
    # קבוצת כפתורים
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Clear Chat", use_container_width=True):
            try:
                response = requests.post(f"{API_URL}/reset", timeout=5)
                if response.status_code == 200:
                    st.session_state.messages = []
                    st.success("✓ Chat cleared")
                else:
                    st.error("Failed to clear chat")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {str(e)}")
                logger.error(f"Reset request failed: {str(e)}")
    
    with col2:
        if st.button("❓ Help", use_container_width=True):
            st.info("""
            **How to use Sentinel:**
            1. Upload a PDF or TXT document
            2. Ask questions about its content
            3. Sentinel will provide answers based on the document
            """)
    
    st.divider()
    st.caption("Sentinel v1.0 | Powered by Gemini API")


# ----- אזור הצ'אט הראשי -----
st.subheader("💬 Conversation")

# הצגת הודעות קודמות
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])


# ----- תיבת קלט וניתוח -----
if prompt := st.chat_input("Ask a question about the document..."):
    # הוספת שאלת המשתמש להיסטוריה
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # הצגת שאלת המשתמש
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # בדיקה שהחומר הועלה
    if not uploaded_file:
        st.warning("⚠️ Please upload a document first before asking questions.")
        logger.warning("Question asked without uploaded file")
    else:
        # ניתוח המסמך
        with st.chat_message("assistant", avatar="🤖"):
            try:
                with st.spinner("🔍 Analyzing the document..."):
                    # הכנת הקובץ לשליחה
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    data = {"question": prompt}
                    
                    # שליחה לשרת
                    response = requests.post(
                        f"{API_URL}/analyze",
                        files=files,
                        data=data,
                        timeout=30
                    )
                    
                    # טיפול בתגובה
                    if response.status_code == 200:
                        result = response.json()
                        answer = result.get("answer", "No answer received")
                        
                        st.markdown(answer)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer
                        })
                        logger.info("Answer provided successfully")
                        
                    elif response.status_code == 400:
                        error_msg = response.json().get("detail", "Invalid file or question")
                        st.error(f"❌ Invalid input: {error_msg}")
                        logger.error(f"Bad request: {error_msg}")
                        
                    elif response.status_code == 413:
                        st.error("❌ File is too large. Maximum size is 50MB")
                        logger.error("File size exceeded")
                        
                    elif response.status_code == 500:
                        error_msg = response.json().get("detail", "Server error")
                        st.error(f"❌ Server error: {error_msg}")
                        logger.error(f"Server error: {error_msg}")
                        
                    else:
                        st.error(f"❌ Unexpected error (Status {response.status_code})")
                        logger.error(f"Unexpected status code: {response.status_code}")
                        
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timeout. The server took too long to respond.")
                logger.error("Request timeout")
                
            except requests.exceptions.ConnectionError:
                st.error("🔌 Connection error. Make sure the server is running on http://127.0.0.1:8000")
                logger.error("Connection refused")
                
            except Exception as e:
                st.error(f"🚨 Unexpected error: {str(e)}")
                logger.error(f"Unexpected error: {str(e)}")


# ----- עמודת מידע בתחתית -----
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.caption(f"📊 Messages: {len(st.session_state.messages)}")
with col2:
    st.caption("🔐 Your data is processed securely")
with col3:
    st.caption("⚡ Powered by Vector Search + GenAI")
