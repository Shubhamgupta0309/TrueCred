"""
API response utilities for the TrueCred API.

This module provides standardized response formats for API endpoints.
"""
from flask import jsonify
from typing import Dict, List, Any, Optional, Union


def success_response(
    data: Optional[Union[Dict, List]] = None,
    message: str = "Operation successful",
    status_code: int = 200,
    meta: Optional[Dict] = None
) -> tuple:
    """
    Generate a standardized success response.
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
        meta: Additional metadata (pagination, etc.)
    
    Returns:
        JSON response with success status
    """
    response = {
        'success': True,
        'message': message
    }
    
    if data is not None:
        response['data'] = data
        
    if meta is not None:
        response['meta'] = meta
        
    return jsonify(response), status_code


def error_response(
    message: str = "An error occurred",
    status_code: int = 400,
    error_code: Optional[str] = None,
    errors: Optional[Dict] = None
) -> tuple:
    """
    Generate a standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        error_code: Error code for client identification
        errors: Detailed validation errors
    
    Returns:
        JSON response with error status
    """
    response = {
        'success': False,
        'message': message
    }
    
    if error_code:
        response['error_code'] = error_code
        
    if errors:
        response['errors'] = errors
        
    return jsonify(response), status_code


def validation_error_response(
    errors: Dict[str, str],
    message: str = "Validation error",
    status_code: int = 400
) -> tuple:
    """
    Generate a standardized validation error response.
    
    Args:
        errors: Dictionary of field-specific validation errors
        message: Error message
        status_code: HTTP status code
    
    Returns:
        JSON response with validation errors
    """
    return error_response(
        message=message,
        status_code=status_code,
        error_code="validation_error",
        errors=errors
    )


def not_found_response(
    resource_type: str = "Resource",
    resource_id: Optional[str] = None
) -> tuple:
    """
    Generate a standardized not found response.
    
    Args:
        resource_type: Type of resource that was not found
        resource_id: ID of the resource that was not found
    
    Returns:
        JSON response with not found error
    """
    message = f"{resource_type} not found"
    if resource_id:
        message = f"{resource_type} with ID {resource_id} not found"
        
    return error_response(
        message=message,
        status_code=404,
        error_code="not_found"
    )


def server_error_response(
    message: str = "Internal server error"
) -> tuple:
    """
    Generate a standardized server error response.
    
    Args:
        message: Error message
    
    Returns:
        JSON response with server error
    """
    return error_response(
        message=message,
        status_code=500,
        error_code="server_error"
    )


def unauthorized_response(
    message: str = "Unauthorized"
) -> tuple:
    """
    Generate a standardized unauthorized response.
    
    Args:
        message: Error message
    
    Returns:
        JSON response with unauthorized error
    """
    return error_response(
        message=message,
        status_code=401,
        error_code="unauthorized"
    )


def forbidden_response(
    message: str = "Forbidden"
) -> tuple:
    """
    Generate a standardized forbidden response.
    
    Args:
        message: Error message
    
    Returns:
        JSON response with forbidden error
    """
    return error_response(
        message=message,
        status_code=403,
        error_code="forbidden"
    )
