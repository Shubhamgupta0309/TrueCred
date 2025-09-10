"""
Test user registration API for TrueCred.
"""
import requests
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_user_registration():
    """Test user registration API."""
    api_url = "http://localhost:5000/api/auth/register"
    
    # Test user data
    user_data = {
        "username": "testuser123",
        "email": "testuser123@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    # Make request
    print(f"Sending POST request to {api_url}")
    print(f"Request data: {json.dumps(user_data, indent=2)}")
    
    try:
        response = requests.post(
            api_url,
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Print response
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 201
    except Exception as e:
        print(f"Error making request: {e}")
        return False

if __name__ == "__main__":
    test_user_registration()
