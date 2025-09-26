import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

from backend.models.credential import Credential
from backend.utils.database import init_db

# Initialize database
init_db()

# Find the latest credential (assuming the test created one)
cred = Credential.objects().order_by('-created_at').first()

if cred:
    print("Credential found:")
    print(f"ID: {cred.id}")
    print(f"Title: {cred.title}")
    print(f"Blockchain TX Hash: {cred.blockchain_tx_hash or 'N/A'}")
    print(f"Blockchain Credential ID: {cred.blockchain_credential_id or 'N/A'}")
    print(f"Blockchain Data: {cred.blockchain_data or 'N/A'}")
    print(f"Verification Status: {cred.verification_status or 'N/A'}")
else:
    print("No credentials found")