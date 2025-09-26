"""
Password utility for the TrueCred application.

This module provides functions for password hashing and verification
using the passlib library with bcrypt algorithm.
"""
from passlib.hash import bcrypt_sha256
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_password(password):
    """
    Hash a password using bcrypt with SHA-256 preprocessing.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password
    """
    try:
        return bcrypt_sha256.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise

def verify_password(password, hashed_password):
    """
    Verify a password against a hashed password.
    
    Args:
        password: Plain text password to verify
        hashed_password: Hashed password to check against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt_sha256.verify(password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False

def password_meets_requirements(password):
    """
    Check if a password meets security requirements.
    
    Requirements:
    - Minimum length of 8 characters
    - Contains at least one lowercase letter
    - Contains at least one uppercase letter
    - Contains at least one digit
    - Contains at least one special character
    
    Args:
        password: Password to check
        
    Returns:
        (bool, str): (True, None) if password meets requirements, 
                     (False, error_message) otherwise
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/~`" for c in password):
        return False, "Password must contain at least one special character"
    
    return True, None
