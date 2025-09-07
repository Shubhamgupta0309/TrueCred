"""
Verification service for the TrueCred application.
"""
from datetime import datetime
from mongoengine.errors import DoesNotExist, ValidationError
from models.experience import Experience
from models.credential import Credential
from models.user import User
from services.notification_service import send_notification

class VerificationService:
    """
    Service for managing verification of experiences and credentials.
    """
    
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
    
    @staticmethod
    def verify_experience(experience_id, verifier_id, verification_data=None):
        """
        Verify an experience.
        
        Args:
            experience_id: ID of the experience to verify
            verifier_id: ID of the user verifying the experience
            verification_data: Optional data about the verification
            
        Returns:
            Updated experience object
            
        Raises:
            DoesNotExist: If experience or verifier not found
            ValidationError: If experience already verified
            ValueError: If verifier does not have permission
        """
        try:
            experience = Experience.objects.get(id=experience_id)
            verifier = User.objects.get(id=verifier_id)
            
            # Check verifier permissions
            # In a real system, we would validate that the verifier represents the organization
            # For now, we'll just check if they have the 'verifier' role
            if 'verifier' not in verifier.roles and 'admin' not in verifier.roles:
                raise ValueError("User does not have permission to verify experiences")
            
            # Check if already verified
            if experience.is_verified and not experience.pending_verification:
                raise ValidationError("Experience is already verified")
            
            # Verify the experience
            experience.verify(verifier, verification_data)
            
            # Notify the user that their experience was verified
            # send_notification(
            #    to=experience.user.email,
            #    subject="Experience Verified",
            #    message=f"Your experience as {experience.title} at {experience.organization} has been verified"
            # )
            
            return experience
            
        except DoesNotExist as e:
            raise DoesNotExist(f"Experience or verifier not found: {str(e)}")
        except ValidationError as e:
            raise ValidationError(f"Validation error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error verifying experience: {str(e)}")
    
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
    
    @staticmethod
    def verify_credential(credential_id, verifier_id, verification_data=None):
        """
        Verify a credential.
        
        Args:
            credential_id: ID of the credential to verify
            verifier_id: ID of the user verifying the credential
            verification_data: Optional data about the verification
            
        Returns:
            Updated credential object
            
        Raises:
            DoesNotExist: If credential or verifier not found
            ValidationError: If credential already verified
            ValueError: If verifier does not have permission
        """
        try:
            credential = Credential.objects.get(id=credential_id)
            verifier = User.objects.get(id=verifier_id)
            
            # Check verifier permissions
            # In a real system, we would validate that the verifier represents the issuer
            # For now, we'll just check if they have the 'verifier' role
            if 'verifier' not in verifier.roles and 'admin' not in verifier.roles:
                raise ValueError("User does not have permission to verify credentials")
            
            # Check if already verified
            if credential.verified and not getattr(credential, 'pending_verification', False):
                raise ValidationError("Credential is already verified")
            
            # Verify the credential
            credential.verify(verifier, verification_data)
            
            # Notify the user that their credential was verified
            # send_notification(
            #    to=credential.user.email,
            #    subject="Credential Verified",
            #    message=f"Your credential {credential.title} from {credential.issuer} has been verified"
            # )
            
            return credential
            
        except DoesNotExist as e:
            raise DoesNotExist(f"Credential or verifier not found: {str(e)}")
        except ValidationError as e:
            raise ValidationError(f"Validation error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error verifying credential: {str(e)}")
    
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
