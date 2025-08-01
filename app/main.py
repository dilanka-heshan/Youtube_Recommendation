"""
Main application file for the Ethical Recommendation System API
Implements security, logging, and proper error handling
"""

import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn

from app.core.config import settings
from app.api import core_routes, youtube_routes
from app.models.schemas import ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Ethical Recommendation System API")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"YouTube API configured: {bool(settings.youtube_api_key)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Ethical Recommendation System API")


# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,  # Disable docs in production
    redoc_url="/redoc" if settings.debug else None
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
)

# CORS middleware with restricted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins if not settings.debug else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only allow necessary methods
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for monitoring"""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} in {process_time:.4f}s")
    
    return response


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP Error",
            message=exc.detail,
            status_code=exc.status_code,
            timestamp=time.time()
        ).dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Validation Error",
            message="Invalid request data",
            status_code=422,
            timestamp=time.time()
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            message="An unexpected error occurred",
            status_code=500,
            timestamp=time.time()
        ).dict()
    )


# Include routers
app.include_router(core_routes.router)
app.include_router(youtube_routes.router)


# Additional security endpoints
@app.get("/api-info", summary="API Information")
async def api_info():
    """Get API information and capabilities"""
    return {
        "api_name": settings.api_title,
        "version": settings.api_version,
        "features": [
            "Ethical recommendations",
            "Bias mitigation",
            "Privacy protection",
            "Rate limiting",
            "Content filtering"
        ],
        "endpoints": {
            "core": "/docs",
            "youtube": "/youtube/*",
            "health": "/health"
        },
        "security_features": [
            "Input validation",
            "Rate limiting",
            "Data anonymization",
            "CORS protection",
            "Request logging"
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
