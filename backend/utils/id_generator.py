"""
User ID generation utilities for TrueCred.
"""
import random
import string
from mongoengine import connect
from models.user import User

def generate_truecred_id():
    """
    Generate a unique TrueCred ID in the format TC + 6 random digits.

    Returns:
        A string containing the TrueCred ID
    """
    max_attempts = 50  # Increased from 10 to 50 for better uniqueness
    attempts = 0

    while attempts < max_attempts:
        # Generate 6 random digits
        random_digits = ''.join(random.choices(string.digits, k=6))

        # Create the ID in the format TC + 6 random digits
        truecred_id = f"TC{random_digits}"

        # Check if this ID already exists in the database
        try:
            existing_user = User.objects(truecred_id=truecred_id).first()
            if not existing_user:
                return truecred_id
        except Exception as e:
            # If there's a database error, try again with a different ID
            pass

        attempts += 1

    # If we can't generate a unique ID after max attempts, use timestamp-based approach
    import time
    timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
    fallback_id = f"TC{timestamp}"

    # Ensure fallback is also unique
    counter = 0
    while User.objects(truecred_id=fallback_id).first() and counter < 100:
        counter += 1
        fallback_id = f"TC{str(int(time.time()) + counter)[-6:]}"

    return fallback_id

def generate_sequential_truecred_id():
    """
    Generate a sequential TrueCred ID starting from TC000001.
    This ensures truly unique IDs without random generation.

    Returns:
        A string containing the TrueCred ID
    """
    try:
        # Find the highest existing TrueCred ID
        last_user = User.objects(truecred_id__exists=True).order_by('-truecred_id').first()

        if last_user and last_user.truecred_id:
            # Extract the numeric part and increment
            numeric_part = last_user.truecred_id[2:]  # Remove 'TC' prefix
            try:
                next_number = int(numeric_part) + 1
                return f"TC{next_number:06d}"  # Pad with zeros to 6 digits
            except ValueError:
                # If parsing fails, start from 1
                return "TC000001"
        else:
            # No existing IDs, start from 1
            return "TC000001"
    except Exception as e:
        # Fallback to timestamp-based ID if database query fails
        import time
        timestamp = str(int(time.time() * 1000))[-6:]  # Last 6 digits of millisecond timestamp
        return f"TC{timestamp}"
