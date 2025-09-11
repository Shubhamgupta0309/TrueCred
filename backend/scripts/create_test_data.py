#!/usr/bin/env python3
"""
Add test data to TrueCred system with real documents and credentials.
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from models.user import User
from models.credential import Credential
from models.experience import Experience
from services.blockchain_service import BlockchainService
from services.ipfs_service import IPFSService
from utils.database import init_db

def create_test_data():
    """Create test users, credentials and experiences with real data."""
    print("Creating test data...")
    
    # Initialize services
    blockchain_service = BlockchainService()
    ipfs_service = IPFSService()
    
    # Create test users
    print("\nCreating users...")
    
    # College admin
    college_admin = User(
        username="harvard_admin",
        email="admin@harvard.edu",
        role="college",
        organization="Harvard University",
        is_email_verified=True
    ).save()
    college_admin.set_password("Test@123")
    college_admin.save()
    print(f"Created college admin: {college_admin.email}")
    
    # Company admin
    company_admin = User(
        username="google_admin",
        email="admin@google.com",
        role="company",
        organization="Google",
        is_email_verified=True
    ).save()
    company_admin.set_password("Test@123")
    company_admin.save()
    print(f"Created company admin: {company_admin.email}")
    
    # Student/Employee
    student = User(
        username="john_doe",
        email="john@example.com",
        role="user",
        first_name="John",
        last_name="Doe",
        is_email_verified=True
    ).save()
    student.set_password("Test@123")
    student.save()
    print(f"Created student: {student.email}")
    
    # Create a test credential
    print("\nCreating credential...")
    
    # Create a sample degree certificate
    certificate_content = """
    HARVARD UNIVERSITY
    
    This is to certify that
    
    John Doe
    
    has successfully completed the requirements for the degree of
    
    Bachelor of Science in Computer Science
    
    Awarded on September 1, 2025
    """
    
    # Store certificate in IPFS
    certificate_bytes = certificate_content.encode('utf-8')
    ipfs_result = ipfs_service.store_document(certificate_bytes, {
        'filename': 'harvard_degree.txt',
        'mime_type': 'text/plain',
        'created_at': datetime.utcnow().isoformat()
    })
    
    document_hash = ipfs_result['hash']
    print(f"Certificate stored in IPFS with hash: {document_hash}")
    
    # Create credential record
    credential = Credential(
        user=student,
        issuer=college_admin,
        credential_type="degree",
        title="Bachelor of Science in Computer Science",
        institution="Harvard University",
        issue_date=datetime(2025, 9, 1),
        document_hash=document_hash,
        status="issued"
    ).save()
    
    # Verify on blockchain
    tx_hash = blockchain_service.verify_credential(
        credential.id,
        document_hash,
        college_admin.id
    )
    
    credential.blockchain_tx = tx_hash
    credential.verified = True
    credential.save()
    
    print(f"Created verified credential with ID: {credential.id}")
    print(f"Blockchain transaction hash: {tx_hash}")
    
    # Create test experience
    print("\nCreating experience...")
    
    # Create experience letter
    letter_content = """
    GOOGLE
    
    To Whom It May Concern,
    
    This letter confirms that John Doe was employed at Google
    as a Software Engineer from March 1, 2025 to September 1, 2025.
    
    During his tenure, John demonstrated excellent technical skills
    and was a valuable member of our team.
    
    Regards,
    HR Department
    Google
    """
    
    # Store letter in IPFS
    letter_bytes = letter_content.encode('utf-8')
    ipfs_result = ipfs_service.store_document(letter_bytes, {
        'filename': 'google_experience.txt',
        'mime_type': 'text/plain',
        'created_at': datetime.utcnow().isoformat()
    })
    
    letter_hash = ipfs_result['hash']
    print(f"Experience letter stored in IPFS with hash: {letter_hash}")
    
    # Create experience record
    experience = Experience(
        user=student,
        issuer=company_admin,
        company="Google",
        position="Software Engineer",
        start_date=datetime(2025, 3, 1),
        end_date=datetime(2025, 9, 1),
        document_hash=letter_hash,
        status="issued"
    ).save()
    
    # Verify on blockchain
    tx_hash = blockchain_service.verify_experience(
        experience.id,
        letter_hash,
        company_admin.id
    )
    
    experience.blockchain_tx = tx_hash
    experience.verified = True
    experience.save()
    
    print(f"Created verified experience with ID: {experience.id}")
    print(f"Blockchain transaction hash: {tx_hash}")
    
    print("\nTest data creation complete!")
    print("\nLogin credentials:")
    print("1. Student:")
    print("   Email: john@example.com")
    print("   Password: Test@123")
    print("\n2. College Admin:")
    print("   Email: admin@harvard.edu")
    print("   Password: Test@123")
    print("\n3. Company Admin:")
    print("   Email: admin@google.com")
    print("   Password: Test@123")

if __name__ == "__main__":
    # Import and create Flask app
    from app import create_app
    app = create_app()
    
    # Initialize database with app context
    with app.app_context():
        init_db(app)
        create_test_data()
