"""
Authentication middleware for the TrueCred application.

This module provides middleware functions for authentication and authorization.
"""
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from functools import wraps
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def role_required(roles):
    """
    Decorator to check if the authenticated user has one of the required roles.
    
    Args:
        roles: List of roles allowed to access the endpoint
        
    Returns:
        Decorator function
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verify JWT is valid
            verify_jwt_in_request()
            
            # Get claims from JWT
            claims = get_jwt()
            
            # Check if role is in claims
            user_role = claims.get('role', '')
            
            # Check if user role is in allowed roles
            if user_role not in roles:
                logger.warning(f"Access denied for user with role '{user_role}'. Required roles: {roles}")
                return jsonify({
                    'success': False,
                    'message': 'Access denied. Insufficient permissions.'
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def admin_required(fn):
    """
    Decorator to check if the authenticated user is an admin.
    
    Returns:
        Decorator function
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Verify JWT is valid
        verify_jwt_in_request()
        
        # Get claims from JWT
        claims = get_jwt()
        
        # Check if role is in claims and is 'admin'
        user_role = claims.get('role', '')
        
        if user_role != 'admin':
            logger.warning(f"Admin access denied for user with role '{user_role}'")
            return jsonify({
                'success': False,
                'message': 'Access denied. Admin privileges required.'
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper

def issuer_required(fn):
    """
    Decorator to check if the authenticated user is an issuer.
    
    Returns:
        Decorator function
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Verify JWT is valid
        verify_jwt_in_request()
        
        # Get claims from JWT
        claims = get_jwt()
        
        # Check if role is in claims and is 'issuer' or 'admin'
        user_role = claims.get('role', '')
        
        if user_role not in ['issuer', 'admin']:
            logger.warning(f"Issuer access denied for user with role '{user_role}'")
            return jsonify({
                'success': False,
                'message': 'Access denied. Issuer privileges required.'
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper
