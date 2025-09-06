

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any, Union
from enum import Enum

# Enums for standardized values
class PredictionResult(str, Enum):
    PHISHING = "phishing"
    LEGITIMATE = "legitimate"
    UNKNOWN = "unknown"

class RiskLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    NO_RESULTS = "no_results"
    NO_MATCH = "no_match"

# Request Models
class PhishingPredictionRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="Text to analyze for phishing")
    include_features: bool = Field(default=True, description="Whether to include feature analysis")
    
    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="User question about cybersecurity")
    use_web_search: bool = Field(default=True, description="Whether to use web search or local KB")
    max_results: int = Field(default=5, ge=1, le=10, description="Maximum number of search results")
    
    @validator('query')
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

class BatchPhishingRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=50, description="List of texts to analyze")
    include_features: bool = Field(default=False, description="Whether to include feature analysis")

# Response Models
class ProbabilityScore(BaseModel):
    legitimate: float = Field(..., ge=0.0, le=1.0, description="Probability of being legitimate")
    phishing: float = Field(..., ge=0.0, le=1.0, description="Probability of being phishing")

class FeatureAnalysis(BaseModel):
    # URL features
    url_count: int = Field(default=0, description="Number of URLs found")
    has_suspicious_url: bool = Field(default=False, description="Whether suspicious URLs detected")
    suspicious_domains: List[str] = Field(default=[], description="List of suspicious domains")
    
    # Text features
    urgency_score: int = Field(default=0, description="Urgency indicator score")
    financial_score: int = Field(default=0, description="Financial/reward indicator score")
    threat_score: int = Field(default=0, description="Threat/fear indicator score")
    action_score: int = Field(default=0, description="Action request indicator score")
    excessive_punctuation: int = Fiel