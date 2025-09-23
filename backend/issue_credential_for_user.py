import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

from backend.models.user import User
from backend.models.credential import Credential
from backend.services.credential_service import CredentialService
from backend.services.blockchain_service import BlockchainService
from backend.utils.database import init_db

# Initialize database
init_db()

# User ID provided
user_id = "68c131bf98c40661753abba0"

# Find the user
user = User.objects(id=user_id).first()
if not user:
    print(f"User with ID {user_id} not found")
    exit(1)

print(f"Found user: {user.email}")

# Create a test credential
cred_data = {
    "title": "Test Blockchain Credential",
    "issuer": "Test Issuer",
    "recipient": user.email,
    "issue_date": "2025-09-23",
    "description": "Test credential for blockchain verification",
    "ipfs_hash": "QmTestHash123"
}

# Create credential
cred_service = CredentialService()
credential = cred_service.create_credential(user_id, cred_data)
if not credential:
    print("Failed to create credential")
    exit(1)

print(f"Created credential: {credential.id}")

# Issue on blockchain
blockchain = BlockchainService()
if not blockchain.is_connected():
    print("Blockchain not connected")
    exit(1)

# Call store_credential_hash (this issues on-chain)
result = blockchain.store_credential_hash(
    title=credential.title,
    issuer=credential.issuer,
    student_id=user.email,
    ipfs_hash=credential.ipfs_hash
)

if result.get('status') == 'success':
    # Update credential with blockchain data
    credential.blockchain_tx_hash = result.get('transaction_hash')
    credential.blockchain_credential_id = result.get('credential_id')
    credential.blockchain_data = result
    credential.verification_status = 'verified'
    credential.save()

    print("Credential issued on-chain successfully")
    print(f"Transaction Hash: {credential.blockchain_tx_hash}")
    print(f"Block Number: {result.get('block_number')}")
    print(f"Timestamp: {result.get('timestamp', 'N/A')}")
    print(f"Verified At: 2025-09-23")  # Current date
else:
    print(f"Failed to issue on-chain: {result}")

# Now verify the credential
verification_result = blockchain.verify_credential(result.get('credential_id'))
if verification_result:
    print("\nVerification Details:")
    print(f"Transaction Hash: {credential.blockchain_tx_hash}")
    print(f"Block Number: {result.get('block_number')}")
    print(f"Timestamp: {verification_result.get('timestamp', 'N/A')}")
    print(f"Verified At: Sep 23, 2025")
else:
    print("Verification failed")