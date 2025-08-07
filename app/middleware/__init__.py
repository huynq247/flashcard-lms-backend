"""
Middleware configuration for the application.
"""
from app.middleware.security import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    RequestValidationMiddleware,
    CORSCustomMiddleware
)


def configure_middleware(app):
    """Configure all middleware for the application."""
    
    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
    
    # Add request validation middleware
    app.add_middleware(RequestValidationMiddleware, max_request_size=10*1024*1024)
    
    # Add custom CORS middleware
    app.add_middleware(
        CORSCustomMiddleware,
        allowed_origins=["http://localhost:3000", "http://localhost:8080", "http://localhost:4200"],
        allowed_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_credentials=True
    )
