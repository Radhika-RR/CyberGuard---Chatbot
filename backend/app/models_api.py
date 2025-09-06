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
    excessive_punctuation: int = Field(default=0, description="Count of excessive punctuation")
    caps_words_count: int = Field(default=0, description="Count of ALL CAPS words")
    text_length: int = Field(default=0, description="Total text length")
    word_count: int = Field(default=0, description="Total word count")
    suspicion_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall suspicion score")

class Source(BaseModel):
    title: str = Field(..., description="Title of the source")
    link: str = Field(..., description="URL of the source")
    snippet: Optional[str] = Field(default="", description="Brief excerpt from the source")

class PhishingPredictionResponse(BaseModel):
    prediction: PredictionResult = Field(..., description="Classification result")
    probability: ProbabilityScore = Field(..., description="Prediction probabilities")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    risk_level: RiskLevel = Field(..., description="Risk assessment level")
    features: Optional[FeatureAnalysis] = Field(default=None, description="Feature analysis details")
    raw_text: str = Field(..., description="Input text (truncated)")
    message: Optional[str] = Field(default=None, description="Additional information")
    error: Optional[str] = Field(default=None, description="Error message if any")

class ChatResponse(BaseModel):
    summary: str = Field(..., description="AI-generated summary of the answer")
    sources: List[Source] = Field(default=[], description="Source references")
    query: str = Field(..., description="Original user query")
    status: ResponseStatus = Field(..., description="Response status")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Response confidence")
    search_count: Optional[int] = Field(default=None, description="Number of search results processed")
    keywords: Optional[List[str]] = Field(default=[], description="Relevant keywords")
    suggestions: Optional[List[str]] = Field(default=[], description="Suggested questions")
    error: Optional[str] = Field(default=None, description="Error message if any")

class BatchPhishingResponse(BaseModel):
    results: List[PhishingPredictionResponse] = Field(..., description="List of prediction results")
    total_processed: int = Field(..., description="Total number of texts processed")
    summary: Dict[str, int] = Field(..., description="Summary statistics")

class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    timestamp: str = Field(..., description="Check timestamp")
    model_loaded: bool = Field(..., description="Whether ML model is loaded")
    services: Dict[str, bool] = Field(..., description="Individual service statuses")
    version: str = Field(..., description="API version")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    code: Optional[int] = Field(default=None, description="Error code")
    timestamp: str = Field(..., description="Error timestamp")

# Statistics and Analytics Models
class PredictionStats(BaseModel):
    total_predictions: int = Field(..., description="Total predictions made")
    phishing_count: int = Field(..., description="Number of phishing predictions")
    legitimate_count: int = Field(..., description="Number of legitimate predictions")
    average_confidence: float = Field(..., description="Average confidence score")
    high_risk_count: int = Field(..., description="Number of high-risk predictions")

class APIUsageStats(BaseModel):
    phishing_requests: int = Field(..., description="Number of phishing detection requests")
    chat_requests: int = Field(..., description="Number of chat requests")
    total_requests: int = Field(..., description="Total API requests")
    error_count: int = Field(..., description="Number of errors")
    uptime: str = Field(..., description="Service uptime")

# Configuration Models
class ModelConfig(BaseModel):
    model_path: str = Field(..., description="Path to the ML model file")
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Classification threshold")
    max_text_length: int = Field(default=10000, description="Maximum input text length")
    batch_size: int = Field(default=50, description="Maximum batch processing size")

class SearchConfig(BaseModel):
    max_results: int = Field(default=5, description="Maximum search results")
    timeout: int = Field(default=10, description="Search timeout in seconds")
    use_cache: bool = Field(default=True, description="Whether to use response caching")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")

# Utility Models for API Documentation
class ExampleTexts(BaseModel):
    phishing_examples: List[str] = Field(
        default=[
            "Urgent! Your account will be suspended. Click here to verify immediately.",
            "Congratulations! You've won $10,000. Send your details to claim.",
            "Your PayPal has been limited. Update at paypal-security.com"
        ],
        description="Example phishing texts"
    )
    legitimate_examples: List[str] = Field(
        default=[
            "Thank you for your purchase. Your order will arrive in 3-5 days.",
            "Your appointment with Dr. Smith is confirmed for tomorrow.",
            "Welcome to our newsletter. Please confirm your subscription."
        ],
        description="Example legitimate texts"
    )

class SupportedQueries(BaseModel):
    cybersecurity_topics: List[str] = Field(
        default=[
            "How to detect phishing emails?",
            "What is two-factor authentication?",
            "How to create strong passwords?",
            "What is malware protection?",
            "How to secure WiFi networks?"
        ],
        description="Supported cybersecurity question types"
    )

# Request/Response wrapper for consistent API format
class APIResponse(BaseModel):
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[Union[
        PhishingPredictionResponse,
        ChatResponse,
        BatchPhishingResponse,
        HealthCheckResponse,
        PredictionStats,
        APIUsageStats
    ]] = Field(default=None, description="Response data")
    error: Optional[ErrorResponse] = Field(default=None, description="Error details if any")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

class APIRequest(BaseModel):
    request_id: Optional[str] = Field(default=None, description="Unique request identifier")
    timestamp: Optional[str] = Field(default=None, description="Request timestamp")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    
    class Config:
        # Allow extra fields for future extensibility
        extra = "allow"