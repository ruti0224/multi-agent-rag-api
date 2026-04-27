from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from agent import get_sentinel_response, clear_chat_history
from vector_manager import vector_db
from fastapi.middleware.cors import CORSMiddleware
from config import MAX_FILE_SIZE_BYTES
import io
import logging
from pypdf import PdfReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sentinel Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze")
async def analyze_file(question: str = Form(...), file: UploadFile = File(...)):
    if file_extension == ".pdf":
        pdf_reader = PdfReader(io.BytesIO(content))
        text = "".join([page.extract_text() or "" for page in pdf_reader.pages])


    try:
        content = await file.read()
        if file.filename.endswith(".pdf"):
            pdf_reader = PdfReader(io.BytesIO(content))
            text = "".join([p.extract_text() for p in pdf_reader.pages])
        if not text.strip():
            logger.error("The PDF appears to be an image or contains no readable text")
            raise HTTPException(400, "לא ניתן לקרוא טקסט מה-PDF. ודא שהקובץ אינו סרוק כתמונה.")
        else:
            text = content.decode("utf-8")

        # שימוש במופע הנקי של ה-Vector DB
        vector_db.process_and_store(text)
        context = vector_db.query_database(question)
        answer = get_sentinel_response(question, context)

        return {"answer": answer, "status": "success"}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(500, str(e))


@app.post("/reset")
async def reset():
    clear_chat_history()
    vector_db.clear_database()
    return {"status": "Reset successful"}


@app.get("/health")
async def health():
    return {"status": "healthy"}