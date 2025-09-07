"""
Test script for the IPFS integration.

This script tests the IPFS service and model integration.
"""
import os
import sys
import json
from datetime import datetime
import base64

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the necessary modules
from services.ipfs_service import IPFSService
from models.credential import Credential
from models.experience import Experience
from models.user import User
from utils.database import init_db

def test_ipfs_service():
    """
    Test the IPFS service.
    """
    print("Testing IPFS service...")
    
    # Initialize IPFS service
    ipfs = IPFSService()
    
    # Connect to IPFS
    connected = ipfs.connect()
    print(f"IPFS connected: {connected}")
    
    if not connected:
        print("Failed to connect to IPFS node. Make sure the IPFS daemon is running.")
        return False
    
    # Test node info
    node_info = ipfs.get_node_info()
    print(f"IPFS Node ID: {node_info.get('ID')}")
    
    # Test adding a file
    test_data = f"Test data at {datetime.utcnow().isoformat()}".encode('utf-8')
    file_result = ipfs.add_file(test_data, filename="test.txt")
    
    if 'error' in file_result:
        print(f"Error adding file: {file_result['error']}")
        return False
        
    print(f"File added with hash: {file_result['Hash']}")
    
    # Test adding JSON
    test_json = {
        "test": True,
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "number": 42,
            "text": "Hello, IPFS!",
            "list": [1, 2, 3, 4, 5]
        }
    }
    
    json_result = ipfs.add_json(test_json)
    
    if 'error' in json_result:
        print(f"Error adding JSON: {json_result['error']}")
        return False
        
    print(f"JSON added with hash: {json_result['Hash']}")
    
    # Test retrieving the file
    file_data = ipfs.get_file(file_result['Hash'])
    print(f"Retrieved file data: {file_data.decode('utf-8')}")
    
    # Test retrieving the JSON
    json_data = ipfs.get_json(json_result['Hash'])
    print(f"Retrieved JSON data: {json.dumps(json_data, indent=2)}")
    
    # Test storing a document with metadata
    document_result = ipfs.store_document(
        test_data,
        {
            "filename": "test_document.txt",
            "description": "Test document for IPFS integration",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    if 'error' in document_result:
        print(f"Error storing document: {document_result['error']}")
        return False
        
    print(f"Document stored with hash: {document_result['document_hash']}")
    print(f"Metadata stored with hash: {document_result['metadata_hash']}")
    
    # Test gateway URL
    gateway_url = ipfs.get_gateway_url(file_result['Hash'])
    print(f"Gateway URL: {gateway_url}")
    
    # Test pinning
    pin_result = ipfs.pin_hash(file_result['Hash'])
    
    if 'error' in pin_result:
        print(f"Error pinning hash: {pin_result['error']}")
    else:
        print(f"Pinned hash: {file_result['Hash']}")
    
    # Disconnect from IPFS
    ipfs.disconnect()
    print("IPFS service test completed successfully!")
    return True

def test_model_ipfs_integration():
    """
    Test the IPFS integration with the models.
    """
    print("Testing model IPFS integration...")
    
    # Initialize database
    init_db()
    
    # Find or create a test user
    try:
        user = User.objects.get(username="ipfs_test_user")
        print(f"Using existing user: {user.username}")
    except User.DoesNotExist:
        # Create a new user
        user = User(
            username="ipfs_test_user",
            email="ipfs_test@example.com",
            first_name="IPFS",
            last_name="Test"
        )
        user.set_password("testpassword")
        user.save()
        print(f"Created new user: {user.username}")
    
    # Create a test credential
    credential = Credential(
        user=user,
        title="IPFS Test Credential",
        issuer="IPFS Testing Authority",
        description="A test credential for IPFS integration",
        type="certificate",
        issue_date=datetime.utcnow()
    )
    credential.save()
    print(f"Created credential: {credential.title}")
    
    # Create a test experience
    experience = Experience(
        user=user,
        title="IPFS Test Experience",
        organization="IPFS Testing Corp",
        description="A test experience for IPFS integration",
        type="work",
        start_date=datetime.utcnow()
    )
    experience.save()
    print(f"Created experience: {experience.title}")
    
    # Initialize IPFS service
    ipfs = IPFSService()
    
    # Connect to IPFS
    connected = ipfs.connect()
    
    if not connected:
        print("Failed to connect to IPFS node. Make sure the IPFS daemon is running.")
        return False
    
    # Test storing credential in IPFS
    try:
        # Create test document
        credential_doc = f"""
        # Certificate of Completion
        
        This certifies that **{user.first_name} {user.last_name}** has successfully completed
        the IPFS Integration Test on {datetime.utcnow().strftime('%B %d, %Y')}.
        
        Issued by: IPFS Testing Authority
        """
        
        # Store credential in IPFS
        credential.store_in_ipfs(
            ipfs,
            credential_doc.encode('utf-8'),
            {
                "test": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        print(f"Credential stored in IPFS with hash: {credential.ipfs_hash}")
        print(f"Credential metadata stored with hash: {credential.ipfs_metadata_hash}")
        
        # Add an additional document
        credential.add_document_to_ipfs(
            ipfs,
            b"This is an additional document for the credential.",
            "additional_document"
        )
        
        print(f"Added document to credential with hashes: {credential.document_hashes}")
    except Exception as e:
        print(f"Error testing credential IPFS integration: {str(e)}")
        return False
    
    # Test storing experience in IPFS
    try:
        # Create test document
        experience_doc = f"""
        # Work Experience Verification
        
        This verifies that **{user.first_name} {user.last_name}** has experience working
        with IPFS integration at IPFS Testing Corp.
        
        Position: Test Developer
        Duration: {datetime.utcnow().strftime('%B %Y')} - Present
        """
        
        # Store experience in IPFS
        experience.store_in_ipfs(
            ipfs,
            experience_doc.encode('utf-8'),
            {
                "test": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        print(f"Experience stored in IPFS with hash: {experience.ipfs_hash}")
        print(f"Experience metadata stored with hash: {experience.ipfs_metadata_hash}")
        
        # Add an additional document
        experience.add_document_to_ipfs(
            ipfs,
            b"This is an additional document for the experience.",
            "additional_document"
        )
        
        print(f"Added document to experience with hashes: {experience.document_hashes}")
    except Exception as e:
        print(f"Error testing experience IPFS integration: {str(e)}")
        return False
    
    # Disconnect from IPFS
    ipfs.disconnect()
    print("Model IPFS integration test completed successfully!")
    return True

if __name__ == "__main__":
    print("IPFS Integration Test")
    print("====================")
    
    # Test IPFS service
    service_success = test_ipfs_service()
    
    if not service_success:
        print("IPFS service test failed!")
        sys.exit(1)
    
    print("\n")
    
    # Test model integration
    model_success = test_model_ipfs_integration()
    
    if not model_success:
        print("Model IPFS integration test failed!")
        sys.exit(1)
    
    print("\nAll tests completed successfully!")
