from fastapi import FastAPI
from pydantic import BaseModel
from agent import get_sentinel_response

app = FastAPI(title="Sentinel-AI Multi-Agent API")


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def health_check():
    # בדיקה שהשרת חי
    return {"status": "online", "agent": "Sentinel"}


@app.post("/ask")
async def ask_agent(request: ChatRequest):
    """
    Endpoint שמקבל שאלה ב-POST ומחזיר תשובה מהסוכן
    """
    # קריאה לפונקציה שכתבנו ב-agent.py
    answer = get_sentinel_response(request.question)

    return {
        "user_question": request.question,
        "agent_response": answer
    }