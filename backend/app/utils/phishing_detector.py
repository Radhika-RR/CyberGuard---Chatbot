# backend/app/utils/phishing_detector.py
import os
import joblib
from urllib.parse import urlparse
import re

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "models", "phish_model.joblib")
_model = None

def load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Train and save it first.")
        _model = joblib.load(MODEL_PATH)
    return _model

def url_features(url_text: str) -> dict:
    parsed = urlparse(url_text)
    hostname = parsed.hostname or ""
    return {
        "length": len(url_text),
        "num_digits": sum(c.isdigit() for c in url_text),
        "has_at": "@" in url_text,
        "has_ip": bool(re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", url_text)),
        "dots": url_text.count("."),
        "hostname_len": len(hostname)
    }

def predict_text(text: str):
    model = load_model()
    try:
        proba = None
        if hasattr(model, "predict_proba"):
            proba = float(model.predict_proba([text])[0][1])
            pred = int(proba >= 0.5)
        else:
            pred = int(model.predict([text])[0])
        return {
            "prediction": "phishing" if pred == 1 else "legit",
            "probability": proba,
            "features": url_features(text)
        }
    except Exception as e:
        # fallback: if model fails, return neutral info
        return {"prediction": "unknown", "probability": None, "features": url_features(text), "error": str(e)}
