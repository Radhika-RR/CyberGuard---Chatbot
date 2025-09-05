# backend/app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from app.utils.phishing_detector import PhishingDetector
from app.utils.chatbot_websearch import websearch_and_summarize
import os

app = FastAPI(title="CyberGuard Assistant API")

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # set your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# load detector once
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
detector = PhishingDetector(model_path=os.path.join(BASE_DIR, "..", "..", "phish_model.joblib"),
                            vec_path=os.path.join(BASE_DIR, "..", "..", "vectorizer.joblib"))

class PhishRequest(BaseModel):
    text: str

class ChatRequest(BaseModel):
    question: str

@app.post("/api/phish/predict")
def phish_predict(req: PhishRequest):
    if not req.text:
        raise HTTPException(status_code=400, detail="text required")
    result = detector.predict(req.text)
    return result

@app.post("/api/chat_web")
def chat_web(req: ChatRequest):
    if not req.question:
        raise HTTPException(status_code=400, detail="question required")
    out = websearch_and_summarize(req.question)
    return out

@app.get("/health")
def health():
    return {"status": "ok"}
