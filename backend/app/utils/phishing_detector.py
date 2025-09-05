"""
Phishing Detection Utility
Loads trained model and provides prediction capabilities with feature analysis.
"""

import os
import re
import joblib
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse
from loguru import logger
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class PhishingDetector:
    def __init__(self, model_path: str = "models/phish_model.joblib"):
        self.model = None
        self.model_path = model_path
        self.stop_words = set()
        self.load_model()
        self._setup_nltk()
    
    def _setup_nltk(self):
        """Setup NLTK dependencies"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            self.stop_words = set(stopwords.words('english'))
        except Exception as e:
            logger.warning(f"Could not setup NLTK: {e}")
            self.stop_words = set()
    
    def load_model(self):
        """Load the trained phishing detection model"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                logger.info(f"Model loaded successfully from {self.model_path}")
            else:
                logger.error(f"Model file not found: {self.model_path}")
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for prediction"""
        if not isinstance(text, str) or not text.strip():
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs, emails, and special characters
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ', text)
        text = re.sub(r'\S+@\S+', ' ', text)
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove stopwords
        try:
            tokens = word_tokenize(text)
            tokens = [word for word in tokens if word not in self.stop_words and len(word) > 2]
            text = ' '.join(tokens)
        except:
            pass
        
        return text
    
    def extract_url_features(self, text: str) -> Dict[str, any]:
        """Extract URL-based features that might indicate phishing"""
        features = {}
        
        # Find URLs in text
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        
        features['url_count'] = len(urls)
        features['has_suspicious_url'] = False
        features['suspicious_domains'] = []
        
        if urls:
            for url in urls:
                try:
                    parsed = urlparse(url)
                    domain = parsed.netloc.lower()
                    
                    # Check for suspicious patterns
                    suspicious_patterns = [
                        # IP addresses instead of domains
                        r'\d+\.\d+\.\d+\.\d+',
                        # Suspicious TLDs
                        r'\.(tk|ml|ga|cf)$',
                        # URL shorteners (could be suspicious)
                        r'(bit\.ly|tinyurl|t\.co|goo\.gl|ow\.ly)',
                        # Common phishing domain patterns
                        r'(secure|verify|update|confirm|account).*\.(com|net|org)',
                        # Typosquatting patterns for major services
                        r'(paypaI|arnazon|googIe|microsooft|appIe)',  # Using capital I instead of l
                    ]
                    
                    for pattern in suspicious_patterns:
                        if re.search(pattern, domain):
                            features['has_suspicious_url'] = True
                            features['suspicious_domains'].append(domain)
                            break
                    
                except Exception:
                    continue
        
        return features
    
    def extract_text_features(self, text: str) -> Dict[str, any]:
        """Extract text-based features that might indicate phishing"""
        features = {}
        
        text_lower = text.lower()
        
        # Urgency indicators
        urgency_words = [
            'urgent', 'immediate', 'expires', 'limited time', 'act now', 'hurry',
            'final notice', 'last chance', 'expires today', 'deadline'
        ]
        features['urgency_score'] = sum(1 for word in urgency_words if word in text_lower)
        
        # Financial/reward indicators
        financial_words = [
            'money', 'prize', 'reward', 'cash', 'free', 'win', 'winner', 'lottery',
            'million', 'thousand', 'dollars', '$', 'payment', 'refund'
        ]
        features['financial_score'] = sum(1 for word in financial_words if word in text_lower)
        
        # Threat/fear indicators
        threat_words = [
            'suspend', 'block', 'close', 'terminated', 'legal action', 'arrest',
            'fine', 'penalty', 'lawsuit', 'court', 'police', 'investigation'
        ]
        features['threat_score'] = sum(1 for word in threat_words if word in text_lower)
        
        # Action request indicators
        action_words = [
            'click', 'verify', 'confirm', 'update', 'download', 'install',
            'provide', 'send', 'submit', 'enter', 'login', 'sign in'
        ]
        features['action_score'] = sum(1 for word in action_words if word in text_lower)
        
        # Spelling/grammar issues (simple heuristic)
        # Count excessive punctuation
        features['excessive_punctuation'] = len(re.findall(r'[!?]{2,}', text))
        
        # Count ALL CAPS words
        words = text.split()
        caps_words = [w for w in words if w.isupper() and len(w) > 2]
        features['caps_words_count'] = len(caps_words)
        
        # Text length
        features['text_length'] = len(text)
        features['word_count'] = len(words)
        
        return features
    
    def analyze_features(self, text: str) -> Dict[str, any]:
        """Comprehensive feature analysis of input text"""
        url_features = self.extract_url_features(text)
        text_features = self.extract_text_features(text)
        
        # Combine all features
        features = {**url_features, **text_features}
        
        # Calculate overall suspicion score (0-1)
        suspicion_factors = [
            features.get('urgency_score', 0) * 0.2,
            features.get('financial_score', 0) * 0.15,
            features.get('threat_score', 0) * 0.25,
            features.get('action_score', 0) * 0.1,
            (1 if features.get('has_suspicious_url', False) else 0) * 0.3
        ]
        
        features['suspicion_score'] = min(sum(suspicion_factors), 1.0)
        
        return features
    
    def predict(self, text: str) -> Dict[str, any]:
        """
        Predict if text is phishing or legitimate
        
        Returns:
            Dict containing prediction, probability, and feature analysis
        """
        try:
            if not self.model:
                raise RuntimeError("Model not loaded")
            
            if not isinstance(text, str) or not text.strip():
                raise ValueError("Invalid input: text cannot be empty")
            
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            if not processed_text:
                return {
                    "prediction": "legitimate",
                    "probability": {"phishing": 0.1, "legitimate": 0.9},
                    "confidence": 0.9,
                    "features": self.analyze_features(text),
                    "raw_text": text[:100] + "..." if len(text) > 100 else text,
                    "message": "Text appears empty after preprocessing"
                }
            
            # Get model prediction
            prediction = self.model.predict([processed_text])[0]
            probabilities = self.model.predict_proba([processed_text])[0]
            
            # Extract feature analysis
            features = self.analyze_features(text)
            
            # Format results
            result = {
                "prediction": "phishing" if prediction == 1 else "legitimate",
                "probability": {
                    "legitimate": float(probabilities[0]),
                    "phishing": float(probabilities[1])
                },
                "confidence": float(max(probabilities)),
                "features": features,
                "raw_text": text[:100] + "..." if len(text) > 100 else text,
                "risk_level": self._calculate_risk_level(probabilities[1], features)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return {
                "error": str(e),
                "prediction": "unknown",
                "probability": {"phishing": 0.5, "legitimate": 0.5},
                "confidence": 0.0,
                "features": {},
                "raw_text": text[:100] + "..." if len(text) > 100 else text
            }
    
    def _calculate_risk_level(self, phishing_prob: float, features: Dict) -> str:
        """Calculate risk level based on probability and features"""
        # Base risk on ML model probability
        if phishing_prob >= 0.8:
            base_risk = "high"
        elif phishing_prob >= 0.6:
            base_risk = "medium"
        elif phishing_prob >= 0.4:
            base_risk = "low"
        else:
            base_risk = "very_low"
        
        # Adjust based on feature analysis
        suspicion_score = features.get('suspicion_score', 0)
        
        if suspicion_score >= 0.7 and base_risk in ["low", "very_low"]:
            base_risk = "medium"
        elif suspicion_score >= 0.5 and base_risk == "very_low":
            base_risk = "low"
        
        return base_risk
    
    def batch_predict(self, texts: List[str]) -> List[Dict[str, any]]:
        """Predict multiple texts at once"""
        results = []
        for text in texts:
            result = self.predict(text)
            results.append(result)
        return results

# Global detector instance
_detector_instance = None

def get_detector() -> PhishingDetector:
    """Get singleton detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = PhishingDetector()
    return _detector_instance

def predict_phishing(text: str) -> Dict[str, any]:
    """Convenience function for phishing prediction"""
    detector = get_detector()
    return detector.predict(text)