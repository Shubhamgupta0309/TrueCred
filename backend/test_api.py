#!/usr/bin/env python3
"""
Test API endpoints without authentication
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Health endpoint status: {response.status_code}")
        print(f"Health response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health endpoint failed: {e}")
        return False

def test_college_profile_endpoint():
    """Test college profile endpoint (should fail without auth)"""
    try:
        response = requests.get(f"{BASE_URL}/api/college/profile")
        print(f"College profile endpoint status: {response.status_code}")
        print(f"College profile response: {response.text}")
        return response.status_code == 401  # Should be unauthorized
    except Exception as e:
        print(f"College profile endpoint failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing API endpoints...")
    print("=" * 50)

    health_ok = test_health_endpoint()
    print()

    profile_ok = test_college_profile_endpoint()
    print()

    if health_ok:
        print("✅ Server is running and health endpoint works")
    else:
        print("❌ Server health check failed")

    if profile_ok:
        print("✅ Authentication is working (endpoint properly rejects unauthorized requests)")
    else:
        print("❌ Authentication check failed")