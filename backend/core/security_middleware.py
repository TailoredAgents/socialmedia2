"""
Security Middleware for Production
Implements security headers, CORS, rate limiting, and request validation
"""
import time
import logging
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta
import hashlib
import json

from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import os

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    def __init__(self, app, environment: str = "production"):
        super().__init__(app)
        self.environment = environment.lower()
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers for production
        if self.environment == "production":
            # Prevent XSS attacks
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            
            # HTTPS enforcement
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
            # Content Security Policy
            csp = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.openai.com https://google.serper.dev"
            response.headers["Content-Security-Policy"] = csp
            
            # Referrer policy
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            
        # Remove server information
        if "server" in response.headers:
            del response.headers["server"]
        
        # Add custom security header
        response.headers["X-Security-Headers"] = "enabled"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware"""
    
    def __init__(self, app, 
                 requests_per_minute: int = 60, 
                 requests_per_hour: int = 1000,
                 burst_limit: int = 10):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_limit = burst_limit
        
        # In-memory storage (for production, use Redis)
        self.minute_counts: Dict[str, deque] = defaultdict(deque)
        self.hour_counts: Dict[str, deque] = defaultdict(deque)
        self.burst_counts: Dict[str, List[float]] = defaultdict(list)
        
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address, handling proxies"""
        # Check for forwarded headers (from load balancers/proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP if multiple
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
            
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def is_rate_limited(self, client_ip: str) -> Optional[Dict[str, Any]]:
        """Check if client is rate limited"""
        now = time.time()
        current_minute = int(now // 60)
        current_hour = int(now // 3600)
        
        # Clean old entries
        minute_deque = self.minute_counts[client_ip]
        while minute_deque and minute_deque[0] < current_minute:
            minute_deque.popleft()
            
        hour_deque = self.hour_counts[client_ip]
        while hour_deque and hour_deque[0] < current_hour:
            hour_deque.popleft()
        
        # Check burst limit (last 10 seconds)
        burst_times = self.burst_counts[client_ip]
        burst_times[:] = [t for t in burst_times if now - t < 10]
        
        # Rate limit checks
        if len(burst_times) >= self.burst_limit:
            return {
                "limit_type": "burst",
                "retry_after": 10,
                "message": f"Burst limit exceeded: max {self.burst_limit} requests per 10 seconds"
            }
            
        if len(minute_deque) >= self.requests_per_minute:
            return {
                "limit_type": "minute",
                "retry_after": 60,
                "message": f"Rate limit exceeded: max {self.requests_per_minute} requests per minute"
            }
            
        if len(hour_deque) >= self.requests_per_hour:
            return {
                "limit_type": "hour",
                "retry_after": 3600,
                "message": f"Rate limit exceeded: max {self.requests_per_hour} requests per hour"
            }
        
        # Record this request
        minute_deque.append(current_minute)
        hour_deque.append(current_hour)
        burst_times.append(now)
        
        return None
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/ready", "/metrics"]:
            return await call_next(request)
        
        client_ip = self.get_client_ip(request)
        
        # Check rate limits
        limit_info = self.is_rate_limited(client_ip)
        if limit_info:
            logger.warning(f"Rate limit exceeded for {client_ip}: {limit_info['message']}")
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": limit_info["message"],
                    "retry_after": limit_info["retry_after"]
                },
                headers={
                    "Retry-After": str(limit_info["retry_after"]),
                    "X-RateLimit-Limit": str(getattr(self, f"requests_per_{limit_info['limit_type']}")),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + limit_info["retry_after"]))
                }
            )
        
        # Add rate limit headers to successful responses
        response = await call_next(request)
        
        # Add current rate limit status to response
        minute_remaining = max(0, self.requests_per_minute - len(self.minute_counts[client_ip]))
        hour_remaining = max(0, self.requests_per_hour - len(self.hour_counts[client_ip]))
        
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(minute_remaining)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(hour_remaining)
        
        return response

class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Validate incoming requests for security threats"""
    
    def __init__(self, app):
        super().__init__(app)
        
        # Common SQL injection patterns
        self.sql_patterns = [
            "union select", "drop table", "delete from", "insert into",
            "update set", "create table", "alter table", "exec(",
            "execute(", "sp_executesql", "xp_cmdshell", "information_schema"
        ]
        
        # Common XSS patterns
        self.xss_patterns = [
            "<script", "javascript:", "onload=", "onerror=", "onclick=",
            "onmouseover=", "eval(", "expression(", "vbscript:", "data:text/html"
        ]
        
        # Path traversal patterns
        self.path_traversal_patterns = [
            "../", "..\\", "....//", "....\\\\", "/etc/passwd", 
            "/etc/shadow", "c:\\windows\\system32", ".htaccess"
        ]
    
    def check_suspicious_content(self, content: str) -> Optional[str]:
        """Check content for suspicious patterns"""
        content_lower = content.lower()
        
        # Check SQL injection
        for pattern in self.sql_patterns:
            if pattern in content_lower:
                return f"Potential SQL injection attempt: {pattern}"
        
        # Check XSS
        for pattern in self.xss_patterns:
            if pattern in content_lower:
                return f"Potential XSS attempt: {pattern}"
        
        # Check path traversal
        for pattern in self.path_traversal_patterns:
            if pattern in content_lower:
                return f"Potential path traversal attempt: {pattern}"
        
        return None
    
    async def dispatch(self, request: Request, call_next):
        # Skip validation for health checks
        if request.url.path in ["/health", "/ready", "/metrics"]:
            return await call_next(request)
        
        # Check URL path
        suspicious = self.check_suspicious_content(str(request.url))
        if suspicious:
            logger.warning(f"Suspicious request from {request.client.host if request.client else 'unknown'}: {suspicious}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Invalid request", "message": "Request contains suspicious content"}
            )
        
        # Check query parameters
        for key, value in request.query_params.items():
            suspicious = self.check_suspicious_content(f"{key}={value}")
            if suspicious:
                logger.warning(f"Suspicious query parameter from {request.client.host if request.client else 'unknown'}: {suspicious}")
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"error": "Invalid request", "message": "Request contains suspicious content"}
                )
        
        # Check headers for suspicious content
        for header_name, header_value in request.headers.items():
            if header_name.lower() not in ["authorization", "cookie", "user-agent"]:  # Skip sensitive headers
                suspicious = self.check_suspicious_content(f"{header_name}: {header_value}")
                if suspicious:
                    logger.warning(f"Suspicious header from {request.client.host if request.client else 'unknown'}: {suspicious}")
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"error": "Invalid request", "message": "Request contains suspicious content"}
                    )
        
        # For POST/PUT requests, check body (limited to prevent DoS)
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Only check first 10KB to prevent DoS
                body = await request.body()
                if len(body) > 10240:  # 10KB limit for security scanning
                    body = body[:10240]
                
                if body:
                    try:
                        body_str = body.decode('utf-8', errors='ignore')
                        suspicious = self.check_suspicious_content(body_str)
                        if suspicious:
                            logger.warning(f"Suspicious request body from {request.client.host if request.client else 'unknown'}: {suspicious}")
                            return JSONResponse(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                content={"error": "Invalid request", "message": "Request contains suspicious content"}
                            )
                    except Exception:
                        # If we can't decode, skip body validation
                        pass
            except Exception as e:
                logger.error(f"Error checking request body: {e}")
        
        return await call_next(request)

def get_cors_middleware_config(environment: str = "production"):
    """Get CORS middleware configuration based on environment"""
    
    if environment.lower() == "development":
        # Development: Allow all origins
        return {
            "allow_origins": ["*"],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"]
        }
    else:
        # Production: Restrict origins
        # Check both ALLOWED_ORIGINS and CORS_ORIGINS for compatibility
        allowed_origins_env = os.getenv("ALLOWED_ORIGINS") or os.getenv("CORS_ORIGINS", "")
        logger.info(f"Security middleware CORS - ALLOWED_ORIGINS: {os.getenv('ALLOWED_ORIGINS')}")
        logger.info(f"Security middleware CORS - CORS_ORIGINS: {os.getenv('CORS_ORIGINS')}")
        
        if allowed_origins_env:
            allowed_origins = allowed_origins_env.split(",")
            allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
        else:
            allowed_origins = []
        
        if not allowed_origins:
            # Always include the lily-ai domain as default
            allowed_origins = [
                "https://www.lily-ai-socialmedia.com",
                "https://lily-ai-socialmedia.com",
                "https://ai-social-frontend.onrender.com",
                "https://localhost", 
                "http://localhost"
            ]
            logger.warning("No CORS environment variables found, using default origins including lily-ai domain")
        
        logger.info(f"Security middleware CORS allowed origins: {allowed_origins}")
        
        return {
            "allow_origins": allowed_origins,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Accept",
                "Accept-Language",
                "Content-Language", 
                "Content-Type",
                "Authorization",
                "X-Requested-With"
            ]
        }

def get_trusted_host_middleware(environment: str = "production"):
    """Get trusted host middleware configuration for production"""
    
    if environment.lower() == "development":
        # Development: Allow all hosts
        return None
    
    # Production: Restrict allowed hosts
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "").split(",")
    allowed_hosts = [host.strip() for host in allowed_hosts if host.strip()]
    
    if not allowed_hosts:
        # Default to common patterns
        allowed_hosts = ["localhost", "127.0.0.1", "*.herokuapp.com", "*.render.com"]
        logger.warning("No ALLOWED_HOSTS specified, using default patterns")
    
    # Return configuration dict for middleware, not the class itself
    return {"allowed_hosts": allowed_hosts}

def setup_security_middleware(app, environment: str = "production"):
    """Setup all security middleware for the application"""
    
    logger.info(f"Setting up security middleware for {environment} environment")
    
    # 1. Request validation (first layer)
    app.add_middleware(RequestValidationMiddleware)
    
    # 2. Rate limiting
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
        requests_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "1000")),
        burst_limit=int(os.getenv("RATE_LIMIT_BURST", "10"))
    )
    
    # 3. Security headers
    app.add_middleware(SecurityHeadersMiddleware, environment=environment)
    
    # 4. CORS (if needed)
    cors_config = get_cors_middleware_config(environment)
    if cors_config:
        app.add_middleware(CORSMiddleware, **cors_config)
    
    # 5. Trusted hosts (production only)
    trusted_host_config = get_trusted_host_middleware(environment)
    if trusted_host_config:
        app.add_middleware(TrustedHostMiddleware, **trusted_host_config)
    
    logger.info("Security middleware setup completed")
    
    return app