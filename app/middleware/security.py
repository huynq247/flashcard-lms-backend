"""
Security middleware for rate limiting and request validation.
"""
import time
from typing import Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent abuse.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
        self.cleanup_interval = 300  # Clean up old entries every 5 minutes
        self.last_cleanup = time.time()
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Clean up old entries periodically
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_requests()
            self.last_cleanup = current_time
        
        # Check rate limit
        if self._is_rate_limited(client_ip):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded: {self.requests_per_minute} requests per minute",
                    "retry_after": 60
                }
            )
        
        # Record request
        self._record_request(client_ip)
        
        # Process request
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        # Check for forwarded IP (when behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP (when behind proxy)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Use client host
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client IP is rate limited."""
        now = time.time()
        minute_ago = now - 60
        
        # Count requests in the last minute
        recent_requests = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]
        
        return len(recent_requests) >= self.requests_per_minute
    
    def _record_request(self, client_ip: str):
        """Record a request from client IP."""
        now = time.time()
        self.requests[client_ip].append(now)
    
    def _cleanup_old_requests(self):
        """Remove old request records to prevent memory buildup."""
        cutoff_time = time.time() - 3600  # Keep records for 1 hour
        
        for client_ip in list(self.requests.keys()):
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if req_time > cutoff_time
            ]
            
            # Remove empty entries
            if not self.requests[client_ip]:
                del self.requests[client_ip]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to responses.
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Remove server header for security
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request validation and sanitization.
    """
    
    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 10MB
        super().__init__(app)
        self.max_request_size = max_request_size
    
    async def dispatch(self, request: Request, call_next):
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "detail": f"Request too large. Maximum size: {self.max_request_size} bytes"
                }
            )
        
        # Validate content type for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            allowed_types = [
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data"
            ]
            
            if not any(allowed_type in content_type for allowed_type in allowed_types):
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={
                        "detail": f"Unsupported media type: {content_type}"
                    }
                )
        
        # Check for suspicious user agents
        user_agent = request.headers.get("user-agent", "").lower()
        suspicious_agents = ["bot", "crawler", "spider", "scraper"]
        
        # Allow legitimate bots but log suspicious activity
        if any(agent in user_agent for agent in suspicious_agents):
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Suspicious user agent detected: {user_agent} from {request.client.host}")
        
        response = await call_next(request)
        return response


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for JWT token validation on protected routes.
    """
    
    def __init__(self, app, protected_paths: Optional[list] = None):
        super().__init__(app)
        # Paths that require authentication
        self.protected_paths = protected_paths or [
            "/api/v1/auth/me",
            "/api/v1/auth/logout",
            "/api/v1/auth/change-password",
            "/api/v1/decks",
            "/api/v1/classes",
            "/api/v1/courses",
            "/api/v1/study",
            "/api/v1/admin",
            "/api/v1/teacher"
        ]
        
        # Paths that don't require authentication
        self.public_paths = [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/api/v1/health",
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/auth/refresh"
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Check if path requires authentication
        path = request.url.path
        
        # Allow public paths
        if any(path.startswith(public_path) for public_path in self.public_paths):
            return await call_next(request)
        
        # Check if path requires authentication
        requires_auth = any(path.startswith(protected_path) for protected_path in self.protected_paths)
        
        if requires_auth:
            # Check for Authorization header
            auth_header = request.headers.get("authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "Authentication required",
                        "headers": {"WWW-Authenticate": "Bearer"}
                    }
                )
            
            # Extract token
            token = auth_header.split(" ")[1]
            
            # Validate token (basic check)
            from app.core.security import JWTUtils, token_blacklist
            
            # Check if token is blacklisted
            if token_blacklist.is_blacklisted(token):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "Token has been revoked",
                        "headers": {"WWW-Authenticate": "Bearer"}
                    }
                )
            
            # Verify token format
            payload = JWTUtils.verify_token(token)
            if not payload:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "Invalid or expired token",
                        "headers": {"WWW-Authenticate": "Bearer"}
                    }
                )
        
        response = await call_next(request)
        return response


class CORSCustomMiddleware(BaseHTTPMiddleware):
    """
    Custom CORS middleware with enhanced security.
    """
    
    def __init__(
        self,
        app,
        allowed_origins: list = None,
        allowed_methods: list = None,
        allowed_headers: list = None,
        allow_credentials: bool = True,
        max_age: int = 86400
    ):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["http://localhost:3000", "http://localhost:8080"]
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allowed_headers = allowed_headers or [
            "Content-Type",
            "Authorization",
            "Accept",
            "Origin",
            "X-Requested-With"
        ]
        self.allow_credentials = allow_credentials
        self.max_age = max_age
    
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            
            if origin in self.allowed_origins or "*" in self.allowed_origins:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
                response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)
                response.headers["Access-Control-Max-Age"] = str(self.max_age)
                
                if self.allow_credentials:
                    response.headers["Access-Control-Allow-Credentials"] = "true"
            
            return response
        
        # Process request
        response = await call_next(request)
        
        # Add CORS headers to response
        if origin in self.allowed_origins or "*" in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            
            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response
