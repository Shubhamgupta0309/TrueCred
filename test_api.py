import requests
import json

# Disable SSL warnings for testing only
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API endpoint
url = "http://127.0.0.1:5000/api/auth/register"

# Request body
data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "Password123!",
    "role": "student"
}

try:
    # Make the request
    response = requests.post(url, json=data, verify=False)
    
    # Print the response
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
