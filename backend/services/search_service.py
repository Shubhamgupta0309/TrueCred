"""
Search service for the TrueCred application.

This service provides functions for searching credentials and experiences.
"""
import logging
from datetime import datetime
from mongoengine.queryset.visitor import Q
from models.credential import Credential
from models.experience import Experience
from models.user import User

# Set up logging
logger = logging.getLogger(__name__)

class SearchService:
    """
    Service class for search operations.
    """
    
    @staticmethod
    def search_credentials(
        user_id, 
        query=None, 
        issuer=None, 
        credential_type=None, 
        verified_only=False,
        include_expired=False,
        start_date=None,
        end_date=None,
        sort_by='-created_at',
        page=1,
        per_page=10
    ):
        """
        Search user credentials with various filters.
        
        Args:
            user_id (str): User ID
            query (str, optional): Search query for title, description
            issuer (str, optional): Filter by issuer
            credential_type (str, optional): Filter by credential type
            verified_only (bool, optional): Include only verified credentials
            include_expired (bool, optional): Include expired credentials
            start_date (str, optional): Start date in ISO format
            end_date (str, optional): End date in ISO format
            sort_by (str, optional): Field to sort by (prepend with - for descending)
            page (int, optional): Page number
            per_page (int, optional): Items per page
            
        Returns:
            tuple: (credentials, total_count, total_pages, error)
        """
        try:
            # Build the base query
            user = User.objects.get(id=user_id)
            base_query = Q(user=user)
            
            # Add text search if query provided
            if query:
                text_query = Q(title__icontains=query) | Q(description__icontains=query)
                base_query = base_query & text_query
                
            # Add issuer filter
            if issuer:
                base_query = base_query & Q(issuer__icontains=issuer)
                
            # Add type filter
            if credential_type:
                base_query = base_query & Q(type=credential_type)
                
            # Add verification filter
            if verified_only:
                base_query = base_query & Q(verified=True)
                
            # Add expiration filter
            if not include_expired:
                current_time = datetime.utcnow()
                expiration_query = Q(expiry_date=None) | Q(expiry_date__gt=current_time)
                base_query = base_query & expiration_query
                
            # Add date range filters
            if start_date:
                try:
                    start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    base_query = base_query & Q(issue_date__gte=start_date_obj)
                except ValueError:
                    return [], 0, 0, "Invalid start date format"
                    
            if end_date:
                try:
                    end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    base_query = base_query & Q(issue_date__lte=end_date_obj)
                except ValueError:
                    return [], 0, 0, "Invalid end date format"
            
            # Execute query with pagination
            total_count = Credential.objects(base_query).count()
            total_pages = (total_count + per_page - 1) // per_page
            
            skip = (page - 1) * per_page
            credentials = Credential.objects(base_query).order_by(sort_by).skip(skip).limit(per_page)
            
            logger.info(f"Found {total_count} credentials for user {user_id} with query: {query}")
            return credentials, total_count, total_pages, None
            
        except User.DoesNotExist:
            logger.error(f"User not found: {user_id}")
            return [], 0, 0, "User not found"
        except Exception as e:
            logger.error(f"Error searching credentials: {str(e)}")
            return [], 0, 0, f"Error searching credentials: {str(e)}"
    
    @staticmethod
    def search_experiences(
        user_id, 
        query=None,
        organization=None, 
        exp_type=None,
        current_only=False,
        start_date=None,
        end_date=None,
        verified_only=False,
        has_credentials=False,
        sort_by='-start_date',
        page=1,
        per_page=10
    ):
        """
        Search user experiences with various filters.
        
        Args:
            user_id (str): User ID
            query (str, optional): Search query for title, description, organization
            organization (str, optional): Filter by organization
            exp_type (str, optional): Filter by experience type (work, education)
            current_only (bool, optional): Include only current experiences
            start_date (str, optional): Start date in ISO format
            end_date (str, optional): End date in ISO format
            verified_only (bool, optional): Include only verified experiences
            has_credentials (bool, optional): Include only experiences with linked credentials
            sort_by (str, optional): Field to sort by (prepend with - for descending)
            page (int, optional): Page number
            per_page (int, optional): Items per page
            
        Returns:
            tuple: (experiences, total_count, total_pages, error)
        """
        try:
            # Build the base query
            user = User.objects.get(id=user_id)
            base_query = Q(user=user)
            
            # Add text search if query provided
            if query:
                text_query = Q(title__icontains=query) | Q(description__icontains=query) | Q(organization__icontains=query)
                base_query = base_query & text_query
                
            # Add organization filter
            if organization:
                base_query = base_query & Q(organization__icontains=organization)
                
            # Add type filter
            if exp_type:
                base_query = base_query & Q(type=exp_type)
                
            # Add current filter
            if current_only:
                base_query = base_query & Q(is_current=True)
                
            # Add verification filter
            if verified_only:
                base_query = base_query & Q(verified=True)
                
            # Add credentials filter
            if has_credentials:
                base_query = base_query & Q(credentials__not__size=0)
                
            # Add date range filters
            if start_date:
                try:
                    start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    base_query = base_query & Q(start_date__gte=start_date_obj)
                except ValueError:
                    return [], 0, 0, "Invalid start date format"
                    
            if end_date:
                try:
                    end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    base_query = base_query & Q(start_date__lte=end_date_obj)
                except ValueError:
                    return [], 0, 0, "Invalid end date format"
            
            # Execute query with pagination
            total_count = Experience.objects(base_query).count()
            total_pages = (total_count + per_page - 1) // per_page
            
            skip = (page - 1) * per_page
            experiences = Experience.objects(base_query).order_by(sort_by).skip(skip).limit(per_page)
            
            logger.info(f"Found {total_count} experiences for user {user_id} with query: {query}")
            return experiences, total_count, total_pages, None
            
        except User.DoesNotExist:
            logger.error(f"User not found: {user_id}")
            return [], 0, 0, "User not found"
        except Exception as e:
            logger.error(f"Error searching experiences: {str(e)}")
            return [], 0, 0, f"Error searching experiences: {str(e)}"
            
    @staticmethod
    def search_all(
        user_id,
        query,
        include_credentials=True,
        include_experiences=True,
        page=1,
        per_page=10
    ):
        """
        Search across both credentials and experiences.
        
        Args:
            user_id (str): User ID
            query (str): Search query
            include_credentials (bool, optional): Include credentials in search
            include_experiences (bool, optional): Include experiences in search
            page (int, optional): Page number
            per_page (int, optional): Items per page
            
        Returns:
            tuple: (results, total_count, total_pages, error)
        """
        try:
            results = {
                'credentials': [],
                'experiences': []
            }
            
            # Search credentials if requested
            if include_credentials:
                credentials, cred_count, _, cred_error = SearchService.search_credentials(
                    user_id=user_id,
                    query=query,
                    page=1,  # Get all for combined results
                    per_page=100  # Limit to reasonable number
                )
                
                if cred_error:
                    return results, 0, 0, cred_error
                
                results['credentials'] = [cred.to_json() for cred in credentials]
            
            # Search experiences if requested
            if include_experiences:
                experiences, exp_count, _, exp_error = SearchService.search_experiences(
                    user_id=user_id,
                    query=query,
                    page=1,  # Get all for combined results
                    per_page=100  # Limit to reasonable number
                )
                
                if exp_error:
                    return results, 0, 0, exp_error
                
                results['experiences'] = [exp.to_json() for exp in experiences]
            
            # Calculate totals and handle pagination for combined results
            total_count = len(results['credentials']) + len(results['experiences'])
            total_pages = (total_count + per_page - 1) // per_page
            
            logger.info(f"Found {total_count} combined results for user {user_id} with query: {query}")
            return results, total_count, total_pages, None
            
        except Exception as e:
            logger.error(f"Error in combined search: {str(e)}")
            return {'credentials': [], 'experiences': []}, 0, 0, f"Error in search: {str(e)}"
