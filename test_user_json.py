#!/usr/bin/env python3
"""
Test script to verify that the User model's to_json method includes truecred_id
"""
import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.dirname(__file__)
sys.path.insert(0, backend_path)

from models.user import User
import json

def test_user_to_json():
    """Test that User.to_json() includes truecred_id"""
    print("Testing User.to_json() method...")

    # Create a test user with truecred_id
    user = User(
        username='testuser',
        email='test@example.com',
        password='hashedpass',
        first_name='Test',
        last_name='User',
        truecred_id='TC123456'
    )

    # Get JSON representation
    json_data = user.to_json()

    # Check if truecred_id is included
    if 'truecred_id' in json_data:
        print("✅ SUCCESS: truecred_id is included in JSON response")
        print(f"   TrueCred ID value: {json_data['truecred_id']}")
    else:
        print("❌ FAILED: truecred_id is missing from JSON response")

    print(f"   All JSON keys: {list(json_data.keys())}")

    # Test with None truecred_id
    user2 = User(
        username='testuser2',
        email='test2@example.com',
        password='hashedpass',
        first_name='Test2',
        last_name='User2',
        truecred_id=None
    )

    json_data2 = user2.to_json()
    print(f"\n   Test with None truecred_id: {json_data2.get('truecred_id')}")

if __name__ == "__main__":
    test_user_to_json()