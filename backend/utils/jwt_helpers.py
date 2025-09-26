"""
JWT helper functions for the TrueCred application.

This module provides helper functions for working with JWT tokens.
"""
import jwt
from flask import current_app
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

def decode_token(token):
    """
    Decode a JWT token without verification.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        # Decode without verification - just to get the payload structure
        return jwt.decode(token, options={"verify_signature": False})
    except Exception as e:
        logger.error(f"Error decoding token: {str(e)}")
        return None

def verify_token(token, is_refresh=False):
    """
    Verify a JWT token.
    
    Args:
        token: JWT token to verify
        is_refresh: Whether this is a refresh token
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        # Get the secret key
        secret_key = current_app.config['JWT_SECRET_KEY']
        
        # Get the appropriate audience claim based on token type
        audience = 'refresh' if is_refresh else 'access'
        
        # Decode and verify the token
        payload = jwt.decode(
            token, 
            secret_key, 
            algorithms=['HS256'],
            options={
                'verify_signature': True,
                'require_exp': True
            }
        )
        
        # Check if token is expired
        if 'exp' in payload and payload['exp'] < datetime.utcnow().timestamp():
            logger.warning(f"Token expired: {payload.get('sub', 'unknown')}")
            return None
        
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        return None
