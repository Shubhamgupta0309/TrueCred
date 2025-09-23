"""
Verification service for the TrueCred application.

This service provides comprehensive verification of credentials and experiences
using both traditional verification and blockchain-based verification.
"""
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from mongoengine.errors import DoesNotExist, ValidationError
from models.experience import Experience
from models.credential import Credential
from models.user import User
from services.notification_service import send_notification
from services.blockchain_service import BlockchainService
from services.ipfs_service import IPFSService

# Set up logging
logger = logging.getLogger(__name__)

class VerificationService:
    """
    Service for managing verification of experiences and credentials.
    
    This service provides:
    - Traditional manual verification by authorities
    - Blockchain-based verification of credential and experience hashes
    - IPFS verification of stored documents
    - Comprehensive verification status tracking
    """
    
    def __init__(self):
        """Initialize the verification service."""
        # Temporarily disable blockchain service to avoid connection issues
        self.blockchain_service = BlockchainService()
        self.blockchain_service = None
        self.ipfs_service = IPFSService()
    
    @staticmethod
    def request_experience_verification(experience_id, user_id, verification_data=None):
        """
        Request verification for an experience.
        
        Args:
            experience_id: ID of the experience to verify
            user_id: ID of the user requesting verification
            verification_data: Optional data about the verification
            
        Returns:
            Updated experience object
            
        Raises:
            DoesNotExist: If experience or user not found
            ValidationError: If experience already verified or pending verification
            ValueError: If user does not own the experience
        """
        try:
            experience = Experience.objects.get(id=experience_id)
            user = User.objects.get(id=user_id)
            
            # Ensure user owns the experience
            if str(experience.user.id) != str(user_id):
                raise ValueError("User does not own this experience")
            
            # Check if already verified
            if experience.is_verified:
                raise ValidationError("Experience is already verified")
            
            # Check if verification already pending
            if experience.pending_verification:
                raise ValidationError("Verification is already pending for this experience")
            
            # Request verification
            experience.request_verification(verification_data)
            
            # Notify organization for verification
            # This would typically send an email or notification to the organization
            # We'll just add this as a placeholder for now
            organization_name = experience.organization
            # send_notification(
            #    to=organization_name,
            #    subject="Experience Verification Request",
            #    message=f"User {user.name} has requested verification of their experience as {experience.title}"
            # )
            
            return experience
            
        except DoesNotExist as e:
            raise DoesNotExist(f"Experience or user not found: {str(e)}")
        except ValidationError as e:
            raise ValidationError(f"Validation error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error requesting verification: {str(e)}")
    
    @classmethod
    def verify_experience(cls, experience_id, verifier_id=None, verification_data=None):
        """
        Verify an experience using both manual verification and blockchain/IPFS verification.
        
        Args:
            experience_id: ID of the experience to verify
            verifier_id: ID of the user verifying the experience (optional)
            verification_data: Optional data about the verification
            
        Returns:
            Dict containing verification results
            
        Raises:
            DoesNotExist: If experience or verifier not found
            ValidationError: If validation fails
            ValueError: If verifier does not have permission
        """
        try:
            experience = Experience.objects.get(id=experience_id)
            
            # Initialize verification result
            verification_result = {
                'experience_id': str(experience.id),
                'title': experience.title,
                'organization': experience.organization,
                'verification_methods': [],
                'verified': False,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # If verifier_id is provided, verify manually
            if verifier_id:
                verifier = User.objects.get(id=verifier_id)
                
                # Check verifier permissions
                if 'verifier' not in verifier.roles and 'admin' not in verifier.roles:
                    raise ValueError("User does not have permission to verify experiences")
                
                # Perform manual verification
                experience.verify(verifier, verification_data)
                verification_result['verification_methods'].append('manual')
                verification_result['manual_verification'] = {
                    'verified': True,
                    'verifier': verifier.email,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Initialize blockchain verification service
            # blockchain_service = BlockchainService()
            ipfs_service = IPFSService()
            
            # Perform blockchain verification if hash exists
            blockchain_verification = {'verified': False, 'status': 'not_on_blockchain'}
            if hasattr(experience, 'blockchain_hash') and experience.blockchain_hash:
                # Convert ID to bytes32
                experience_id_bytes32 = cls._string_to_bytes32(str(experience.id))
                
                # Verify on blockchain
                blockchain_verification['verified'] = blockchain_service.verify_experience_hash(
                    experience_id_bytes32, 
                    experience.blockchain_hash
                )
                
                blockchain_verification['status'] = 'verified' if blockchain_verification['verified'] else 'hash_mismatch'
                blockchain_verification['timestamp'] = datetime.utcnow().isoformat()
                verification_result['verification_methods'].append('blockchain')
            
            verification_result['blockchain_verification'] = blockchain_verification
            
            # Perform IPFS verification if hash exists
            ipfs_verification = {'verified': False, 'status': 'not_on_ipfs'}
            if hasattr(experience, 'ipfs_hash') and experience.ipfs_hash:
                # Verify document exists on IPFS
                ipfs_data = ipfs_service.get_file(experience.ipfs_hash)
                
                if ipfs_data:
                    ipfs_verification['verified'] = True
                    ipfs_verification['status'] = 'verified'
                    ipfs_verification['gateway_url'] = ipfs_service.get_gateway_url(experience.ipfs_hash)
                    
                    # Check metadata if available
                    if hasattr(experience, 'ipfs_metadata_hash') and experience.ipfs_metadata_hash:
                        try:
                            metadata = ipfs_service.get_json(experience.ipfs_metadata_hash)
                            ipfs_verification['metadata'] = metadata
                        except Exception as e:
                            logger.warning(f"Error retrieving IPFS metadata: {str(e)}")
                    
                    verification_result['verification_methods'].append('ipfs')
            
            verification_result['ipfs_verification'] = ipfs_verification
            
            # Overall verification status - verified if any method succeeded
            verification_result['verified'] = (
                ('manual_verification' in verification_result and verification_result['manual_verification']['verified']) or
                blockchain_verification['verified'] or
                ipfs_verification['verified']
            )
            
            # Update experience verification status
            if verification_result['verified']:
                experience.is_verified = True
                experience.verified_at = datetime.utcnow()
                experience.verification_status = 'verified'
                experience.verification_data = verification_result
                experience.save()
            
            return verification_result
            
        except DoesNotExist as e:
            logger.error(f"Experience or verifier not found: {str(e)}")
            return {
                'verified': False,
                'status': 'not_found',
                'message': f"Experience or verifier not found: {str(e)}",
                'timestamp': datetime.utcnow().isoformat()
            }
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return {
                'verified': False,
                'status': 'validation_error',
                'message': f"Validation error: {str(e)}",
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error verifying experience: {str(e)}")
            return {
                'verified': False,
                'status': 'error',
                'message': f"Error verifying experience: {str(e)}",
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def reject_experience_verification(experience_id, verifier_id, reason, verification_data=None):
        """
        Reject verification for an experience.
        
        Args:
            experience_id: ID of the experience to reject
            verifier_id: ID of the user rejecting the verification
            reason: Reason for rejection
            verification_data: Optional data about the verification attempt
            
        Returns:
            Updated experience object
            
        Raises:
            DoesNotExist: If experience or verifier not found
            ValidationError: If experience already verified or not pending verification
            ValueError: If verifier does not have permission
        """
        try:
            experience = Experience.objects.get(id=experience_id)
            verifier = User.objects.get(id=verifier_id)
            
            # Check verifier permissions
            if 'verifier' not in verifier.roles and 'admin' not in verifier.roles:
                raise ValueError("User does not have permission to reject experience verifications")
            
            # Check if verification is pending
            if not experience.pending_verification:
                raise ValidationError("Experience is not pending verification")
            
            # Reject the verification
            experience.reject_verification(verifier, reason, verification_data)
            
            # Notify the user that their experience verification was rejected
            # send_notification(
            #    to=experience.user.email,
            #    subject="Experience Verification Rejected",
            #    message=f"Your experience verification for {experience.title} at {experience.organization} has been rejected: {reason}"
            # )
            
            return experience
            
        except DoesNotExist as e:
            raise DoesNotExist(f"Experience or verifier not found: {str(e)}")
        except ValidationError as e:
            raise ValidationError(f"Validation error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error rejecting experience verification: {str(e)}")
    
    @staticmethod
    def request_credential_verification(credential_id, user_id, verification_data=None):
        """
        Request verification for a credential.
        
        Args:
            credential_id: ID of the credential to verify
            user_id: ID of the user requesting verification
            verification_data: Optional data about the verification
            
        Returns:
            Updated credential object
            
        Raises:
            DoesNotExist: If credential or user not found
            ValidationError: If credential already verified or pending verification
            ValueError: If user does not own the credential
        """
        try:
            credential = Credential.objects.get(id=credential_id)
            user = User.objects.get(id=user_id)
            
            # Ensure user owns the credential
            if str(credential.user.id) != str(user_id):
                raise ValueError("User does not own this credential")
            
            # Check if already verified
            if credential.verified:
                raise ValidationError("Credential is already verified")
            
            # Check if verification already pending
            if getattr(credential, 'pending_verification', False):
                raise ValidationError("Verification is already pending for this credential")
            
            # Request verification
            credential.request_verification(verification_data)
            
            # Notify issuer for verification
            # This would typically send an email or notification to the issuer
            # We'll just add this as a placeholder for now
            issuer_name = credential.issuer
            # send_notification(
            #    to=issuer_name,
            #    subject="Credential Verification Request",
            #    message=f"User {user.name} has requested verification of their credential {credential.title}"
            # )
            
            return credential
            
        except DoesNotExist as e:
            raise DoesNotExist(f"Credential or user not found: {str(e)}")
        except ValidationError as e:
            raise ValidationError(f"Validation error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error requesting verification: {str(e)}")
    
    @classmethod
    def verify_credential(cls, credential_id, verifier_id=None, verification_data=None):
        """
        Verify a credential using both manual verification and blockchain/IPFS verification.
        
        Args:
            credential_id: ID of the credential to verify
            verifier_id: ID of the user verifying the credential (optional)
            verification_data: Optional data about the verification
            
        Returns:
            Dict containing verification results
            
        Raises:
            DoesNotExist: If credential or verifier not found
            ValidationError: If validation fails
            ValueError: If verifier does not have permission
        """
        try:
            credential = Credential.objects.get(id=credential_id)
            
            # Initialize verification result
            verification_result = {
                'credential_id': str(credential.id),
                'title': credential.title,
                'issuer': credential.issuer,
                'verification_methods': [],
                'verified': False,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # If verifier_id is provided, verify manually
            if verifier_id:
                verifier = User.objects.get(id=verifier_id)
                
                # Check verifier permissions
                if 'verifier' not in verifier.roles and 'admin' not in verifier.roles:
                    raise ValueError("User does not have permission to verify credentials")
                
                # Perform manual verification
                credential.verify(verifier, verification_data)
                verification_result['verification_methods'].append('manual')
                verification_result['manual_verification'] = {
                    'verified': True,
                    'verifier': verifier.email,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Initialize blockchain verification service
            # blockchain_service = BlockchainService()
            ipfs_service = IPFSService()
            
            # Perform blockchain verification if hash exists
            blockchain_verification = {'verified': False, 'status': 'not_on_blockchain'}
            if hasattr(credential, 'blockchain_hash') and credential.blockchain_hash:
                # Convert ID to bytes32
                credential_id_bytes32 = cls._string_to_bytes32(str(credential.id))
                
                # Verify on blockchain
                blockchain_verification['verified'] = blockchain_service.verify_credential_hash(
                    credential_id_bytes32, 
                    credential.blockchain_hash
                )
                
                blockchain_verification['status'] = 'verified' if blockchain_verification['verified'] else 'hash_mismatch'
                blockchain_verification['timestamp'] = datetime.utcnow().isoformat()
                verification_result['verification_methods'].append('blockchain')
            
            verification_result['blockchain_verification'] = blockchain_verification
            
            # Perform IPFS verification if hash exists
            ipfs_verification = {'verified': False, 'status': 'not_on_ipfs'}
            if hasattr(credential, 'ipfs_hash') and credential.ipfs_hash:
                # Verify document exists on IPFS
                ipfs_data = ipfs_service.get_file(credential.ipfs_hash)
                
                if ipfs_data:
                    ipfs_verification['verified'] = True
                    ipfs_verification['status'] = 'verified'
                    ipfs_verification['gateway_url'] = ipfs_service.get_gateway_url(credential.ipfs_hash)
                    
                    # Check metadata if available
                    if hasattr(credential, 'ipfs_metadata_hash') and credential.ipfs_metadata_hash:
                        try:
                            metadata = ipfs_service.get_json(credential.ipfs_metadata_hash)
                            ipfs_verification['metadata'] = metadata
                        except Exception as e:
                            logger.warning(f"Error retrieving IPFS metadata: {str(e)}")
                    
                    verification_result['verification_methods'].append('ipfs')
            
            verification_result['ipfs_verification'] = ipfs_verification
            
            # Overall verification status - verified if any method succeeded
            verification_result['verified'] = (
                ('manual_verification' in verification_result and verification_result['manual_verification']['verified']) or
                blockchain_verification['verified'] or
                ipfs_verification['verified']
            )
            
            # Update credential verification status
            if verification_result['verified']:
                credential.verified = True
                credential.verified_at = datetime.utcnow()
                credential.verification_status = 'verified'
                credential.verification_data = verification_result
                credential.save()
            
            return verification_result
            
        except DoesNotExist as e:
            logger.error(f"Credential or verifier not found: {str(e)}")
            return {
                'verified': False,
                'status': 'not_found',
                'message': f"Credential or verifier not found: {str(e)}",
                'timestamp': datetime.utcnow().isoformat()
            }
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return {
                'verified': False,
                'status': 'validation_error',
                'message': f"Validation error: {str(e)}",
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error verifying credential: {str(e)}")
            return {
                'verified': False,
                'status': 'error',
                'message': f"Error verifying credential: {str(e)}",
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def reject_credential_verification(credential_id, verifier_id, reason, verification_data=None):
        """
        Reject verification for a credential.
        
        Args:
            credential_id: ID of the credential to reject
            verifier_id: ID of the user rejecting the verification
            reason: Reason for rejection
            verification_data: Optional data about the verification attempt
            
        Returns:
            Updated credential object
            
        Raises:
            DoesNotExist: If credential or verifier not found
            ValidationError: If credential already verified or not pending verification
            ValueError: If verifier does not have permission
        """
        try:
            credential = Credential.objects.get(id=credential_id)
            verifier = User.objects.get(id=verifier_id)
            
            # Check verifier permissions
            if 'verifier' not in verifier.roles and 'admin' not in verifier.roles:
                raise ValueError("User does not have permission to reject credential verifications")
            
            # Check if verification is pending
            if not getattr(credential, 'pending_verification', False):
                raise ValidationError("Credential is not pending verification")
            
            # Reject the verification
            credential.reject_verification(verifier, reason, verification_data)
            
            # Notify the user that their credential verification was rejected
            # send_notification(
            #    to=credential.user.email,
            #    subject="Credential Verification Rejected",
            #    message=f"Your credential verification for {credential.title} from {credential.issuer} has been rejected: {reason}"
            # )
            
            return credential
            
        except DoesNotExist as e:
            raise DoesNotExist(f"Credential or verifier not found: {str(e)}")
        except ValidationError as e:
            raise ValidationError(f"Validation error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error rejecting credential verification: {str(e)}")
    
    @staticmethod
    def link_credential_to_experience(credential_id, experience_id, user_id):
        """
        Link a credential to an experience.
        
        Args:
            credential_id: ID of the credential to link
            experience_id: ID of the experience to link to
            user_id: ID of the user making the request
            
        Returns:
            Updated credential object
            
        Raises:
            DoesNotExist: If credential, experience, or user not found
            ValueError: If user does not own both the credential and experience
        """
        try:
            credential = Credential.objects.get(id=credential_id)
            experience = Experience.objects.get(id=experience_id)
            user = User.objects.get(id=user_id)
            
            # Ensure user owns both the credential and experience
            if str(credential.user.id) != str(user_id) or str(experience.user.id) != str(user_id):
                raise ValueError("User must own both the credential and experience")
            
            # Link the credential to the experience
            credential.link_to_experience(experience)
            
            return credential
            
        except DoesNotExist as e:
            raise DoesNotExist(f"Credential, experience, or user not found: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error linking credential to experience: {str(e)}")
    
    @staticmethod
    def unlink_credential_from_experience(credential_id, experience_id, user_id):
        """
        Unlink a credential from an experience.
        
        Args:
            credential_id: ID of the credential to unlink
            experience_id: ID of the experience to unlink from
            user_id: ID of the user making the request
            
        Returns:
            Updated credential object
            
        Raises:
            DoesNotExist: If credential, experience, or user not found
            ValueError: If user does not own both the credential and experience
        """
        try:
            credential = Credential.objects.get(id=credential_id)
            experience = Experience.objects.get(id=experience_id)
            user = User.objects.get(id=user_id)
            
            # Ensure user owns both the credential and experience
            if str(credential.user.id) != str(user_id) or str(experience.user.id) != str(user_id):
                raise ValueError("User must own both the credential and experience")
            
            # Unlink the credential from the experience
            credential.unlink_from_experience(experience)
            
            return credential
            
        except DoesNotExist as e:
            raise DoesNotExist(f"Credential, experience, or user not found: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error unlinking credential from experience: {str(e)}")
    
    @staticmethod
    def get_pending_verifications(user_id=None, verification_type=None):
        """
        Get a list of pending verifications.
        
        Args:
            user_id: Optional ID of the user to filter by
            verification_type: Optional type of verification ('experience' or 'credential')
            
        Returns:
            List of pending verifications
        """
        results = {
            'experiences': [],
            'credentials': []
        }
        
        # Get pending experience verifications
        if verification_type is None or verification_type == 'experience':
            exp_query = {'pending_verification': True}
            if user_id:
                exp_query['user'] = user_id
            
            experiences = Experience.objects.filter(**exp_query)
            results['experiences'] = [exp.to_json() for exp in experiences]
        
        # Get pending credential verifications
        if verification_type is None or verification_type == 'credential':
            cred_query = {'pending_verification': True}
            if user_id:
                cred_query['user'] = user_id
            
            credentials = Credential.objects.filter(**cred_query)
            results['credentials'] = [cred.to_json() for cred in credentials]
        
        return results
        
    @classmethod
    def batch_verify_credentials(cls, credential_ids, verifier_id=None):
        """
        Verify multiple credentials in a batch.
        
        Args:
            credential_ids: List of credential IDs to verify
            verifier_id: ID of the user performing verification (optional)
            
        Returns:
            Dict containing results for each credential
        """
        results = {}
        for credential_id in credential_ids:
            try:
                result = cls.verify_credential(credential_id, verifier_id)
                results[credential_id] = result
            except Exception as e:
                results[credential_id] = {
                    'verified': False,
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        # Compile summary statistics
        verified_count = sum(1 for result in results.values() if result.get('verified', False))
        
        return {
            'results': results,
            'summary': {
                'total': len(credential_ids),
                'verified': verified_count,
                'failed': len(credential_ids) - verified_count,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    
    @classmethod
    def batch_verify_experiences(cls, experience_ids, verifier_id=None):
        """
        Verify multiple experiences in a batch.
        
        Args:
            experience_ids: List of experience IDs to verify
            verifier_id: ID of the user performing verification (optional)
            
        Returns:
            Dict containing results for each experience
        """
        results = {}
        for experience_id in experience_ids:
            try:
                result = cls.verify_experience(experience_id, verifier_id)
                results[experience_id] = result
            except Exception as e:
                results[experience_id] = {
                    'verified': False,
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        # Compile summary statistics
        verified_count = sum(1 for result in results.values() if result.get('verified', False))
        
        return {
            'results': results,
            'summary': {
                'total': len(experience_ids),
                'verified': verified_count,
                'failed': len(experience_ids) - verified_count,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    
    @classmethod
    def verify_user_profile(cls, user_id):
        """
        Verify all credentials and experiences for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dict containing verification results for the user's profile
        """
        try:
            user = User.objects.get(id=user_id)
            
            # Get user's credentials and experiences
            credentials = Credential.objects.filter(user=user)
            experiences = Experience.objects.filter(user=user)
            
            credential_ids = [str(c.id) for c in credentials]
            experience_ids = [str(e.id) for e in experiences]
            
            # Verify all credentials and experiences
            credential_results = cls.batch_verify_credentials(credential_ids)
            experience_results = cls.batch_verify_experiences(experience_ids)
            
            # Calculate overall verification score
            cred_verified = credential_results['summary']['verified']
            cred_total = credential_results['summary']['total']
            exp_verified = experience_results['summary']['verified']
            exp_total = experience_results['summary']['total']
            
            verification_score = cls._calculate_verification_score(
                cred_verified, cred_total, 
                exp_verified, exp_total
            )
            
            return {
                'user_id': str(user.id),
                'username': user.username,
                'email': user.email,
                'credential_verifications': credential_results,
                'experience_verifications': experience_results,
                'summary': {
                    'total_credentials': cred_total,
                    'verified_credentials': cred_verified,
                    'total_experiences': exp_total,
                    'verified_experiences': exp_verified,
                    'verification_score': verification_score,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
        except DoesNotExist:
            return {
                'error': f"User not found: {user_id}",
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'error': f"Error verifying user profile: {str(e)}",
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def _calculate_verification_score(verified_credentials, total_credentials, verified_experiences, total_experiences):
        """
        Calculate a verification score for a user's profile.
        
        Args:
            verified_credentials: Number of verified credentials
            total_credentials: Total number of credentials
            verified_experiences: Number of verified experiences
            total_experiences: Total number of experiences
            
        Returns:
            float: Verification score (0-100)
        """
        # If no credentials or experiences, score is 0
        if total_credentials == 0 and total_experiences == 0:
            return 0.0
        
        # Calculate individual scores
        credential_score = (verified_credentials / total_credentials * 100) if total_credentials > 0 else 0
        experience_score = (verified_experiences / total_experiences * 100) if total_experiences > 0 else 0
        
        # Weight credentials more heavily than experiences
        if total_credentials > 0 and total_experiences > 0:
            return round((credential_score * 0.6) + (experience_score * 0.4), 2)
        elif total_credentials > 0:
            return round(credential_score, 2)
        else:
            return round(experience_score, 2)
    
    @staticmethod
    def _string_to_bytes32(value):
        """
        Convert a string to bytes32 format for Ethereum.
        
        Args:
            value: String to convert
            
        Returns:
            str: bytes32 representation
        """
        # If value is already bytes32 (0x followed by 64 hex chars), return as is
        if isinstance(value, str) and value.startswith('0x') and len(value) == 66:
            return value
            
        # Otherwise, hash the value to get a bytes32
        return '0x' + hashlib.sha256(value.encode('utf-8')).hexdigest()
