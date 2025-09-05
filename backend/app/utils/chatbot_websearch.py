# backend/app/utils/chatbot_websearch.py
from duckduckgo_search import ddg
import requests
from bs4 import BeautifulSoup
import os

# optional HF summarizer or OpenAI usage
USE_HF = os.getenv("USE_HF_SUMMARIZER", "false").lower() == "true"
USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"

if USE_HF:
    from transformers import pipeline
    summarizer = pipeline("summarization", model=os.getenv("HF_MODEL", "facebook/bart-large-cnn"))

if USE_OPENAI:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")

def fetch_snippet(url):
    try:
        r = requests.get(url, timeout=4, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        # pull first few paragraphs
        ps = soup.find_all("p")
        text = " ".join([p.get_text() for p in ps[:4]])
        return text[:1000]
    except Exception:
        return ""

def summarize_text(text):
    if not text:
        return ""
    if USE_HF:
        s = summarizer(text, max_length=120, min_length=30, do_sample=False)
        return s[0]['summary_text']
    if USE_OPENAI:
        resp = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Summarize the following text in 2-3 concise sentences:\n\n{text}",
            max_tokens=150
        )
        return resp["choices"][0]["text"].strip()
    # fallback: take first 2 sentences
    return " ".join(text.split(".")[:2]) + "."

def websearch_and_summarize(query, max_results=4):
    results = ddg(query, max_results=max_results)
    sources = []
    snippets = []
    for r in results:
        title = r.get("title")
        link = r.get("href") or r.get("url")
        snippet = r.get("body") or ""
        if not snippet and link:
            snippet = fetch_snippet(link)
        if snippet:
            snippets.append(snippet)
        sources.append({"title": title, "link": link})
    combined = "\n\n".join(snippets)[:4000]
    summary = summarize_text(combined)
    return {"summary": summary, "sources": sources}
