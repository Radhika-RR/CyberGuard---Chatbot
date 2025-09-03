# backend/app/utils/chatbot_retrieval.py
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "kb.json")
_vectorizer = None
_question_vectors = None
_kb = None

def load_kb():
    global _kb, _vectorizer, _question_vectors
    if _kb is None:
        if not os.path.exists(KB_PATH):
            _kb = []
            _vectorizer = None
            _question_vectors = None
            return _kb
        with open(KB_PATH, "r", encoding="utf8") as f:
            _kb = json.load(f)
        questions = [item.get("q", "") for item in _kb]
        if questions:
            _vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=10000)
            _question_vectors = _vectorizer.fit_transform(questions)
    return _kb

def answer(question: str, top_k: int = 1):
    kb = load_kb()
    if not kb:
        return []
    q_vec = _vectorizer.transform([question])
    sims = cosine_similarity(q_vec, _question_vectors)[0]
    ranked_idx = sims.argsort()[::-1][:top_k]
    results = []
    for idx in ranked_idx:
        results.append({"q": kb[idx]["q"], "a": kb[idx]["a"], "score": float(sims[idx])})
    return results
