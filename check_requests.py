#!/usr/bin/env python3
"""
Check credential requests in database
"""
import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.dirname(__file__)
sys.path.insert(0, backend_path)

from models.credential_request import CredentialRequest
from models.user import User

def check_requests():
    # Check if there are any credential requests
    requests = CredentialRequest.objects.all()
    print(f'Total credential requests: {len(requests)}')

    for req in requests:
        print(f'ID: {req.id}, Title: {req.title}, Status: {req.status}')
        print(f'Issuer: {req.issuer}, Issuer_ID: {req.issuer_id}')

        # Get user info
        user = User.objects(id=req.user_id).first()
        if user:
            print(f'User: {user.username} ({user.email})')
        else:
            print('User: Not found')
        print('---')

if __name__ == "__main__":
    check_requests()