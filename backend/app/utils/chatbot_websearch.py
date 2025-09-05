import asyncio
import aiohttp
import requests
import json
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from loguru import logger
import os
from duckduckgo_search import DDGS

class WebSearchChatbot:
    def __init__(self):
        self.summarizer = None
        self.tokenizer = None
        self.model = None
        self.max_search_results = 5
        self.max_content_length = 2000
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self._load_summarizer()
    
    def _load_summarizer(self):
        """Load AI model for summarization"""
        try:
            # Use a lightweight model for summarization
            model_name = "facebook/bart-large-cnn"
            logger.info(f"Loading summarization model: {model_name}")
            
            self.summarizer = pipeline(
                "summarization",
                model=model_name,
                tokenizer=model_name,
                max_length=150,
                min_length=30,
                do_sample=False
            )
            logger.info("Summarization model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading summarization model: {e}")
            logger.info("Falling back to extractive summarization")
            self.summarizer = None
    
    def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Search using DuckDuckGo API"""
        try:
            with DDGS() as ddgs:
                results = []
                # Add cybersecurity context to improve results
                enhanced_query = f"{query} cybersecurity security"
                
                for result in ddgs.text(enhanced_query, max_results=max_results):
                    results.append({
                        'title': result.get('title', ''),
                        'link': result.get('href', ''),
                        'snippet': result.get('body', '')
                    })
                
                logger.info(f"DuckDuckGo search returned {len(results)} results for: {query}")
                return results
                
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    def search_fallback(self, query: str) -> List[Dict[str, str]]:
        """Fallback search method using direct scraping (simplified)"""
        try:
            # This is a basic fallback - in production, you'd use proper APIs
            search_url = f"https://www.google.com/search?q={quote_plus(query)}+cybersecurity"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Extract search results (simplified)
            for g in soup.find_all('div', class_='g')[:3]:
                title_elem = g.find('h3')
                link_elem = g.find('a')
                snippet_elem = g.find('span', class_=['aCOpRe', 'st'])
                
                if title_elem and link_elem:
                    results.append({
                        'title': title_elem.get_text(),
                        'link': link_elem.get('href', ''),
                        'snippet': snippet_elem.get_text() if snippet_elem else ''
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Fallback search error: {e}")
            return []
    
    def fetch_page_content(self, url: str) -> str:
        """Fetch and extract main content from a webpage"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup