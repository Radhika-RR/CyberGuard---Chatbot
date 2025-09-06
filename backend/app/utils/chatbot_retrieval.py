import json
import os
from typing import Dict, List, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from loguru import logger
import re

class ChatbotRetrieval:
    def __init__(self, kb_path: str = "app/data/kb.json"):
        self.kb_path = kb_path
        self.knowledge_base = {}
        self.vectorizer = None
        self.question_vectors = None
        self.questions = []
        self.load_knowledge_base()
        self.setup_retrieval_system()
    
    def load_knowledge_base(self):
        """Load knowledge base from JSON file"""
        try:
            if os.path.exists(self.kb_path):
                with open(self.kb_path, 'r', encoding='utf-8') as f:
                    self.knowledge_base = json.load(f)
                logger.info(f"Knowledge base loaded: {len(self.knowledge_base.get('faqs', []))} entries")
            else:
                logger.warning(f"Knowledge base not found at {self.kb_path}, creating default")
                self.knowledge_base = self.create_default_kb()
                self.save_knowledge_base()
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            self.knowledge_base = self.create_default_kb()
    
    def create_default_kb(self) -> Dict:
        """Create default cybersecurity knowledge base"""
        return {
            "faqs": [
                {
                    "question": "How to detect phishing emails?",
                    "answer": "Look for suspicious sender addresses, urgent language, requests for personal information, unexpected attachments, and links to unfamiliar websites. Always verify sender identity through a separate channel.",
                    "keywords": ["phishing", "email", "detect", "suspicious", "scam"]
                },
                {
                    "question": "What is two-factor authentication?",
                    "answer": "Two-factor authentication (2FA) is a security method that requires two different verification factors: something you know (password) and something you have (phone, token, or app). It significantly increases account security.",
                    "keywords": ["2FA", "two-factor", "authentication", "security", "password"]
                },
                {
                    "question": "How to create strong passwords?",
                    "answer": "Use at least 12 characters with a mix of uppercase, lowercase, numbers, and symbols. Avoid personal information, use unique passwords for each account, and consider using a password manager.",
                    "keywords": ["password", "strong", "secure", "create", "characters"]
                },
                {
                    "question": "What is malware?",
                    "answer": "Malware is malicious software designed to harm, exploit, or gain unauthorized access to computer systems. Types include viruses, trojans, ransomware, spyware, and adware.",
                    "keywords": ["malware", "virus", "trojan", "ransomware", "spyware", "malicious"]
                },
                {
                    "question": "How to secure WiFi networks?",
                    "answer": "Use WPA3 or WPA2 encryption, change default router passwords, use strong network passwords, disable WPS, enable network firewalls, and regularly update router firmware.",
                    "keywords": ["wifi", "wireless", "network", "secure", "encryption", "router"]
                },
                {
                    "question": "What is social engineering?",
                    "answer": "Social engineering is the psychological manipulation of people to divulge confidential information or perform actions that compromise security. Common tactics include phishing, pretexting, and baiting.",
                    "keywords": ["social", "engineering", "manipulation", "psychological", "tactics"]
                },
                {
                    "question": "How to backup data safely?",
                    "answer": "Follow the 3-2-1 rule: 3 copies of data, 2 different storage types, 1 offsite backup. Use encrypted backups, test restoration regularly, and automate the process when possible.",
                    "keywords": ["backup", "data", "safe", "storage", "encryption", "restore"]
                },
                {
                    "question": "What is a VPN and why use it?",
                    "answer": "A VPN (Virtual Private Network) creates an encrypted connection between your device and a server, protecting your data and privacy. Use it on public WiFi, for privacy, or to access geo-restricted content.",
                    "keywords": ["VPN", "virtual", "private", "network", "encrypted", "privacy"]
                },
                {
                    "question": "How to recognize fake websites?",
                    "answer": "Check for HTTPS, verify URLs carefully, look for spelling errors, check domain age and reputation, be wary of too-good-to-be-true offers, and use website reputation tools.",
                    "keywords": ["fake", "website", "recognize", "scam", "fraudulent", "suspicious"]
                },
                {
                    "question": "What to do if hacked?",
                    "answer": "Immediately change all passwords, enable 2FA, check account activities, run antivirus scans, monitor financial accounts, report to relevant authorities, and consider professional help.",
                    "keywords": ["hacked", "compromised", "breach", "response", "recovery", "help"]
                }
            ],
            "categories": [
                "phishing",
                "authentication",
                "passwords",
                "malware",
                "network_security",
                "social_engineering",
                "data_protection",
                "privacy",
                "incident_response"
            ]
        }
    
    def save_knowledge_base(self):
        """Save knowledge base to file"""
        try:
            os.makedirs(os.path.dirname(self.kb_path), exist_ok=True)
            with open(self.kb_path, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
            logger.info(f"Knowledge base saved to {self.kb_path}")
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
    
    def setup_retrieval_system(self):
        """Setup TF-IDF based retrieval system"""
        try:
            faqs = self.knowledge_base.get('faqs', [])
            if not faqs:
                logger.warning("No FAQs found in knowledge base")
                return
            
            # Combine questions and keywords for better matching
            self.questions = []
            texts_for_vectorization = []
            
            for faq in faqs:
                question = faq.get('question', '')
                keywords = ' '.join(faq.get('keywords', []))
                combined_text = f"{question} {keywords}"
                
                self.questions.append(faq)
                texts_for_vectorization.append(combined_text.lower())
            
            # Create TF-IDF vectors
            self.vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                max_features=1000
            )
            
            self.question_vectors = self.vectorizer.fit_transform(texts_for_vectorization)
            logger.info(f"Retrieval system setup complete with {len(self.questions)} questions")
            
        except Exception as e:
            logger.error(f"Error setting up retrieval system: {e}")
            self.vectorizer = None
            self.question_vectors = None
    
    def preprocess_query(self, query: str) -> str:
        """Clean and preprocess user query"""
        # Remove special characters and normalize
        query = re.sub(r'[^\w\s]', ' ', query)
        query = ' '.join(query.split())  # Remove extra whitespace
        return query.lower()
    
    def find_best_match(self, query: str, threshold: float = 0.1) -> Optional[Tuple[Dict, float]]:
        """Find the best matching FAQ for the query"""
        if not self.vectorizer or not self.question_vectors.any():
            return None
        
        try:
            # Preprocess query
            processed_query = self.preprocess_query(query)
            
            # Vectorize query
            query_vector = self.vectorizer.transform([processed_query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.question_vectors).flatten()
            
            # Find best match
            best_idx = np.argmax(similarities)
            best_score = similarities[best_idx]
            
            if best_score >= threshold:
                return self.questions[best_idx], best_score
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error finding best match: {e}")
            return None
    
    def get_response(self, query: str) -> Dict[str, any]:
        """Get response from knowledge base"""
        try:
            # Find best matching FAQ
            match = self.find_best_match(query)
            
            if match:
                faq, confidence = match
                return {
                    "answer": faq.get('answer', ''),
                    "question": faq.get('question', ''),
                    "confidence": float(confidence),
                    "source": "knowledge_base",
                    "keywords": faq.get('keywords', []),
                    "status": "success"
                }
            else:
                # No good match found
                return {
                    "answer": "I don't have specific information about that topic in my knowledge base. Please try rephrasing your question or use the web search feature for more comprehensive results.",
                    "question": query,
                    "confidence": 0.0,
                    "source": "knowledge_base",
                    "keywords": [],
                    "status": "no_match",
                    "suggestions": self.get_suggestions()
                }
                
        except Exception as e:
            logger.error(f"Error getting response: {e}")
            return {
                "answer": "I'm sorry, I encountered an error while processing your question.",
                "question": query,
                "confidence": 0.0,
                "source": "knowledge_base",
                "status": "error",
                "error": str(e)
            }
    
    def get_suggestions(self) -> List[str]:
        """Get suggestion questions from knowledge base"""
        try:
            faqs = self.knowledge_base.get('faqs', [])
            suggestions = [faq.get('question', '') for faq in faqs[:5]]  # Top 5 questions
            return [q for q in suggestions if q]  # Filter empty questions
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            return []
    
    def add_faq(self, question: str, answer: str, keywords: List[str] = None) -> bool:
        """Add new FAQ to knowledge base"""
        try:
            if not question or not answer:
                return False
            
            new_faq = {
                "question": question,
                "answer": answer,
                "keywords": keywords or []
            }
            
            self.knowledge_base.setdefault('faqs', []).append(new_faq)
            self.save_knowledge_base()
            
            # Refresh retrieval system
            self.setup_retrieval_system()
            
            logger.info(f"Added new FAQ: {question[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error adding FAQ: {e}")
            return False
    
    def search_faqs(self, keyword: str) -> List[Dict]:
        """Search FAQs by keyword"""
        try:
            results = []
            keyword_lower = keyword.lower()
            
            for faq in self.knowledge_base.get('faqs', []):
                question = faq.get('question', '').lower()
                answer = faq.get('answer', '').lower()
                keywords = [k.lower() for k in faq.get('keywords', [])]
                
                if (keyword_lower in question or 
                    keyword_lower in answer or 
                    keyword_lower in keywords):
                    results.append(faq)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching FAQs: {e}")
            return []

# Global retrieval instance
_retrieval_instance = None

def get_retrieval_chatbot() -> ChatbotRetrieval:
    """Get singleton retrieval chatbot instance"""
    global _retrieval_instance
    if _retrieval_instance is None:
        _retrieval_instance = ChatbotRetrieval()
    return _retrieval_instance

def get_kb_response(query: str) -> Dict[str, any]:
    """Convenience function for knowledge base retrieval"""
    chatbot = get_retrieval_chatbot()
    return chatbot.get_response(query)