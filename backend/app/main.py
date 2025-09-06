import os
import sys
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

# Logging
from loguru import logger
import uvicorn

# Local imports
from .models_api import (
    PhishingPredictionRequest, ChatRequest, BatchPhishingRequest,
    PhishingPredictionResponse, ChatResponse, BatchPhishingResponse,
    HealthCheckResponse, ErrorResponse, APIResponse, PredictionStats
)
from .utils.phishing_detector import get_detector, predict_phishing
from .utils.chatbot_websearch import get_chatbot, search_and_answer
from .utils.chatbot_retrieval import get_retrieval_chatbot, get_kb_response

# Global variables for tracking
app_start_time = datetime.now()
request_stats = {
    "phishing_requests": 0,
    "chat_requests": 0,
    "total_requests": 0,
    "error_count": 0
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting CyberGuard Assistant API...")
    
    # Initialize services
    try:
        # Load phishing detector
        detector = get_detector()
        logger.info("Phishing detector loaded successfully")
        
        # Initialize chatbot
        chatbot = get_chatbot()
        logger.info("Web search chatbot initialized")
        
        # Initialize retrieval chatbot
        retrieval_bot = get_retrieval_chatbot()
        logger.info("Knowledge base chatbot initialized")
        
        logger.info("CyberGuard Assistant API started successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        sys.exit(1)
    
    yield
    
    # Shutdown
    logger.info("Shutting down CyberGuard Assistant API...")

# Create FastAPI application
app = FastAPI(
    title="CyberGuard Assistant API",
    description="AI-powered cybersecurity assistant with phishing detection and awareness chatbot",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware for request tracking
@app.middleware("http")
async def track_requests(request, call_next):
    """Track API requests for statistics"""
    start_time = datetime.now()
    
    try:
        response = await call_next(request)
        
        # Update stats
        request_stats["total_requests"] += 1
        
        if request.url.path.startswith("/api/phish"):
            request_stats["phishing_requests"] += 1
        elif request.url.path.startswith("/api/chat"):
            request_stats["chat_requests"] += 1
        
        # Log request
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
        
        return response
        
    except Exception as e:
        request_stats["error_count"] += 1
        logger.error(f"Request error: {e}")
        raise

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "error": exc.detail,
                "code": exc.status_code,
                "timestamp": datetime.now().isoformat()
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "error": "Internal server error",
                "detail": str(exc),
                "code": 500,
                "timestamp": datetime.now().isoformat()
            }
        }
    )

# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check():
    """Check API health status"""
    try:
        detector = get_detector()
        model_loaded = detector.model is not None
        
        chatbot = get_chatbot()
        chatbot_ready = chatbot.summarizer is not None
        
        retrieval_bot = get_retrieval_chatbot()
        kb_ready = len(retrieval_bot.knowledge_base.get('faqs', [])) > 0
        
        return HealthCheckResponse(
            status="healthy" if all([model_loaded, chatbot_ready, kb_ready]) else "degraded",
            timestamp=datetime.now().isoformat(),
            model_loaded=model_loaded,
            services={
                "phishing_detector": model_loaded,
                "web_search_chatbot": chatbot_ready,
                "knowledge_base": kb_ready
            },
            version="1.0.0"
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

# Statistics endpoint
@app.get("/stats", response_model=PredictionStats, tags=["System"])
async def get_stats():
    """Get API usage statistics"""
    uptime = str(datetime.now() - app_start_time)
    
    return {
        "total_predictions": request_stats["phishing_requests"],
        "phishing_count": 0,  # Would need to track this separately
        "legitimate_count": 0,  # Would need to track this separately
        "average_confidence": 0.0,  # Would need to track this separately
        "high_risk_count": 0,  # Would need to track this separately
        "phishing_requests": request_stats["phishing_requests"],
        "chat_requests": request_stats["chat_requests"],
        "total_requests": request_stats["total_requests"],
        "error_count": request_stats["error_count"],
        "uptime": uptime
    }

# Phishing Detection Endpoints
@app.post("/api/phish/predict", response_model=PhishingPredictionResponse, tags=["Phishing Detection"])
async def predict_phishing_endpoint(request: PhishingPredictionRequest):
    """
    Predict if text is phishing or legitimate
    
    Analyzes the input text using machine learning to detect potential phishing attempts.
    Returns prediction, probability scores, and feature analysis.
    """
    try:
        logger.info(f"Phishing prediction request: {request.text[:100]}...")
        
        # Get prediction from detector
        result = predict_phishing(request.text)
        
        # Handle error in prediction
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Format response
        response_data = PhishingPredictionResponse(
            prediction=result["prediction"],
            probability=result["probability"],
            confidence=result["confidence"],
            risk_level=result.get("risk_level", "low"),
            features=result["features"] if request.include_features else None,
            raw_text=result["raw_text"],
            message=result.get("message")
        )
        
        logger.info(f"Prediction: {result['prediction']} (confidence: {result['confidence']:.3f})")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Phishing prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/api/phish/batch", response_model=BatchPhishingResponse, tags=["Phishing Detection"])
async def batch_predict_phishing(request: BatchPhishingRequest):
    """
    Batch prediction for multiple texts
    
    Analyzes multiple texts at once for phishing detection.
    Useful for processing multiple emails or messages simultaneously.
    """
    try:
        logger.info(f"Batch prediction request: {len(request.texts)} texts")
        
        detector = get_detector()
        results = detector.batch_predict(request.texts)
        
        # Format results
        formatted_results = []
        phishing_count = 0
        legitimate_count = 0
        
        for i, result in enumerate(results):
            if "error" not in result:
                if result["prediction"] == "phishing":
                    phishing_count += 1
                else:
                    legitimate_count += 1
                
                formatted_result = PhishingPredictionResponse(
                    prediction=result["prediction"],
                    probability=result["probability"],
                    confidence=result["confidence"],
                    risk_level=result.get("risk_level", "low"),
                    features=result["features"] if request.include_features else None,
                    raw_text=result["raw_text"]
                )
            else:
                # Handle individual errors
                formatted_result = PhishingPredictionResponse(
                    prediction="unknown",
                    probability={"legitimate": 0.5, "phishing": 0.5},
                    confidence=0.0,
                    risk_level="low",
                    raw_text=request.texts[i][:100],
                    error=result["error"]
                )
            
            formatted_results.append(formatted_result)
        
        summary = {
            "total": len(request.texts),
            "phishing": phishing_count,
            "legitimate": legitimate_count,
            "errors": len(request.texts) - phishing_count - legitimate_count
        }
        
        response = BatchPhishingResponse(
            results=formatted_results,
            total_processed=len(request.texts),
            summary=summary
        )
        
        logger.info(f"Batch prediction completed: {summary}")
        return response
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

# Chatbot Endpoints
@app.post("/api/chat/web", response_model=ChatResponse, tags=["Cybersecurity Chatbot"])
async def chat_web_search(request: ChatRequest):
    """
    Ask cybersecurity questions with web search
    
    Searches the web for current cybersecurity information and provides
    AI-summarized answers with source references.
    """
    try:
        logger.info(f"Web search chat request: {request.query}")
        
        if request.use_web_search:
            # Use web search
            chatbot = get_chatbot()
            result = chatbot.search_and_summarize_sync(request.query)
            
            response = ChatResponse(
                summary=result["summary"],
                sources=result.get("sources", []),
                query=result["query"],
                status=result["status"],
                search_count=result.get("search_count"),
                error=result.get("error")
            )
        else:
            # Use local knowledge base
            retrieval_bot = get_retrieval_chatbot()
            result = retrieval_bot.get_response(request.query)
            
            # Convert KB response to ChatResponse format
            sources = []
            if result.get("source") == "knowledge_base":
                sources = [{"title": "Knowledge Base", "link": "", "snippet": result["answer"][:200]}]
            
            response = ChatResponse(
                summary=result["answer"],
                sources=sources,
                query=result["question"],
                status=result["status"],
                confidence=result.get("confidence"),
                keywords=result.get("keywords", []),
                suggestions=result.get("suggestions", []),
                error=result.get("error")
            )
        
        logger.info(f"Chat response generated for: {request.query}")
        return response
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat request failed: {str(e)}")

@app.post("/api/chat/kb", response_model=ChatResponse, tags=["Cybersecurity Chatbot"])
async def chat_knowledge_base(request: ChatRequest):
    """
    Ask questions using local knowledge base
    
    Searches the local cybersecurity knowledge base for answers.
    Faster than web search but limited to pre-stored information.
    """
    try:
        logger.info(f"Knowledge base chat request: {request.query}")
        
        result = get_kb_response(request.query)
        
        # Convert KB response to ChatResponse format
        sources = []
        if result.get("source") == "knowledge_base":
            sources = [{"title": "CyberGuard Knowledge Base", "link": "", "snippet": result["answer"][:200]}]
        
        response = ChatResponse(
            summary=result["answer"],
            sources=sources,
            query=request.query,
            status=result["status"],
            confidence=result.get("confidence"),
            keywords=result.get("keywords", []),
            suggestions=result.get("suggestions", []),
            error=result.get("error")
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Knowledge base chat error: {e}")
        raise HTTPException(status_code=500, detail=f"KB chat request failed: {str(e)}")

# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """API root endpoint"""
    return {
        "message": "CyberGuard Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "active"
    }

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="CyberGuard Assistant API",
        version="1.0.0",
        description="AI-powered cybersecurity assistant providing phishing detection and cybersecurity awareness through web search and local knowledge base.",
        routes=app.routes,
    )
    
    # Add custom schema information
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Development server
if __name__ == "__main__":
    logger.info("Starting CyberGuard Assistant API in development mode...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )