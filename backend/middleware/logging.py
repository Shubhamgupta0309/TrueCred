"""
Logging middleware for Flask applications.

This module provides middleware for logging API requests and responses.
"""
import time
import logging
from flask import request, g

# Set up logger
logger = logging.getLogger(__name__)

def log_request():
    """Log details about incoming requests."""
    g.start_time = time.time()
    
    # Log the request
    logger.info(f"Request: {request.method} {request.path}")
    logger.debug(f"Headers: {dict(request.headers)}")
    
    # For POST/PUT requests, log the body (but be careful with sensitive data)
    if request.method in ['POST', 'PUT'] and request.is_json:
        # Create a sanitized version of the request data to avoid logging sensitive information
        sanitized_data = {}
        for key, value in request.json.items():
            if key.lower() in ['password', 'token', 'secret', 'key']:
                sanitized_data[key] = '[REDACTED]'
            else:
                sanitized_data[key] = value
        
        logger.debug(f"Body: {sanitized_data}")

def log_response(response):
    """Log details about outgoing responses."""
    # Calculate duration
    duration = time.time() - g.get('start_time', time.time())
    
    # Log basic response info
    logger.info(f"Response: {request.method} {request.path} - Status: {response.status_code} - Duration: {duration:.4f}s")
    
    # For debugging, log more detailed response data
    try:
        if response.is_json:
            # Don't log the entire response body as it might be large
            # Just log the structure or specific fields
            data = response.get_json()
            success = data.get('success', None)
            message = data.get('message', None)
            logger.debug(f"Response JSON - Success: {success}, Message: {message}")
    except Exception as e:
        logger.warning(f"Error logging response: {str(e)}")
    
    return response

def setup_logging_middleware(app):
    """Set up request/response logging middleware."""
    # Register the middleware functions
    app.before_request(log_request)
    app.after_request(log_response)
