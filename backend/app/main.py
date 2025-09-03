# backend/app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.utils.phishing_detector import predict_text
from app.utils.chatbot_retrieval import answer as answer_from_kb
from app.utils.chatbot_websearch import answer_from_web, fetch_web_results
import os

app = FastAPI(title="CyberGuard Assistant API")

class PhishRequest(BaseModel):
    text: str

class ChatRequest(BaseModel):
    question: str

@app.post("/api/phish/predict")
def phish_predict(req: PhishRequest):
    if not req.text:
        raise HTTPException(status_code=400, detail="text required")
    res = predict_text(req.text)
    return res

@app.post("/api/chat")
def chat(req: ChatRequest):
    """Fallback/local KB retrieval (faq JSON)."""
    if not req.question:
        raise HTTPException(status_code=400, detail="question required")
    results = answer_from_kb(req.question, top_k=3)
    return {"results": results}

@app.post("/api/chat_web")
def chat_web(req: ChatRequest):
    """Web-enabled chat: search web + summarize + return sources."""
    if not req.question:
        raise HTTPException(status_code=400, detail="question required")
    res = answer_from_web(req.question)
    return res

@app.get("/api/test_search")
def test_search(q: str):
    """Quick test endpoint to verify search API works (returns raw results)."""
    return {"results": fetch_web_results(q)}
