import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Request
from fastapi.responses import StreamingResponse, JSONResponse
from app.core.processor import FileProcessor
from app.infrastructure.vector_store import vector_store
from app.core.engine import sentinel_rag_flow, generate_document_summary
import logging
from fastapi.responses import JSONResponse
# הגדרת לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Main")

app = FastAPI(title="Sentinel AI")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = str(exc)
    logger.error(f"Global Error Captured: {error_msg}")
    if "api_key" in error_msg.lower():
        return JSONResponse(status_code=401, content={"detail": "שגיאה במפתח ה-API. אנא בדקי את קובץ ה-env."})
    if "connection" in error_msg.lower():
        return JSONResponse(status_code=502, content={"detail": "שגיאת חיבור לרשת. ודאי שאין חסימה לשרתי OpenAI."})
    return JSONResponse(status_code=500, content={"detail": "קרתה שגיאה פנימית בשרת Sentinel."})


@app.get("/summary/{filename}")
async def get_summary(filename: str):
    summary = await generate_document_summary(filename)
    return {"summary": summary}


@app.post("/analyze")
async def analyze_file(
        question: str = Form(...),
        file: UploadFile = File(...)
):
    try:
        content = await file.read()
        if file.filename.endswith(".pdf"):
            chunks = await FileProcessor.process_pdf(content)
        elif file.filename.endswith(".txt"):
            chunks = await FileProcessor.process_txt(content)
        else:
            raise HTTPException(status_code=400, detail="סוג קובץ לא נתמך.")

        await vector_store.add_documents(chunks, file.filename)

        # קבלת התשובה והמקורות (ללא stream)
        answer, sources = await sentinel_rag_flow(question, file.filename)

        # החזרת התשובה כ-JSON
        return JSONResponse(content={"answer": answer, "sources": sources})

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    logger.info("Starting Sentinel AI Server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)