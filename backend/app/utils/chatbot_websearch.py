# backend/app/utils/chatbot_websearch.py
import os
import requests
from typing import List, Dict
from transformers import pipeline, Pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

# CONFIG via environment variables
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
# If you prefer Bing, replace the fetch_web_results implementation accordingly.

SERPAPI_SEARCH_URL = "https://serpapi.com/search"

# Load summarizer pipeline lazily (avoid heavy import at module import time if not used)
_summarizer: Pipeline = None

def _load_summarizer():
    global _summarizer
    if _summarizer is None:
        # Use a reasonably high-quality summarization model; change if you need smaller model
        model_name = os.getenv("SUMMARIZER_MODEL", "facebook/bart-large-cnn")
        _summarizer = pipeline("summarization", model=model_name)
    return _summarizer

def fetch_web_results(query: str, num_results: int = 3) -> List[Dict]:
    """
    Uses SerpAPI to fetch top organic results.
    Requires SERPAPI_KEY in env.
    Returns list of dicts: {title, snippet, link}
    """
    if not SERPAPI_KEY:
        raise RuntimeError("SERPAPI_KEY env var not set. Set it to use web search.")
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "num": num_results
    }
    resp = requests.get(SERPAPI_SEARCH_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    results = []
    # serpapi uses 'organic_results' widely; defensive checks
    for item in data.get("organic_results", [])[:num_results]:
        results.append({
            "title": item.get("title") or "",
            "snippet": item.get("snippet") or item.get("snippet_highlighted") or "",
            "link": item.get("link") or item.get("formatted_url") or ""
        })
    # fallback: use 'top_results' or 'knowledge_graph'
    if not results:
        for item in data.get("top_results", [])[:num_results]:
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "link": item.get("link", "")
            })
    return results

def summarize_text(text: str) -> str:
    if not text or text.strip() == "":
        return ""
    try:
        summarizer = _load_summarizer()
        # summarizer may fail on very short text; handle exceptions
        out = summarizer(text, max_length=130, min_length=30, do_sample=False)
        return out[0]["summary_text"].strip()
    except Exception as e:
        # if summarizer fails, return the original text (or a truncated snippet)
        truncated = (text[:800] + "...") if len(text) > 800 else text
        return truncated

def answer_from_web(question: str, num_results: int = 3) -> Dict:
    """
    - Fetches top results for `question`
    - Summarizes combined snippets with the summarizer
    - Returns summary + list of sources
    """
    results = fetch_web_results(question, num_results=num_results)
    combined_snippets = " ".join(r.get("snippet", "") for r in results)
    # If snippets small or empty, optionally fetch article texts (not implemented here).
    summary = summarize_text(combined_snippets) if combined_snippets else ""
    return {"summary": summary, "sources": results}
