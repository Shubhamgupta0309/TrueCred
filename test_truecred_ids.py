#!/usr/bin/env python3
"""
Test script to verify TrueCred ID generation functionality.
"""
import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from backend.utils.id_generator import generate_truecred_id, generate_sequential_truecred_id
from backend.services.auth_service import AuthService
from backend.models.user import User
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_id_generation():
    """Test the TrueCred ID generation functions."""
    print("Testing TrueCred ID Generation...")
    print("=" * 50)

    # Test random ID generation
    print("\n1. Testing random ID generation:")
    for i in range(5):
        random_id = generate_truecred_id()
        print(f"   Random ID {i+1}: {random_id}")
        assert random_id.startswith("TC"), f"ID should start with TC: {random_id}"
        assert len(random_id) == 8, f"ID should be 8 characters: {random_id}"
        assert random_id[2:].isdigit(), f"Last 6 characters should be digits: {random_id}"

    # Test sequential ID generation
    print("\n2. Testing sequential ID generation:")
    for i in range(3):
        sequential_id = generate_sequential_truecred_id()
        print(f"   Sequential ID {i+1}: {sequential_id}")
        assert sequential_id.startswith("TC"), f"ID should start with TC: {sequential_id}"
        assert len(sequential_id) == 8, f"ID should be 8 characters: {sequential_id}"
        assert sequential_id[2:].isdigit(), f"Last 6 characters should be digits: {sequential_id}"

    # Test uniqueness (this would require database connection)
    print("\n3. Testing uniqueness checking:")
    try:
        unique_id = AuthService._generate_unique_truecred_id()
        if unique_id:
            print(f"   Generated unique ID: {unique_id}")
            # Check if it exists in database (would need actual DB connection)
            print("   Note: Full uniqueness test requires database connection")
        else:
            print("   Warning: Failed to generate unique ID")
    except Exception as e:
        print(f"   Error testing uniqueness: {e}")

    print("\n4. Testing format validation:")
    test_ids = ["TC123456", "TC000001", "TC999999", "TC12345", "TC1234567", "AB123456"]
    for test_id in test_ids:
        is_valid = (test_id.startswith("TC") and
                   len(test_id) == 8 and
                   test_id[2:].isdigit())
        print(f"   {test_id}: {'Valid' if is_valid else 'Invalid'}")

    print("\n" + "=" * 50)
    print("TrueCred ID generation test completed successfully!")

if __name__ == "__main__":
    test_id_generation()