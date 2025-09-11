#!/usr/bin/env python3
"""
TrueCred Blockchain Integration Test Script
This script tests the full functionality of the blockchain integration.
"""
import json
import os
import requests
import time
from pathlib import Path
from pprint import pprint

# Base URL for the TrueCred API
BASE_URL = "http://localhost:5000/api"

def test_blockchain_status():
    """Test the blockchain connection status endpoint."""
    print("\n=== Testing Blockchain Status ===")
    response = requests.get(f"{BASE_URL}/blockchain/status")
    
    if response.status_code == 200:
        print("✅ Blockchain status endpoint works")
        pprint(response.json())
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False

def test_issue_credential():
    """Test issuing a credential on the blockchain."""
    print("\n=== Testing Issue Credential ===")
    
    # Test data
    data = {
        "subject": "0x1234567890123456789012345678901234567890",
        "credential_type": "Diploma",
        "metadata_uri": "ipfs://QmXZLbCpvJ6dxQBX3CqbMF8jQUvDTVhJoiDvxaQDpF9Ab4",
        "expiration_date": int(time.time()) + 31536000  # 1 year from now
    }
    
    response = requests.post(f"{BASE_URL}/blockchain/credentials/issue", json=data)
    
    if response.status_code == 201:
        print("✅ Issue credential endpoint works")
        result = response.json()
        pprint(result)
        
        # Save credential ID for later tests
        credential_id = result.get("credential_id")
        print(f"Credential ID: {credential_id}")
        
        return credential_id
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

def test_batch_issue_credentials():
    """Test batch issuing credentials on the blockchain."""
    print("\n=== Testing Batch Issue Credentials ===")
    
    # Test data
    data = {
        "subjects": [
            "0x1234567890123456789012345678901234567890",
            "0x2345678901234567890123456789012345678901"
        ],
        "credential_types": [
            "Certificate",
            "Badge"
        ],
        "metadata_uris": [
            "ipfs://QmXZLbCpvJ6dxQBX3CqbMF8jQUvDTVhJoiDvxaQDpF9Ab4",
            "ipfs://QmYZLbCpvJ6dxQBX3CqbMF8jQUvDTVhJoiDvxaQDpF9Ab5"
        ],
        "expiration_dates": [
            int(time.time()) + 31536000,  # 1 year from now
            int(time.time()) + 63072000   # 2 years from now
        ]
    }
    
    response = requests.post(f"{BASE_URL}/blockchain/credentials/batch-issue", json=data)
    
    if response.status_code == 201:
        print("✅ Batch issue credentials endpoint works")
        result = response.json()
        pprint(result)
        
        # Save credential IDs for later tests
        credential_ids = result.get("credential_ids", [])
        print(f"Credential IDs: {credential_ids}")
        
        return credential_ids
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

def test_verify_credential(credential_id):
    """Test verifying a credential on the blockchain."""
    print("\n=== Testing Verify Credential ===")
    
    if not credential_id:
        print("❌ No credential ID provided, skipping test")
        return False
    
    data = {
        "credential_id": credential_id
    }
    
    response = requests.post(f"{BASE_URL}/blockchain/credentials/verify", json=data)
    
    if response.status_code == 200:
        print("✅ Verify credential endpoint works")
        pprint(response.json())
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False

def test_get_credential_details(credential_id):
    """Test getting credential details from the blockchain."""
    print("\n=== Testing Get Credential Details ===")
    
    if not credential_id:
        print("❌ No credential ID provided, skipping test")
        return False
    
    data = {
        "credential_id": credential_id
    }
    
    response = requests.post(f"{BASE_URL}/blockchain/credentials/details", json=data)
    
    if response.status_code == 200:
        print("✅ Get credential details endpoint works")
        pprint(response.json())
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False

def test_revoke_credential(credential_id):
    """Test revoking a credential on the blockchain."""
    print("\n=== Testing Revoke Credential ===")
    
    if not credential_id:
        print("❌ No credential ID provided, skipping test")
        return False
    
    data = {
        "credential_id": credential_id
    }
    
    response = requests.post(f"{BASE_URL}/blockchain/credentials/revoke", json=data)
    
    if response.status_code == 200:
        print("✅ Revoke credential endpoint works")
        pprint(response.json())
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False

def test_get_subject_credentials():
    """Test getting credentials for a subject."""
    print("\n=== Testing Get Subject Credentials ===")
    
    subject_address = "0x1234567890123456789012345678901234567890"
    
    response = requests.get(f"{BASE_URL}/blockchain/credentials/subject/{subject_address}")
    
    if response.status_code == 200:
        print("✅ Get subject credentials endpoint works")
        pprint(response.json())
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False

def test_get_issuer_credentials():
    """Test getting credentials issued by an issuer."""
    print("\n=== Testing Get Issuer Credentials ===")
    
    issuer_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"  # Our mock deployer address
    
    response = requests.get(f"{BASE_URL}/blockchain/credentials/issuer/{issuer_address}")
    
    if response.status_code == 200:
        print("✅ Get issuer credentials endpoint works")
        pprint(response.json())
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False

def test_is_authorized_issuer():
    """Test checking if an address is an authorized issuer."""
    print("\n=== Testing Is Authorized Issuer ===")
    
    issuer_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"  # Our mock deployer address
    
    response = requests.get(f"{BASE_URL}/blockchain/issuers/check/{issuer_address}")
    
    if response.status_code == 200:
        print("✅ Is authorized issuer endpoint works")
        pprint(response.json())
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False

def test_authorize_issuer():
    """Test authorizing an issuer."""
    print("\n=== Testing Authorize Issuer ===")
    
    data = {
        "issuer": "0x3456789012345678901234567890123456789012"
    }
    
    response = requests.post(f"{BASE_URL}/blockchain/issuers/authorize", json=data)
    
    if response.status_code == 200:
        print("✅ Authorize issuer endpoint works")
        pprint(response.json())
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False

def test_revoke_issuer():
    """Test revoking an issuer's authorization."""
    print("\n=== Testing Revoke Issuer ===")
    
    data = {
        "issuer": "0x3456789012345678901234567890123456789012"
    }
    
    response = requests.post(f"{BASE_URL}/blockchain/issuers/revoke", json=data)
    
    if response.status_code == 200:
        print("✅ Revoke issuer endpoint works")
        pprint(response.json())
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False

def test_sign_message():
    """Test signing a message."""
    print("\n=== Testing Sign Message ===")
    
    data = {
        "message": "This is a test message for TrueCred verification."
    }
    
    response = requests.post(f"{BASE_URL}/blockchain/sign", json=data)
    
    if response.status_code == 200:
        print("✅ Sign message endpoint works")
        result = response.json()
        pprint(result)
        
        # Save signature for verification test
        signature = result.get("signature")
        signer = result.get("signer")
        message = result.get("message")
        
        return {
            "signature": signature,
            "signer": signer,
            "message": message
        }
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

def test_verify_signature(signature_data):
    """Test verifying a signature."""
    print("\n=== Testing Verify Signature ===")
    
    if not signature_data:
        print("❌ No signature data provided, skipping test")
        return False
    
    data = {
        "message": signature_data["message"],
        "signature": signature_data["signature"],
        "address": signature_data["signer"]
    }
    
    response = requests.post(f"{BASE_URL}/blockchain/verify-signature", json=data)
    
    if response.status_code == 200:
        print("✅ Verify signature endpoint works")
        pprint(response.json())
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False

def run_all_tests():
    """Run all blockchain integration tests."""
    print("Starting TrueCred Blockchain Integration Tests...")
    
    # Test blockchain status
    test_blockchain_status()
    
    # Test issuing credentials
    credential_id = test_issue_credential()
    batch_credential_ids = test_batch_issue_credentials()
    
    # Use the first credential from the batch if the single issue failed
    if not credential_id and batch_credential_ids:
        credential_id = batch_credential_ids[0]
    
    # Test credential operations
    test_verify_credential(credential_id)
    test_get_credential_details(credential_id)
    test_revoke_credential(credential_id)
    
    # Test getting credentials
    test_get_subject_credentials()
    test_get_issuer_credentials()
    
    # Test issuer operations
    test_is_authorized_issuer()
    test_authorize_issuer()
    test_revoke_issuer()
    
    # Test signature operations
    signature_data = test_sign_message()
    test_verify_signature(signature_data)
    
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    run_all_tests()
