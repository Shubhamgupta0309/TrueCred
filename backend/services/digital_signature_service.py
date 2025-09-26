"""
Digital signature service for the TrueCred application.

This service provides functionality to create and verify digital signatures
for credentials and experiences, preparing them for blockchain storage.
"""
import hashlib
import json
import base64
import time
import logging
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key, load_pem_public_key,
    Encoding, PrivateFormat, PublicFormat, NoEncryption
)
from cryptography.exceptions import InvalidSignature
from models.credential import Credential
from models.experience import Experience

# Set up logging
logger = logging.getLogger(__name__)

class DigitalSignatureService:
    """
    Service for creating and verifying digital signatures for TrueCred.
    
    This service handles:
    - Generating key pairs for signing
    - Creating signatures for credentials and experiences
    - Verifying signatures
    - Preparing data for blockchain storage
    """
    
    @staticmethod
    def generate_key_pair():
        """
        Generate an RSA key pair for digital signatures.
        
        Returns:
            tuple: (private_key_pem, public_key_pem) as strings
        """
        # Generate a private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        # Get the public key
        public_key = private_key.public_key()
        
        # Serialize keys to PEM format
        private_key_pem = private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption()
        ).decode('utf-8')
        
        public_key_pem = public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return private_key_pem, public_key_pem
    
    @staticmethod
    def hash_data(data):
        """
        Create a SHA-256 hash of the provided data.
        
        Args:
            data (dict): Data to hash
            
        Returns:
            str: Hexadecimal hash string
        """
        # Convert data to a stable JSON string (sorted keys for deterministic output)
        data_json = json.dumps(data, sort_keys=True)
        
        # Create SHA-256 hash
        hash_object = hashlib.sha256(data_json.encode())
        return hash_object.hexdigest()
    
    @staticmethod
    def sign_data(data, private_key_pem):
        """
        Create a digital signature for the provided data.
        
        Args:
            data (dict): Data to sign
            private_key_pem (str): PEM-encoded private key
            
        Returns:
            str: Base64-encoded signature
        """
        # Hash the data first
        data_hash = DigitalSignatureService.hash_data(data)
        
        # Load the private key
        private_key = load_pem_private_key(
            private_key_pem.encode(),
            password=None
        )
        
        # Create signature
        signature = private_key.sign(
            data_hash.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Return base64 encoded signature
        return base64.b64encode(signature).decode('utf-8')
    
    @staticmethod
    def verify_signature(data, signature, public_key_pem):
        """
        Verify a digital signature for the provided data.
        
        Args:
            data (dict): Data that was signed
            signature (str): Base64-encoded signature
            public_key_pem (str): PEM-encoded public key
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            # Hash the data
            data_hash = DigitalSignatureService.hash_data(data)
            
            # Load the public key
            public_key = load_pem_public_key(public_key_pem.encode())
            
            # Decode the signature from base64
            signature_bytes = base64.b64decode(signature)
            
            # Verify the signature
            public_key.verify(
                signature_bytes,
                data_hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # If we get here, verification succeeded
            return True
            
        except InvalidSignature:
            # Signature verification failed
            logger.warning("Invalid signature detected")
            return False
        except Exception as e:
            # Other verification error
            logger.error(f"Error verifying signature: {str(e)}")
            return False
    
    @staticmethod
    def prepare_credential_for_blockchain(credential):
        """
        Prepare a credential for blockchain storage by creating a 
        standardized data structure with signature.
        
        Args:
            credential (Credential): Credential to prepare
            
        Returns:
            dict: Blockchain-ready credential data with signature
        """
        # Extract relevant credential data
        credential_data = {
            'id': str(credential.id),
            'user_id': str(credential.user.id),
            'title': credential.title,
            'issuer': credential.issuer,
            'type': credential.type,
            'issue_date': credential.issue_date.isoformat() if credential.issue_date else None,
            'expiry_date': credential.expiry_date.isoformat() if credential.expiry_date else None,
            'verified': credential.verified,
            'verified_at': credential.verified_at.isoformat() if credential.verified_at else None,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Create data hash for blockchain
        data_hash = DigitalSignatureService.hash_data(credential_data)
        
        # Currently, we're not actually signing with a private key yet - this would 
        # be implemented when we have the actual blockchain integration
        # For now, we'll return the hash and structured data
        
        blockchain_data = {
            'credential_id': str(credential.id),
            'data_hash': data_hash,
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'credential',
            'status': 'verified' if credential.verified else 'unverified'
        }
        
        return blockchain_data
    
    @staticmethod
    def prepare_experience_for_blockchain(experience):
        """
        Prepare an experience for blockchain storage by creating a 
        standardized data structure with signature.
        
        Args:
            experience (Experience): Experience to prepare
            
        Returns:
            dict: Blockchain-ready experience data with signature
        """
        # Extract relevant experience data
        experience_data = {
            'id': str(experience.id),
            'user_id': str(experience.user.id),
            'title': experience.title,
            'organization': experience.organization,
            'type': experience.type,
            'start_date': experience.start_date.isoformat() if experience.start_date else None,
            'end_date': experience.end_date.isoformat() if experience.end_date else None,
            'is_verified': experience.is_verified,
            'verified_at': experience.verified_at.isoformat() if experience.verified_at else None,
            'verified_by': str(experience.verified_by.id) if experience.verified_by else None,
            'linked_credentials': [str(cred.id) for cred in experience.credentials] if experience.credentials else [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Create data hash for blockchain
        data_hash = DigitalSignatureService.hash_data(experience_data)
        
        # Currently, we're not actually signing with a private key yet - this would 
        # be implemented when we have the actual blockchain integration
        # For now, we'll return the hash and structured data
        
        blockchain_data = {
            'experience_id': str(experience.id),
            'data_hash': data_hash,
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'experience',
            'status': 'verified' if experience.is_verified else 'unverified'
        }
        
        return blockchain_data
    
    @staticmethod
    def update_credential_blockchain_data(credential, blockchain_data=None):
        """
        Update a credential with blockchain data.
        
        Args:
            credential (Credential): Credential to update
            blockchain_data (dict, optional): Existing blockchain data or None
            
        Returns:
            Credential: Updated credential
        """
        if blockchain_data is None:
            blockchain_data = DigitalSignatureService.prepare_credential_for_blockchain(credential)
        
        # Update the credential with the blockchain data
        credential.blockchain_hash = blockchain_data.get('data_hash')
        
        # Additional blockchain metadata
        if not hasattr(credential, 'blockchain_data') or not credential.blockchain_data:
            credential.blockchain_data = {}
        
        credential.blockchain_data.update({
            'hash': blockchain_data.get('data_hash'),
            'timestamp': blockchain_data.get('timestamp'),
            'status': blockchain_data.get('status')
        })
        
        credential.save()
        return credential
    
    @staticmethod
    def update_experience_blockchain_data(experience, blockchain_data=None):
        """
        Update an experience with blockchain data.
        
        Args:
            experience (Experience): Experience to update
            blockchain_data (dict, optional): Existing blockchain data or None
            
        Returns:
            Experience: Updated experience
        """
        if blockchain_data is None:
            blockchain_data = DigitalSignatureService.prepare_experience_for_blockchain(experience)
        
        # Update the experience with the blockchain data
        if not hasattr(experience, 'metadata') or not experience.metadata:
            experience.metadata = {}
        
        # Add blockchain data to metadata
        experience.metadata['blockchain'] = {
            'hash': blockchain_data.get('data_hash'),
            'timestamp': blockchain_data.get('timestamp'),
            'status': blockchain_data.get('status')
        }
        
        experience.save()
        return experience
