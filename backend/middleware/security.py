"""
Security middleware for TrueCred API.

This module provides rate limiting, input validation, and security headers.
"""
import time
import hashlib
import logging
from flask import request, jsonify, g, current_app
from functools import wraps
from typing import Dict, Any, Optional, Callable
import re
import bleach

logger = logging.getLogger(__name__)

# In-memory rate limiting store (use Redis in production)
rate_limit_store: Dict[str, Dict[str, Any]] = {}

class SecurityMiddleware:
    """Security middleware for API protection."""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the security middleware with the Flask app."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)

        # Register security error handlers
        self.register_error_handlers(app)

    def before_request(self):
        """Process requests before they reach the endpoint."""
        # Rate limiting
        if self._check_rate_limit():
            return self._rate_limit_exceeded_response()

        # Input sanitization
        self._sanitize_input()

        # Security headers validation
        self._validate_security_headers()

    def after_request(self, response):
        """Process responses before they are sent."""
        # Add security headers
        response = self._add_security_headers(response)

        # Log security events
        self._log_security_events(response)

        return response

    def _check_rate_limit(self) -> bool:
        """
        Check if the request exceeds rate limits.

        Returns:
            True if rate limit exceeded, False otherwise
        """
        # Get client identifier (IP address or user ID if authenticated)
        client_id = self._get_client_identifier()

        # Get rate limit configuration
        limits = current_app.config.get('RATE_LIMITS', {
            'default': {'requests': 100, 'window': 60},  # 100 requests per minute
            'auth': {'requests': 5, 'window': 60},       # 5 auth requests per minute
            'upload': {'requests': 10, 'window': 3600}   # 10 uploads per hour
        })

        # Determine limit type based on endpoint
        limit_type = 'default'
        if request.endpoint and 'auth' in request.endpoint:
            limit_type = 'auth'
        elif request.endpoint and ('upload' in request.endpoint or request.method in ['POST', 'PUT']):
            limit_type = 'upload'

        limit_config = limits.get(limit_type, limits['default'])

        # Check rate limit
        current_time = time.time()
        window_start = current_time - limit_config['window']

        # Clean old entries
        if client_id in rate_limit_store:
            rate_limit_store[client_id] = {
                k: v for k, v in rate_limit_store[client_id].items()
                if k == 'count' or float(k) > window_start
            }

        # Initialize client data if not exists
        if client_id not in rate_limit_store:
            rate_limit_store[client_id] = {'count': 0}

        # Count requests in current window
        request_count = sum(1 for k, v in rate_limit_store[client_id].items()
                          if k != 'count' and float(k) > window_start)

        # Check if limit exceeded
        if request_count >= limit_config['requests']:
            return True

        # Record this request
        rate_limit_store[client_id][str(current_time)] = True
        rate_limit_store[client_id]['count'] = request_count + 1

        return False

    def _get_client_identifier(self) -> str:
        """Get a unique identifier for the client."""
        # Use user ID if authenticated, otherwise IP address
        if hasattr(g, 'user_id') and g.user_id:
            return f"user_{g.user_id}"

        # Fallback to IP address
        client_ip = request.remote_addr
        if not client_ip:
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', 'unknown').split(',')[0].strip()

        return f"ip_{client_ip}"

    def _rate_limit_exceeded_response(self):
        """Return rate limit exceeded response."""
        logger.warning(f"Rate limit exceeded for client: {self._get_client_identifier()}")

        response = jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.',
            'retry_after': 60
        })
        response.status_code = 429
        response.headers['Retry-After'] = '60'
        return response

    def _sanitize_input(self):
        """Sanitize input data to prevent XSS and injection attacks."""
        # Sanitize query parameters
        for key, value in request.args.items():
            if isinstance(value, str):
                request.args = request.args.copy()
                request.args[key] = bleach.clean(value, strip=True)

        # Sanitize form data
        if request.form:
            sanitized_form = {}
            for key, value in request.form.items():
                if isinstance(value, str):
                    sanitized_form[key] = bleach.clean(value, strip=True)
                else:
                    sanitized_form[key] = value
            # Note: In Flask, form data is immutable, so we can't modify it directly
            # Instead, we'll validate it in the endpoint

        # Sanitize JSON data
        if request.is_json and request.json:
            self._sanitize_json_data(request.json)

    def _sanitize_json_data(self, data):
        """Recursively sanitize JSON data."""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    # Basic sanitization - remove potentially dangerous characters
                    data[key] = re.sub(r'[<>]', '', value)
                elif isinstance(value, (dict, list)):
                    self._sanitize_json_data(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, str):
                    data[i] = re.sub(r'[<>]', '', item)
                elif isinstance(item, (dict, list)):
                    self._sanitize_json_data(item)

    def _validate_security_headers(self):
        """Validate security-related headers."""
        # Check for suspicious headers that might indicate attacks
        suspicious_headers = [
            'X-Forwarded-For',  # Should be handled by proxy
            'X-Real-IP',        # Should be handled by proxy
        ]

        for header in suspicious_headers:
            if header in request.headers and not self._is_trusted_proxy():
                logger.warning(f"Suspicious header detected: {header}")

    def _is_trusted_proxy(self) -> bool:
        """Check if the request comes from a trusted proxy."""
        # In production, implement proper proxy validation
        # For now, assume all requests are from trusted sources
        return True

    def _add_security_headers(self, response):
        """Add security headers to the response."""
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"

        # Remove server header for security
        response.headers.pop('Server', None)

        return response

    def _log_security_events(self, response):
        """Log security-related events."""
        if response.status_code >= 400:
            logger.warning(f"Security event: {response.status_code} - {request.method} {request.path}")

    def register_error_handlers(self, app):
        """Register security-related error handlers."""

        @app.errorhandler(400)
        def bad_request(error):
            return jsonify({
                'error': 'Bad Request',
                'message': 'Invalid request data'
            }), 400

        @app.errorhandler(413)
        def request_entity_too_large(error):
            return jsonify({
                'error': 'Request Entity Too Large',
                'message': 'File size exceeds maximum limit'
            }), 413

        @app.errorhandler(415)
        def unsupported_media_type(error):
            return jsonify({
                'error': 'Unsupported Media Type',
                'message': 'Content type not supported'
            }), 415

        @app.errorhandler(429)
        def too_many_requests(error):
            return jsonify({
                'error': 'Too Many Requests',
                'message': 'Rate limit exceeded'
            }), 429

def rate_limit(limit_type: str = 'default'):
    """
    Decorator for custom rate limiting on specific endpoints.

    Args:
        limit_type: Type of rate limit to apply
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Custom rate limiting logic can be implemented here
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_input(schema: Dict[str, Any]):
    """
    Decorator for input validation.

    Args:
        schema: Validation schema for the input data
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Input validation logic can be implemented here
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_https(f):
    """
    Decorator to require HTTPS for sensitive endpoints.

    Args:
        f: Function to decorate
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and not current_app.debug:
            return jsonify({
                'error': 'HTTPS Required',
                'message': 'This endpoint requires a secure connection'
            }), 403
        return f(*args, **kwargs)
    return decorated_function

# Input validation functions
def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_file_type(filename: str, allowed_types: list) -> bool:
    """Validate file type based on extension."""
    if '.' not in filename:
        return False

    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_types

def sanitize_string(input_str: str, max_length: int = 1000) -> str:
    """Sanitize string input."""
    if not input_str:
        return ""

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>]', '', input_str)

    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized.strip()