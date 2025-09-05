"""
Simple script to test the TrueCred API.
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_api():
    """Test basic API endpoints."""
    try:
        # Test the root endpoint
        print("Testing root endpoint...")
        response = requests.get(f"{BASE_URL}/")
        print_response(response)
        
        # Test the API info endpoint
        print("Testing API info endpoint...")
        response = requests.get(f"{BASE_URL}/api")
        print_response(response)
        
        # Test the health check endpoint
        print("Testing health check endpoint...")
        response = requests.get(f"{BASE_URL}/api/health")
        print_response(response)
        
        print("All tests completed successfully!")
    except Exception as e:
        print(f"Error during testing: {e}")

def print_response(response):
    """Print response in a readable format."""
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print("-" * 50)

if __name__ == "__main__":
    test_api()
