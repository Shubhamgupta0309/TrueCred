"""
Credential service for the TrueCred application.

This service provides functions for credential management, validation,
and verification.
"""
from models.credential import Credential
from models.user import User
from datetime import datetime
import logging
from bson import ObjectId
from mongoengine.errors import ValidationError, DoesNotExist, NotUniqueError
from mongoengine.queryset import Q

# Set up logging
logger = logging.getLogger(__name__)

class CredentialService:
    """
    Service class for credential-related operations.
    """
    
    @staticmethod
    def get_user_credentials(user_id, include_expired=False, status=None, credential_type=None):
        """
        Get credentials for a specific user.
        
        Args:
            user_id: User ID
            include_expired: Whether to include expired credentials
            status: Filter by verification status (verified, unverified, all)
            credential_type: Filter by credential type
            
        Returns:
            List of credentials for the user
        """
        try:
            # Build query using mongoengine Q objects to avoid raw $ operators
            # Normalize user_id to string
            if isinstance(user_id, dict):
                user_id = str(user_id.get('user_id') or user_id.get('id') or user_id.get('_id') or '')
            else:
                user_id = str(user_id) if user_id is not None else None

            # Resolve user_id into a User document when possible so ReferenceField matching works
            user_obj = None
            if user_id:
                try:
                    # First try by ObjectId / id
                    user_obj = User.objects(id=user_id).first()
                except Exception:
                    user_obj = None

                # If not found, try by username or email
                if not user_obj:
                    try:
                        user_obj = User.objects(username=user_id).first() or User.objects(email=user_id).first()
                    except Exception:
                        user_obj = None

            # Start with user filter. If we resolved a User doc, filter by that object; otherwise
            # fall back to using the string id (mongoengine will attempt to cast where possible).
            query_filter = Q(user=user_obj if user_obj else user_id)

            # Expiry filter: either no expiry_date or expiry_date in the future
            if not include_expired:
                current_time = datetime.utcnow()
                query_filter &= (Q(expiry_date=None) | Q(expiry_date__gt=current_time))

            # Verification status
            if status == 'verified':
                query_filter &= Q(verified=True)
            elif status == 'unverified':
                query_filter &= Q(verified=False)

            # Credential type
            if credential_type:
                query_filter &= Q(type=credential_type)

            # Fetch credentials using the composed Q filter
            credentials = Credential.objects(query_filter).order_by('-created_at')
            
            logger.info(f"Retrieved {credentials.count()} credentials for user {user_id}")
            return credentials, None
            
        except Exception as e:
            logger.error(f"Error retrieving credentials for user {user_id}: {e}")
            return [], f"Error retrieving credentials: {str(e)}"
    
    @staticmethod
    def get_credential_by_id(credential_id, user_id=None):
        """
        Get a specific credential by ID.
        
        Args:
            credential_id: Credential ID
            user_id: Optional user ID to validate ownership
            
        Returns:
            (credential, error): (Credential object, None) if successful, (None, error_message) otherwise
        """
        try:
            # Try to convert string ID to ObjectId
            try:
                if not ObjectId.is_valid(credential_id):
                    return None, "Invalid credential ID format"
            except:
                return None, "Invalid credential ID format"
            
            # Fetch credential
            credential = Credential.objects(id=credential_id).first()
            
            if not credential:
                return None, "Credential not found"
            
            # Check if user has access
            if user_id and str(credential.user.id) != user_id:
                logger.warning(f"User {user_id} attempted to access credential {credential_id} owned by {credential.user.id}")
                return None, "Access denied"
            
            return credential, None
            
        except Exception as e:
            logger.error(f"Error retrieving credential {credential_id}: {e}")
            return None, f"Error retrieving credential: {str(e)}"
    
    @staticmethod
    def create_credential(user_id, data):
        """
        Create a new credential.
        
        Args:
            user_id: User ID of the credential owner
            data: Credential data
            
        Returns:
            (credential, error): (Credential object, None) if successful, (None, error_message) otherwise
        """
        try:
            # Validate user ID
            try:
                user = User.objects(id=user_id).first()
                if not user:
                    return None, "User not found"
            except Exception as e:
                return None, f"Invalid user ID: {str(e)}"
            
            # Validate required fields
            required_fields = ['title', 'issuer', 'type']
            for field in required_fields:
                if field not in data or not data[field]:
                    return None, f"Missing required field: {field}"
            
            # Process dates
            issue_date = None
            if 'issue_date' in data and data['issue_date']:
                try:
                    issue_date = datetime.fromisoformat(data['issue_date'].replace('Z', '+00:00'))
                except ValueError:
                    return None, "Invalid issue date format"
            
            expiry_date = None
            if 'expiry_date' in data and data['expiry_date']:
                try:
                    expiry_date = datetime.fromisoformat(data['expiry_date'].replace('Z', '+00:00'))
                except ValueError:
                    return None, "Invalid expiry date format"
            
            # Create new credential
            credential = Credential(
                user=user,
                title=data.get('title'),
                issuer=data.get('issuer'),
                description=data.get('description', ''),
                type=data.get('type'),
                issue_date=issue_date or datetime.utcnow(),
                expiry_date=expiry_date,
                document_url=data.get('document_url'),
                metadata=data.get('metadata', {})
            )
            
            # Save credential
            credential.save()
            
            logger.info(f"Created new credential {credential.id} for user {user_id}")
            return credential, None
            
        except ValidationError as e:
            logger.error(f"Validation error creating credential: {e}")
            return None, f"Validation error: {str(e)}"
            
        except NotUniqueError as e:
            logger.error(f"Not unique error creating credential: {e}")
            return None, "A credential with these details already exists"
            
        except Exception as e:
            logger.error(f"Error creating credential: {e}")
            return None, f"Error creating credential: {str(e)}"
    
    @staticmethod
    def update_credential(credential_id, user_id, data):
        """
        Update an existing credential.
        
        Args:
            credential_id: Credential ID
            user_id: User ID of the credential owner
            data: Updated credential data
            
        Returns:
            (credential, error): (Credential object, None) if successful, (None, error_message) otherwise
        """
        try:
            # Get credential
            credential, error = CredentialService.get_credential_by_id(credential_id, user_id)
            
            if error:
                return None, error
            
            # Check if credential is already verified
            if credential.verified:
                return None, "Cannot update a verified credential"
            
            # Update fields
            updatable_fields = [
                'title', 'issuer', 'description', 'type', 
                'document_url', 'metadata'
            ]
            
            for field in updatable_fields:
                if field in data and data[field] is not None:
                    setattr(credential, field, data[field])
            
            # Process dates
            if 'issue_date' in data and data['issue_date']:
                try:
                    credential.issue_date = datetime.fromisoformat(data['issue_date'].replace('Z', '+00:00'))
                except ValueError:
                    return None, "Invalid issue date format"
            
            if 'expiry_date' in data and data['expiry_date']:
                try:
                    credential.expiry_date = datetime.fromisoformat(data['expiry_date'].replace('Z', '+00:00'))
                except ValueError:
                    return None, "Invalid expiry date format"
            elif 'expiry_date' in data and data['expiry_date'] is None:
                credential.expiry_date = None
            
            # Save credential
            credential.save()
            
            logger.info(f"Updated credential {credential_id} for user {user_id}")
            return credential, None
            
        except ValidationError as e:
            logger.error(f"Validation error updating credential: {e}")
            return None, f"Validation error: {str(e)}"
            
        except Exception as e:
            logger.error(f"Error updating credential: {e}")
            return None, f"Error updating credential: {str(e)}"
    
    @staticmethod
    def delete_credential(credential_id, user_id):
        """
        Delete a credential.
        
        Args:
            credential_id: Credential ID
            user_id: User ID of the credential owner
            
        Returns:
            (success, error): (True, None) if successful, (False, error_message) otherwise
        """
        try:
            # Get credential
            credential, error = CredentialService.get_credential_by_id(credential_id, user_id)
            
            if error:
                return False, error
            
            # Check if credential is verified
            if credential.verified:
                return False, "Cannot delete a verified credential"
            
            # Delete credential
            credential.delete()
            
            logger.info(f"Deleted credential {credential_id} for user {user_id}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error deleting credential: {e}")
            return False, f"Error deleting credential: {str(e)}"
    
    @staticmethod
    def verify_credential(credential_id, issuer_id, verification_data=None):
        """
        Verify a credential.
        
        Args:
            credential_id: Credential ID
            issuer_id: ID of the user verifying the credential (must be an issuer)
            verification_data: Optional verification data
            
        Returns:
            (credential, error): (Credential object, None) if successful, (None, error_message) otherwise
        """
        try:
            # Check if issuer exists and has issuer role
            issuer = User.objects(id=issuer_id).first()
            
            if not issuer:
                return None, "Issuer not found"
            
            if issuer.role != 'issuer' and issuer.role != 'admin':
                return None, "Only issuers can verify credentials"
            
            # Get credential
            credential, error = CredentialService.get_credential_by_id(credential_id)
            
            if error:
                return None, error
            
            # Check if issuer matches credential issuer
            if credential.issuer.lower() != issuer.username.lower() and issuer.role != 'admin':
                return None, "Only the original issuer can verify this credential"
            
            # Check if already verified
            if credential.verified:
                return credential, "Credential is already verified"
            
            # Add verification data
            if not verification_data:
                verification_data = {}
            
            verification_data['verified_by'] = str(issuer.id)
            verification_data['verified_at'] = datetime.utcnow().isoformat()
            
            # Verify credential
            credential.verify(verification_data)
            
            logger.info(f"Verified credential {credential_id} by issuer {issuer_id}")
            return credential, None
            
        except Exception as e:
            logger.error(f"Error verifying credential: {e}")
            return None, f"Error verifying credential: {str(e)}"
    
    @staticmethod
    def bulk_verify_credentials(credential_ids, issuer_id, verification_data=None):
        """
        Verify multiple credentials in bulk.
        
        Args:
            credential_ids: List of credential IDs
            issuer_id: ID of the user verifying the credentials (must be an issuer)
            verification_data: Optional verification data
            
        Returns:
            (results, errors): (Dict of results, Dict of errors) 
        """
        results = {}
        errors = {}
        
        for credential_id in credential_ids:
            credential, error = CredentialService.verify_credential(
                credential_id, issuer_id, verification_data
            )
            
            if error:
                errors[credential_id] = error
            else:
                results[credential_id] = "Verified successfully"
        
        return results, errors
