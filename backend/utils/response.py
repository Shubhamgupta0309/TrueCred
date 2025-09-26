"""
Response utilities for the TrueCred application.

This module provides standardized response formatters for API endpoints.
"""
from flask import jsonify

def success_response(message="Success", data=None, status_code=200):
    """
    Create a standardized success response.
    
    Args:
        message: Success message to include in the response
        data: Optional data to include in the response
        status_code: HTTP status code to return
        
    Returns:
        Flask response object with JSON data
    """
    response = {
        'success': True,
        'message': message
    }
    
    if data is not None:
        response['data'] = data
        
    return jsonify(response), status_code

def error_response(message="Error", errors=None, status_code=400):
    """
    Create a standardized error response.
    
    Args:
        message: Error message to include in the response
        errors: Optional list of specific errors to include
        status_code: HTTP status code to return
        
    Returns:
        Flask response object with JSON data
    """
    response = {
        'success': False,
        'message': message
    }
    
    if errors is not None:
        response['errors'] = errors
        
    return jsonify(response), status_code

def paginated_response(items, page, per_page, total, message="Success"):
    """
    Create a standardized paginated response.
    
    Args:
        items: List of items for the current page
        page: Current page number
        per_page: Number of items per page
        total: Total number of items
        message: Success message to include in the response
        
    Returns:
        Flask response object with JSON data
    """
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    
    response = {
        'success': True,
        'message': message,
        'data': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_items': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }
    
    return jsonify(response), 200
