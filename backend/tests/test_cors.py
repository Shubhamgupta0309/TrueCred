"""
Test CORS and API accessibility from frontend.
"""
import requests
import json
import sys
import os

def test_api_cors():
    """Test API CORS configuration."""
    # Base API URL
    api_url = "http://localhost:5000/api"
    
    # Origin header simulating request from frontend
    headers = {
        "Origin": "http://localhost:5173"  # Vite's default port
    }
    
    # Make request
    print(f"Testing CORS with request to {api_url} from origin {headers['Origin']}")
    
    try:
        response = requests.get(api_url, headers=headers)
        
        # Print response
        print(f"Status code: {response.status_code}")
        
        # Check CORS headers
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers"
        ]
        
        print("\nCORS Headers:")
        for header in cors_headers:
            value = response.headers.get(header, "Not set")
            print(f"{header}: {value}")
            
        # Check if frontend origin is allowed
        allowed_origin = response.headers.get("Access-Control-Allow-Origin", "")
        if headers["Origin"] in allowed_origin or allowed_origin == "*":
            print("\n✅ Frontend origin is allowed by CORS!")
        else:
            print(f"\n❌ Frontend origin {headers['Origin']} is NOT allowed by CORS!")
            print(f"Allowed origins: {allowed_origin}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error making request: {e}")
        return False

if __name__ == "__main__":
    test_api_cors()
