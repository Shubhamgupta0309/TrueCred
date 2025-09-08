"""
Script to demonstrate authentication with the TrueCred API.
"""
import requests
import json
import getpass

BASE_URL = "http://localhost:5000"

def print_response(response):
    """Print response in a readable format."""
    print(f"Status Code: {response.status_code}")
    try:
        json_response = response.json()
        print(json.dumps(json_response, indent=2))
        return json_response
    except:
        print(response.text)
        return None
    finally:
        print("-" * 50)

def register_user():
    """Register a new user."""
    print("\n=== REGISTER A NEW USER ===")
    
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = getpass.getpass("Enter password: ")
    first_name = input("Enter first name (optional): ")
    last_name = input("Enter last name (optional): ")
    
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    if first_name:
        data["first_name"] = first_name
    
    if last_name:
        data["last_name"] = last_name
    
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=data
    )
    
    return print_response(response)

def login_user():
    """Login a user."""
    print("\n=== LOGIN ===")
    
    username_or_email = input("Enter username or email: ")
    password = getpass.getpass("Enter password: ")
    
    data = {
        "username_or_email": username_or_email,
        "password": password
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=data
    )
    
    return print_response(response)

def get_profile(access_token):
    """Get user profile."""
    print("\n=== GET PROFILE ===")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/auth/profile",
        headers=headers
    )
    
    return print_response(response)

def update_profile(access_token):
    """Update user profile."""
    print("\n=== UPDATE PROFILE ===")
    
    first_name = input("Enter new first name: ")
    last_name = input("Enter new last name: ")
    
    data = {}
    if first_name:
        data["first_name"] = first_name
    if last_name:
        data["last_name"] = last_name
    
    if not data:
        print("No updates provided.")
        return None
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.put(
        f"{BASE_URL}/api/auth/profile",
        headers=headers,
        json=data
    )
    
    return print_response(response)

def logout(access_token):
    """Logout user."""
    print("\n=== LOGOUT ===")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/logout",
        headers=headers
    )
    
    return print_response(response)

def main():
    """Main function to demonstrate the auth flow."""
    print("=== TRUECRED AUTHENTICATION DEMO ===")
    print("1. Register a new user")
    print("2. Login with existing user")
    choice = input("Choose an option (1/2): ")
    
    if choice == "1":
        result = register_user()
        if result and result.get("success"):
            tokens = result.get("tokens", {})
            access_token = tokens.get("access_token")
            
            if access_token:
                get_profile(access_token)
                update_profile(access_token)
                logout(access_token)
    elif choice == "2":
        result = login_user()
        if result and result.get("success"):
            tokens = result.get("tokens", {})
            access_token = tokens.get("access_token")
            
            if access_token:
                get_profile(access_token)
                update_profile(access_token)
                logout(access_token)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
