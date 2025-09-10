"""
Test user login API for TrueCred.
"""
import requests
import json
import sys
import os

def test_user_login():
    """Test user login API."""
    api_url = "http://localhost:5000/api/auth/login"
    
    # Test user credentials
    user_data = {
        "username_or_email": "testuser123@example.com",  # Use the email from registration test
        "password": "TestPassword123!"
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
        
        if response.status_code == 200:
            print("Login successful!")
            response_json = response.json()
            
            # Print tokens (but mask most of it for security)
            if "tokens" in response_json:
                access_token = response_json["tokens"]["access_token"]
                refresh_token = response_json["tokens"]["refresh_token"]
                
                print("\nAccess Token: " + access_token[:10] + "..." + access_token[-10:])
                print("Refresh Token: " + refresh_token[:10] + "..." + refresh_token[-10:])
                
                # Test a protected endpoint
                test_protected_endpoint(access_token)
            else:
                print("No tokens found in response!")
        else:
            print(f"Login failed with status {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error making request: {e}")
        return False

def test_protected_endpoint(access_token):
    """Test accessing a protected endpoint with the token."""
    api_url = "http://localhost:5000/api/auth/profile"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\nTesting protected endpoint: {api_url}")
    
    try:
        response = requests.get(api_url, headers=headers)
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Successfully accessed protected endpoint!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Failed to access protected endpoint with status {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error making request: {e}")

if __name__ == "__main__":
    test_user_login()
