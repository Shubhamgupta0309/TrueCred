"""
User ID generation utilities for TrueCred.
"""
import random
import string

def generate_truecred_id():
    """
    Generate a unique TrueCred ID in the format TC + 6 random digits.
    
    Returns:
        A string containing the TrueCred ID
    """
    # Generate 6 random digits
    random_digits = ''.join(random.choices(string.digits, k=6))
    
    # Return the ID in the format TC + 6 random digits
    return f"TC{random_digits}"
