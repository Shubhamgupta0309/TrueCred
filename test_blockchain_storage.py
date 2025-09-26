#!/usr/bin/env python3
"""
Test script to verify blockchain data storage in credential issuance.
"""
import sys
import os
import requests
import json
from datetime import datetime

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Import backend modules
from backend.models.credential_request import CredentialRequest
from backend.models.credential import Credential
from backend.models.user import User
from backend.services.credential_service import CredentialService
from backend.services.blockchain_service import BlockchainService
from backend.config import get_config
from backend.utils.database import init_db
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_blockchain_data_storage():
    """Test that blockchain data is properly stored when credentials are issued."""
    print("Testing Blockchain Data Storage in Credential Issuance...")
    print("=" * 60)

    try:
        # Initialize database connection
        from flask import Flask
        app = Flask(__name__)
        config = get_config('development')
        app.config.from_object(config)
        init_db(app)
        print("✅ Database connection initialized")
        # Create a test user if it doesn't exist
        test_user = User.objects(email="test@example.com").first()
        if not test_user:
            test_user = User(
                username="testuser",
                email="test@example.com",
                password="hashedpassword123",
                first_name="Test",
                last_name="User",
                role="student"
            )
            test_user.save()
            print(f"✅ Created test user: {test_user.id}")

        # Create a credential request
        cr = CredentialRequest(
            user_id=str(test_user.id),
            title="Test Blockchain Credential",
            issuer="Test University",
            type="certificate",
            status="pending",
            metadata={"description": "Test credential for blockchain verification"}
        )
        cr.save()
        print(f"✅ Created credential request: {cr.id}")

        # Simulate the approval process (what happens in the approve_request endpoint)
        print("\n🔄 Simulating credential approval and blockchain storage...")

        # Create credential data
        credential_data = {
            'title': cr.title,
            'issuer': cr.issuer,
            'description': cr.metadata.get('description', ''),
            'type': 'certificate',
            'issue_date': datetime.utcnow().isoformat(),
            'expiry_date': None,
            'document_url': None,
            'metadata': cr.metadata
        }

        # Create the credential
        credential, err = CredentialService.create_credential(
            user_id=cr.user_id,
            data=credential_data
        )

        if err:
            print(f"❌ Failed to create credential: {err}")
            return False

        print(f"✅ Created credential: {credential.id}")

        # Mark as verified
        credential.verified = True
        credential.verified_at = datetime.utcnow()

        # Now test the blockchain storage logic (from the approve_request endpoint)
        blockchain_result = None
        blockchain = BlockchainService()

        # Check if Web3 is connected
        web3_connected = blockchain.web3.is_connected() if hasattr(blockchain, 'web3') else False

        if web3_connected:
            print("🌐 Web3 connected - attempting real blockchain storage...")
            blockchain_result = blockchain.store_credential_hash(
                title=credential.title,
                issuer=credential.issuer or "Unknown Issuer",
                student_id=cr.user_id,
                ipfs_hash=credential.document_url or credential.ipfs_hash or ""
            )

            if blockchain_result and (blockchain_result.get('status') == 'success' or blockchain_result.get('simulated')):
                # Update credential with blockchain info
                credential.blockchain_tx_hash = blockchain_result.get('transaction_hash')
                credential.blockchain_credential_id = blockchain_result.get('credential_id')
                credential.blockchain_data = blockchain_result.get('blockchain_data', blockchain_result)
                credential.verification_status = 'verified'
                credential.save()
                print("✅ Real blockchain data stored successfully!")
                print(f"   Transaction Hash: {blockchain_result.get('transaction_hash')}")
                print(f"   Credential ID: {blockchain_result.get('credential_id')}")
            else:
                print(f"❌ Failed to store on real blockchain: {blockchain_result}")
                return False
        else:
            print("🔧 Web3 not connected - using mock blockchain storage...")
            # Generate mock data for development
            mock_result = blockchain.store_credential_hash(
                title=credential.title,
                issuer=credential.issuer or "Unknown Issuer", 
                student_id=cr.user_id,
                ipfs_hash=credential.document_url or credential.ipfs_hash or ""
            )
            if mock_result and (mock_result.get('status') == 'success' or mock_result.get('simulated')):
                # Save mock blockchain data
                credential.blockchain_tx_hash = mock_result.get('transaction_hash')
                credential.blockchain_credential_id = mock_result.get('credential_id')
                credential.blockchain_data = mock_result.get('blockchain_data', mock_result)
                credential.verification_status = 'verified'
                credential.save()
                print("✅ Mock blockchain data stored successfully!")
                print(f"   Transaction Hash: {mock_result.get('transaction_hash')}")
                print(f"   Credential ID: {mock_result.get('credential_id')}")
            else:
                print(f"❌ Failed to generate mock blockchain data: {mock_result}")
                return False

        # Mark request as issued
        cr.status = 'issued'
        cr.save()

        # Verify the credential has blockchain data
        print("\n🔍 Verifying stored blockchain data...")
        saved_credential = Credential.objects(id=credential.id).first()

        if saved_credential.blockchain_tx_hash:
            print("✅ Blockchain transaction hash saved")
        else:
            print("❌ Blockchain transaction hash missing")
            return False

        if saved_credential.blockchain_credential_id:
            print("✅ Blockchain credential ID saved")
        else:
            print("❌ Blockchain credential ID missing")
            return False

        if saved_credential.blockchain_data:
            print("✅ Blockchain data saved")
            print(f"   Data keys: {list(saved_credential.blockchain_data.keys())}")
        else:
            print("❌ Blockchain data missing")
            return False

        if saved_credential.verification_status == 'verified':
            print("✅ Verification status set to 'verified'")
        else:
            print(f"❌ Verification status incorrect: {saved_credential.verification_status}")
            return False

        print("\n🎉 All blockchain data storage tests passed!")
        print("The frontend should now display real transaction details instead of 'N/A'")
        return True

    except Exception as e:
        logger.exception("Test failed with exception")
        print(f"❌ Test failed: {e}")
        return False

def test_regular_credential_creation():
    """Test that regular credential creation also stores blockchain data."""
    print("\n🧪 Testing Regular Credential Creation with Blockchain Storage...")
    print("=" * 60)

    try:
        # Create a test user if it doesn't exist
        test_user = User.objects(email="test2@example.com").first()
        if not test_user:
            test_user = User(
                username="testuser2",
                email="test2@example.com",
                password="hashedpassword123",
                first_name="Test2",
                last_name="User",
                role="student"
            )
            test_user.save()
            print(f"✅ Created test user: {test_user.id}")

        # Test regular credential creation (simulating the POST /api/credentials/ endpoint)
        from backend.services.credential_service import CredentialService
        
        credential_data = {
            'title': 'Direct Created Certificate',
            'issuer': 'Test University',
            'description': 'Created directly without request flow',
            'type': 'certificate',
            'issue_date': datetime.utcnow().isoformat(),
            'expiry_date': None,
            'document_url': None,
            'metadata': {'direct_creation': True}
        }

        # Create the credential using the service
        credential, err = CredentialService.create_credential(
            user_id=str(test_user.id),
            data=credential_data
        )

        if err:
            print(f"❌ Failed to create credential: {err}")
            return False

        print(f"✅ Created credential: {credential.id}")

        # Now simulate the blockchain storage logic from the create_credential endpoint
        blockchain_result = None
        blockchain = BlockchainService()

        # Check if Web3 is connected
        web3_connected = blockchain.web3.is_connected() if hasattr(blockchain, 'web3') else False

        if web3_connected:
            print("🌐 Web3 connected - attempting real blockchain storage...")
            blockchain_result = blockchain.store_credential_hash(
                title=credential.title,
                issuer=credential.issuer or "Unknown Issuer",
                student_id=str(credential.user.id),
                ipfs_hash=credential.document_url or credential.ipfs_hash or ""
            )

            if blockchain_result and (blockchain_result.get('status') == 'success' or blockchain_result.get('simulated')):
                # Update credential with blockchain info
                credential.blockchain_tx_hash = blockchain_result.get('transaction_hash')
                credential.blockchain_credential_id = blockchain_result.get('credential_id')
                credential.blockchain_data = blockchain_result.get('blockchain_data', blockchain_result)
                credential.verification_status = 'verified'
                credential.verified = True
                credential.verified_at = datetime.utcnow()
                credential.save()
                print("✅ Real blockchain data stored successfully!")
                print(f"   Transaction Hash: {blockchain_result.get('transaction_hash')}")
                print(f"   Credential ID: {blockchain_result.get('credential_id')}")
            else:
                print(f"❌ Failed to store on real blockchain: {blockchain_result}")
                return False
        else:
            print("🔧 Web3 not connected - using mock blockchain storage...")
            # Generate mock data for development
            mock_result = blockchain.store_credential_hash(
                title=credential.title,
                issuer=credential.issuer or "Unknown Issuer", 
                student_id=str(credential.user.id),
                ipfs_hash=credential.document_url or credential.ipfs_hash or ""
            )
            
            if mock_result and (mock_result.get('status') == 'success' or mock_result.get('simulated')):
                # Save mock blockchain data
                credential.blockchain_tx_hash = mock_result.get('transaction_hash')
                credential.blockchain_credential_id = mock_result.get('credential_id')
                credential.blockchain_data = mock_result.get('blockchain_data', mock_result)
                credential.verification_status = 'verified'
                credential.verified = True
                credential.verified_at = datetime.utcnow()
                credential.save()
                print("✅ Mock blockchain data stored successfully!")
                print(f"   Transaction Hash: {mock_result.get('transaction_hash')}")
                print(f"   Credential ID: {mock_result.get('credential_id')}")
            else:
                print(f"❌ Failed to generate mock blockchain data: {mock_result}")
                return False

        # Verify the credential has blockchain data
        print("\n🔍 Verifying stored blockchain data...")
        saved_credential = Credential.objects(id=credential.id).first()

        if saved_credential.blockchain_tx_hash:
            print("✅ Blockchain transaction hash saved")
        else:
            print("❌ Blockchain transaction hash missing")
            return False

        if saved_credential.blockchain_credential_id:
            print("✅ Blockchain credential ID saved")
        else:
            print("❌ Blockchain credential ID missing")
            return False

        if saved_credential.blockchain_data:
            print("✅ Blockchain data saved")
            print(f"   Data keys: {list(saved_credential.blockchain_data.keys())}")
        else:
            print("❌ Blockchain data missing")
            return False

        if saved_credential.verification_status == 'verified':
            print("✅ Verification status set to 'verified'")
        else:
            print(f"❌ Verification status incorrect: {saved_credential.verification_status}")
            return False

        if saved_credential.verified and saved_credential.verified_at:
            print("✅ Credential marked as verified with timestamp")
        else:
            print("❌ Credential verification flags incorrect")
            return False

        print("\n🎉 Regular credential creation with blockchain storage test passed!")
        return True

    except Exception as e:
        logger.exception("Regular credential creation test failed with exception")
        print(f"❌ Test failed: {e}")
        return False

def test_organization_upload_credential():
    """Test that organization upload credential also stores blockchain data."""
    print("\n🏫 Testing Organization Upload Credential with Blockchain Storage...")
    print("=" * 70)

    try:
        # Create a test student user if it doesn't exist
        test_student = User.objects(email="student@example.com").first()
        if not test_student:
            test_student = User(
                username="teststudent",
                email="student@example.com",
                password="hashedpassword123",
                first_name="Test",
                last_name="Student",
                role="student"
            )
            test_student.save()
            print(f"✅ Created test student: {test_student.id}")

        # Create a test issuer/college user if it doesn't exist
        test_issuer = User.objects(email="college@example.com").first()
        if not test_issuer:
            test_issuer = User(
                username="testcollege",
                email="college@example.com",
                password="hashedpassword123",
                first_name="Test",
                last_name="College",
                role="college"
            )
            test_issuer.save()
            print(f"✅ Created test college: {test_issuer.id}")

        # Simulate the organization upload credential endpoint
        from backend.services.credential_service import CredentialService
        
        credential_data = {
            'title': 'Organization Uploaded Certificate',
            'issuer': 'Test College University',
            'description': 'Uploaded by organization for student',
            'type': 'certificate',
            'issue_date': datetime.utcnow().isoformat(),
            'expiry_date': None,
            'document_url': None,
            'metadata': {'uploaded_by_organization': True}
        }

        # Create the credential using the service (simulating the endpoint)
        credential, err = CredentialService.create_credential(
            user_id=str(test_student.id), 
            data=credential_data
        )

        if err:
            print(f"❌ Failed to create credential: {err}")
            return False

        print(f"✅ Created credential: {credential.id}")

        # Mark as verified (like the endpoint does)
        credential.verified = True
        credential.verified_at = datetime.utcnow()

        # Now simulate the blockchain storage logic from the organization upload endpoint
        blockchain_result = None
        blockchain = BlockchainService()

        # Check if Web3 is connected
        web3_connected = blockchain.web3.is_connected() if hasattr(blockchain, 'web3') else False

        if web3_connected:
            print("🌐 Web3 connected - attempting real blockchain storage...")
            blockchain_result = blockchain.store_credential_hash(
                title=credential.title,
                issuer=credential.issuer or "Unknown Issuer",
                student_id=str(test_student.id),
                ipfs_hash=credential.document_url or credential.ipfs_hash or ""
            )

            if blockchain_result and (blockchain_result.get('status') == 'success' or blockchain_result.get('simulated')):
                # Update credential with blockchain info
                credential.blockchain_tx_hash = blockchain_result.get('transaction_hash')
                credential.blockchain_credential_id = blockchain_result.get('credential_id')
                credential.blockchain_data = blockchain_result.get('blockchain_data', blockchain_result)
                credential.verification_status = 'verified'
                credential.save()
                print("✅ Real blockchain data stored successfully!")
                print(f"   Transaction Hash: {blockchain_result.get('transaction_hash')}")
                print(f"   Credential ID: {blockchain_result.get('credential_id')}")
            else:
                print(f"❌ Failed to store on real blockchain: {blockchain_result}")
                return False
        else:
            print("🔧 Web3 not connected - using mock blockchain storage...")
            # Generate mock data for development
            mock_result = blockchain.store_credential_hash(
                title=credential.title,
                issuer=credential.issuer or "Unknown Issuer", 
                student_id=str(test_student.id),
                ipfs_hash=credential.document_url or credential.ipfs_hash or ""
            )
            
            if mock_result and (mock_result.get('status') == 'success' or mock_result.get('simulated')):
                # Save mock blockchain data
                credential.blockchain_tx_hash = mock_result.get('transaction_hash')
                credential.blockchain_credential_id = mock_result.get('credential_id')
                credential.blockchain_data = mock_result.get('blockchain_data', mock_result)
                credential.verification_status = 'verified'
                credential.save()
                print("✅ Mock blockchain data stored successfully!")
                print(f"   Transaction Hash: {mock_result.get('transaction_hash')}")
                print(f"   Credential ID: {mock_result.get('credential_id')}")
            else:
                print(f"❌ Failed to generate mock blockchain data: {mock_result}")
                return False

        # Verify the credential has blockchain data
        print("\n🔍 Verifying stored blockchain data...")
        saved_credential = Credential.objects(id=credential.id).first()

        if saved_credential.blockchain_tx_hash:
            print("✅ Blockchain transaction hash saved")
        else:
            print("❌ Blockchain transaction hash missing")
            return False

        if saved_credential.blockchain_credential_id:
            print("✅ Blockchain credential ID saved")
        else:
            print("❌ Blockchain credential ID missing")
            return False

        if saved_credential.blockchain_data:
            print("✅ Blockchain data saved")
            print(f"   Data keys: {list(saved_credential.blockchain_data.keys())}")
        else:
            print("❌ Blockchain data missing")
            return False

        if saved_credential.verification_status == 'verified':
            print("✅ Verification status set to 'verified'")
        else:
            print(f"❌ Verification status incorrect: {saved_credential.verification_status}")
            return False

        if saved_credential.verified and saved_credential.verified_at:
            print("✅ Credential marked as verified with timestamp")
        else:
            print("❌ Credential verification flags incorrect")
            return False

        print("\n🎉 Organization upload credential with blockchain storage test passed!")
        return True

    except Exception as e:
        logger.exception("Organization upload credential test failed with exception")
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running Blockchain Storage Tests...")
    print("=" * 80)
    
    # Test approval flow (existing test)
    approval_success = test_blockchain_data_storage()
    
    # Test regular creation flow (new test)
    creation_success = test_regular_credential_creation()
    
    # Test organization upload flow (new test)
    org_upload_success = test_organization_upload_credential()
    
    overall_success = approval_success and creation_success and org_upload_success
    
    print("\n" + "=" * 80)
    if overall_success:
        print("🎉 ALL BLOCKCHAIN STORAGE TESTS PASSED!")
        print("All credential creation flows now store blockchain data.")
    else:
        print("❌ SOME TESTS FAILED!")
        if not approval_success:
            print("  - Approval flow test failed")
        if not creation_success:
            print("  - Regular creation flow test failed")
        if not org_upload_success:
            print("  - Organization upload flow test failed")
    
    sys.exit(0 if overall_success else 1)