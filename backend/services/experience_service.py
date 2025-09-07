"""
Experience Service - Provides business logic for managing user experiences.
"""
from datetime import datetime
import logging
from mongoengine.errors import ValidationError, DoesNotExist
from models.experience import Experience
from models.credential import Credential
from models.user import User

logger = logging.getLogger(__name__)

class ExperienceService:
    """Service class for managing experiences"""
    
    @staticmethod
    def get_user_experiences(user_id, exp_type=None, current_only=False):
        """
        Get all experiences for a user.
        
        Args:
            user_id (str): User ID
            exp_type (str, optional): Filter by experience type (work, education)
            current_only (bool, optional): Filter by current status
            
        Returns:
            tuple: (list of experiences, error message)
        """
        try:
            # Get user
            user = User.objects.get(id=user_id)
            
            # Build query
            query = {'user': user}
            if exp_type:
                query['type'] = exp_type
            if current_only:
                query['is_current'] = True
                
            # Get experiences
            experiences = Experience.objects(**query).order_by('-start_date')
            return experiences, None
            
        except DoesNotExist:
            logger.error(f"User not found: {user_id}")
            return [], "User not found"
        except Exception as e:
            logger.error(f"Error getting experiences: {str(e)}")
            return [], f"Error retrieving experiences: {str(e)}"
    
    @staticmethod
    def create_experience(user_id, data):
        """
        Create a new experience.
        
        Args:
            user_id (str): User ID
            data (dict): Experience data
            
        Returns:
            tuple: (created experience, error message)
        """
        try:
            # Get user
            user = User.objects.get(id=user_id)
            
            # Parse dates
            start_date = datetime.fromisoformat(data.get('start_date')) if data.get('start_date') else None
            end_date = datetime.fromisoformat(data.get('end_date')) if data.get('end_date') else None
            
            # Create experience
            experience = Experience(
                user=user,
                type=data.get('type', 'work'),
                title=data.get('title'),
                organization=data.get('organization'),
                start_date=start_date,
                end_date=end_date,
                description=data.get('description'),
                location=data.get('location'),
                skills=data.get('skills', []),
                is_current=data.get('is_current', False),
                metadata=data.get('metadata', {})
            )
            
            # Save experience
            experience.save()
            
            # Link credentials if provided
            if 'related_credentials' in data and data['related_credentials']:
                ExperienceService.link_credentials(
                    experience_id=str(experience.id),
                    user_id=user_id,
                    credential_ids=data['related_credentials']
                )
                # Reload the experience to get the linked credentials
                experience.reload()
            
            return experience, None
            
        except ValidationError as e:
            logger.error(f"Validation error creating experience: {str(e)}")
            return None, f"Validation error: {str(e)}"
        except DoesNotExist:
            logger.error(f"User not found: {user_id}")
            return None, "User not found"
        except Exception as e:
            logger.error(f"Error creating experience: {str(e)}")
            return None, f"Error creating experience: {str(e)}"
    
    @staticmethod
    def get_experience_by_id(experience_id, user_id=None):
        """
        Get an experience by ID.
        
        Args:
            experience_id (str): Experience ID
            user_id (str, optional): User ID for permission check
            
        Returns:
            tuple: (experience, error message)
        """
        try:
            # Get experience
            experience = Experience.objects.get(id=experience_id)
            
            # Check permissions if user_id is provided
            if user_id and str(experience.user.id) != user_id:
                logger.warning(f"User {user_id} attempted to access experience {experience_id} belonging to {experience.user.id}")
                return None, "You do not have permission to access this experience"
            
            return experience, None
            
        except DoesNotExist:
            logger.error(f"Experience not found: {experience_id}")
            return None, "Experience not found"
        except Exception as e:
            logger.error(f"Error retrieving experience: {str(e)}")
            return None, f"Error retrieving experience: {str(e)}"
    
    @staticmethod
    def update_experience(experience_id, user_id, data):
        """
        Update an experience.
        
        Args:
            experience_id (str): Experience ID
            user_id (str): User ID
            data (dict): Updated experience data
            
        Returns:
            tuple: (updated experience, error message)
        """
        try:
            # Get experience
            experience = Experience.objects.get(id=experience_id)
            
            # Check permissions
            if str(experience.user.id) != user_id:
                logger.warning(f"User {user_id} attempted to update experience {experience_id} belonging to {experience.user.id}")
                return None, "You do not have permission to update this experience"
            
            # Update fields
            if 'type' in data:
                experience.type = data['type']
            if 'title' in data:
                experience.title = data['title']
            if 'organization' in data:
                experience.organization = data['organization']
            if 'start_date' in data:
                experience.start_date = datetime.fromisoformat(data['start_date']) if data['start_date'] else None
            if 'end_date' in data:
                experience.end_date = datetime.fromisoformat(data['end_date']) if data['end_date'] else None
            if 'description' in data:
                experience.description = data['description']
            if 'location' in data:
                experience.location = data['location']
            if 'skills' in data:
                experience.skills = data['skills']
            if 'is_current' in data:
                experience.is_current = data['is_current']
            if 'metadata' in data:
                experience.metadata = data['metadata']
            
            # Save experience
            experience.save()
            
            # Update related credentials if provided
            if 'related_credentials' in data:
                # Clear existing credentials and add new ones
                experience.credentials = []
                experience.save()
                
                if data['related_credentials']:
                    ExperienceService.link_credentials(
                        experience_id=experience_id,
                        user_id=user_id,
                        credential_ids=data['related_credentials']
                    )
                    # Reload the experience to get the updated credentials
                    experience.reload()
            
            return experience, None
            
        except ValidationError as e:
            logger.error(f"Validation error updating experience: {str(e)}")
            return None, f"Validation error: {str(e)}"
        except DoesNotExist:
            logger.error(f"Experience not found: {experience_id}")
            return None, "Experience not found"
        except Exception as e:
            logger.error(f"Error updating experience: {str(e)}")
            return None, f"Error updating experience: {str(e)}"
    
    @staticmethod
    def delete_experience(experience_id, user_id):
        """
        Delete an experience.
        
        Args:
            experience_id (str): Experience ID
            user_id (str): User ID
            
        Returns:
            tuple: (success, error message)
        """
        try:
            # Get experience
            experience = Experience.objects.get(id=experience_id)
            
            # Check permissions
            if str(experience.user.id) != user_id:
                logger.warning(f"User {user_id} attempted to delete experience {experience_id} belonging to {experience.user.id}")
                return False, "You do not have permission to delete this experience"
            
            # Delete experience
            experience.delete()
            return True, None
            
        except DoesNotExist:
            logger.error(f"Experience not found: {experience_id}")
            return False, "Experience not found"
        except Exception as e:
            logger.error(f"Error deleting experience: {str(e)}")
            return False, f"Error deleting experience: {str(e)}"
    
    @staticmethod
    def verify_experience(experience_id, verifier_id, verification_data=None):
        """
        Verify an experience.
        
        Args:
            experience_id (str): Experience ID
            verifier_id (str): Verifier user ID
            verification_data (dict, optional): Additional verification data
            
        Returns:
            tuple: (verified experience, error message)
        """
        try:
            # Get experience and verifier
            experience = Experience.objects.get(id=experience_id)
            verifier = User.objects.get(id=verifier_id)
            
            # Check if already verified
            if experience.verified:
                return experience, "Experience is already verified"
            
            # Verify experience
            verification_data = verification_data or {}
            experience.verify(verifier, verification_data)
            return experience, None
            
        except DoesNotExist as e:
            if "Experience" in str(e):
                logger.error(f"Experience not found: {experience_id}")
                return None, "Experience not found"
            else:
                logger.error(f"Verifier not found: {verifier_id}")
                return None, "Verifier not found"
        except Exception as e:
            logger.error(f"Error verifying experience: {str(e)}")
            return None, f"Error verifying experience: {str(e)}"
    
    @staticmethod
    def get_experience_credentials(experience_id, user_id):
        """
        Get credentials associated with an experience.
        
        Args:
            experience_id (str): Experience ID
            user_id (str): User ID
            
        Returns:
            tuple: (list of credentials, error message)
        """
        try:
            # Get experience
            experience = Experience.objects.get(id=experience_id)
            
            # Check permissions
            if str(experience.user.id) != user_id:
                logger.warning(f"User {user_id} attempted to access credentials for experience {experience_id} belonging to {experience.user.id}")
                return [], "You do not have permission to access this experience"
            
            # Get credentials
            return experience.credentials, None
            
        except DoesNotExist:
            logger.error(f"Experience not found: {experience_id}")
            return [], "Experience not found"
        except Exception as e:
            logger.error(f"Error retrieving experience credentials: {str(e)}")
            return [], f"Error retrieving experience credentials: {str(e)}"
    
    @staticmethod
    def link_credentials(experience_id, user_id, credential_ids):
        """
        Link credentials to an experience.
        
        Args:
            experience_id (str): Experience ID
            user_id (str): User ID
            credential_ids (list): List of credential IDs
            
        Returns:
            tuple: (updated experience, error message)
        """
        try:
            # Get experience
            experience = Experience.objects.get(id=experience_id)
            
            # Check permissions
            if str(experience.user.id) != user_id:
                logger.warning(f"User {user_id} attempted to link credentials to experience {experience_id} belonging to {experience.user.id}")
                return None, "You do not have permission to modify this experience"
            
            # Get credentials
            credentials = []
            for cred_id in credential_ids:
                try:
                    credential = Credential.objects.get(id=cred_id)
                    
                    # Check if credential belongs to the user
                    if str(credential.user.id) != user_id:
                        logger.warning(f"User {user_id} attempted to link credential {cred_id} belonging to {credential.user.id}")
                        continue
                    
                    credentials.append(credential)
                except DoesNotExist:
                    logger.warning(f"Credential not found: {cred_id}")
                    continue
            
            # Add credentials to experience (without duplicates)
            for credential in credentials:
                if credential not in experience.credentials:
                    experience.credentials.append(credential)
            
            # Save experience
            experience.save()
            return experience, None
            
        except DoesNotExist:
            logger.error(f"Experience not found: {experience_id}")
            return None, "Experience not found"
        except Exception as e:
            logger.error(f"Error linking credentials: {str(e)}")
            return None, f"Error linking credentials: {str(e)}"
    
    @staticmethod
    def unlink_credential(experience_id, user_id, credential_id):
        """
        Unlink a credential from an experience.
        
        Args:
            experience_id (str): Experience ID
            user_id (str): User ID
            credential_id (str): Credential ID
            
        Returns:
            tuple: (updated experience, error message)
        """
        try:
            # Get experience
            experience = Experience.objects.get(id=experience_id)
            
            # Check permissions
            if str(experience.user.id) != user_id:
                logger.warning(f"User {user_id} attempted to unlink credential from experience {experience_id} belonging to {experience.user.id}")
                return None, "You do not have permission to modify this experience"
            
            # Get credential
            credential = Credential.objects.get(id=credential_id)
            
            # Remove credential from experience
            if credential in experience.credentials:
                experience.credentials.remove(credential)
                experience.save()
            
            return experience, None
            
        except DoesNotExist as e:
            if "Experience" in str(e):
                logger.error(f"Experience not found: {experience_id}")
                return None, "Experience not found"
            else:
                logger.error(f"Credential not found: {credential_id}")
                return None, "Credential not found"
        except Exception as e:
            logger.error(f"Error unlinking credential: {str(e)}")
            return None, f"Error unlinking credential: {str(e)}"
