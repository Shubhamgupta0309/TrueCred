import requests
import json

# API endpoint
url = "http://127.0.0.1:5000/api/auth/register"

# Request body
data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "role": "student"
}

# Make the request
response = requests.post(url, json=data)

# Print the response
print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.text}")
