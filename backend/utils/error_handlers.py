"""
Error handling for the TrueCred API.

This module defines custom exceptions and error handlers for the API.
"""
from flask import Blueprint, jsonify, current_app
import logging
from utils.api_response import error_response

# Set up logging
logger = logging.getLogger(__name__)

# Error handling blueprint
error_bp = Blueprint('errors', __name__)


class APIError(Exception):
    """Base exception class for API errors."""
    
    def __init__(self, message, status_code=400, error_code=None, errors=None):
        """
        Initialize API error.
        
        Args:
            message: Error message
            status_code: HTTP status code
            error_code: Error code for client identification
            errors: Detailed validation errors
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or 'api_error'
        self.errors = errors


class ValidationError(APIError):
    """Exception for validation errors."""
    
    def __init__(self, message="Validation error", errors=None):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            errors: Dictionary of field-specific validation errors
        """
        super().__init__(
            message=message,
            status_code=400,
            error_code='validation_error',
            errors=errors or {}
        )


class NotFoundError(APIError):
    """Exception for resource not found errors."""
    
    def __init__(self, resource_type="Resource", resource_id=None):
        """
        Initialize not found error.
        
        Args:
            resource_type: Type of resource that was not found
            resource_id: ID of the resource that was not found
        """
        message = f"{resource_type} not found"
        if resource_id:
            message = f"{resource_type} with ID {resource_id} not found"
            
        super().__init__(
            message=message,
            status_code=404,
            error_code='not_found'
        )


class UnauthorizedError(APIError):
    """Exception for unauthorized access errors."""
    
    def __init__(self, message="Unauthorized"):
        """
        Initialize unauthorized error.
        
        Args:
            message: Error message
        """
        super().__init__(
            message=message,
            status_code=401,
            error_code='unauthorized'
        )


class ForbiddenError(APIError):
    """Exception for forbidden access errors."""
    
    def __init__(self, message="Forbidden"):
        """
        Initialize forbidden error.
        
        Args:
            message: Error message
        """
        super().__init__(
            message=message,
            status_code=403,
            error_code='forbidden'
        )


class ServerError(APIError):
    """Exception for server errors."""
    
    def __init__(self, message="Internal server error"):
        """
        Initialize server error.
        
        Args:
            message: Error message
        """
        super().__init__(
            message=message,
            status_code=500,
            error_code='server_error'
        )


def register_error_handlers(app):
    """
    Register error handlers for the Flask app.
    
    Args:
        app: Flask application instance
    """
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle API errors."""
        logger.error(f"API error: {error.message}")
        return error_response(
            message=error.message,
            status_code=error.status_code,
            error_code=error.error_code,
            errors=error.errors
        )
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors."""
        return error_response(
            message="Resource not found",
            status_code=404,
            error_code="not_found"
        )
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle 400 errors."""
        return error_response(
            message="Bad request",
            status_code=400,
            error_code="bad_request"
        )
    
    @app.errorhandler(401)
    def handle_unauthorized(error):
        """Handle 401 errors."""
        return error_response(
            message="Unauthorized",
            status_code=401,
            error_code="unauthorized"
        )
    
    @app.errorhandler(403)
    def handle_forbidden(error):
        """Handle 403 errors."""
        return error_response(
            message="Forbidden",
            status_code=403,
            error_code="forbidden"
        )
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 errors."""
        return error_response(
            message="Method not allowed",
            status_code=405,
            error_code="method_not_allowed"
        )
    
    @app.errorhandler(500)
    def handle_server_error(error):
        """Handle 500 errors."""
        logger.error(f"Server error: {str(error)}")
        return error_response(
            message="Internal server error",
            status_code=500,
            error_code="server_error"
        )
