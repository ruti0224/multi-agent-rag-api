import streamlit as st
import requests

st.set_page_config(page_title="Sentinel AI | Executive Analysis", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stAlert { background-color: #161b22; border-right: 5px solid #238636; border-radius: 12px; }
    .stChatMessage { border-radius: 15px; margin-bottom: 15px; }
    h1, h2, h3 { color: #e6edf3 !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ Sentinel AI")
st.markdown("##### *מערכת ניתוח מודיעין וסריקת מסמכים מתקדמת*")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_summary" not in st.session_state:
    st.session_state.current_summary = None
if "last_processed_file" not in st.session_state:
    st.session_state.last_processed_file = None

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=80)
    st.header("📂 ניהול מסמכים")

    uploaded_file = st.file_uploader("בחר קובץ לניתוח", type=["pdf", "txt"])

    st.divider()
    if st.button("🗑️ נקה היסטוריית שיחה", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_summary = None
        st.session_state.last_processed_file = None
        st.rerun()

# לוגיקת תקציר מנהלים וניקוי מסך בהחלפת קובץ
if uploaded_file:
    if st.session_state.last_processed_file != uploaded_file.name:
        # איפוס מוחלט של זיכרון הממשק לקובץ החדש
        st.session_state.current_summary = None
        st.session_state.messages = []

        with st.status(f"🔍 מנתח את {uploaded_file.name}...", expanded=True) as status:
            try:
                # שליחת בקשה לעיבוד ושמירה ב-DB (אם לא קיים)
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/octet-stream")}
                requests.post("http://127.0.0.1:8000/analyze",
                              data={"question": "init", "filename": uploaded_file.name}, files=files)

                # משיכת הסיכום
                response = requests.get(f"http://127.0.0.1:8000/summary/{uploaded_file.name}")
                if response.status_code == 200:
                    st.session_state.current_summary = response.json()["summary"]
                    st.session_state.last_processed_file = uploaded_file.name
                    status.update(label="✅ הניתוח הושלם!", state="complete", expanded=False)
            except Exception as e:
                st.error(f"שגיאת חיבור לשרת: {e}")

    if st.session_state.current_summary:
        st.info(f"💡 **תקציר מנהלים עבור {uploaded_file.name}:**\n\n{st.session_state.current_summary}")

# תצוגת צ'אט
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# קלט ושליחה
if prompt := st.chat_input("שאל שאלה על המסמך..."):
    if not uploaded_file:
        st.warning("אנא העלה קובץ (PDF או TXT) כדי להתחיל.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            sources_list = []

            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/octet-stream")}
            data = {"question": prompt, "filename": uploaded_file.name}

            try:
                with requests.post("http://127.0.0.1:8000/analyze", data=data, files=files, stream=True) as r:
                    if r.status_code == 200:
                        for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                            if chunk:
                                if chunk.startswith("SOURCES:"):
                                    raw_sources = chunk.split("---")[0].replace("SOURCES:", "").strip()
                                    sources_list = [s.strip() for s in raw_sources.split(",") if s.strip()]
                                    continue
                                full_response += chunk
                                message_placeholder.markdown(full_response + "▌")

                        final_text = full_response
                        if sources_list:
                            final_text += f"\n\n---\n**📄 מקורות:** {', '.join(sources_list)}"

                        message_placeholder.markdown(final_text)
                        st.session_state.messages.append({"role": "assistant", "content": final_text})
                    else:
                        st.error(f"שגיאת שרת: {r.status_code}")
            except Exception as e:
                st.error(f"שגיאת תקשורת: {e}")