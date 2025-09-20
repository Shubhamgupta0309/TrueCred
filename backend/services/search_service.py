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
    
    @staticmethod
    def search_institutions(
        user_id,
        query=None,
        institution_type=None,
        location=None,
        country=None,
        state=None,
        city=None,
        verified_only=False,
        accreditation_status=None,
        founded_after=None,
        founded_before=None,
        sort_by='-created_at',
        page=1,
        per_page=10
    ):
        """
        Search institutions with advanced filters.
        
        Args:
            user_id (str): User ID (for access control)
            query (str, optional): Search query for name, description
            institution_type (str, optional): Filter by institution type
            location (str, optional): Filter by location (general)
            country (str, optional): Filter by country
            state (str, optional): Filter by state/province
            city (str, optional): Filter by city
            verified_only (bool, optional): Include only verified institutions
            accreditation_status (str, optional): Filter by accreditation status
            founded_after (str, optional): Founded after date (YYYY-MM-DD)
            founded_before (str, optional): Founded before date (YYYY-MM-DD)
            sort_by (str, optional): Field to sort by
            page (int, optional): Page number
            per_page (int, optional): Items per page
            
        Returns:
            tuple: (institutions list, total_count, total_pages, error)
        """
        try:
            from models.organization_profile import OrganizationProfile
            
            # Build query
            search_query = Q()
            
            if query:
                # Search in name and description
                search_query &= (Q(name__icontains=query) | Q(description__icontains=query))
            
            if institution_type:
                search_query &= Q(institution_type=institution_type)
            
            # Location-based filters
            if location:
                # Search in address, city, state, country fields
                location_query = (
                    Q(address__icontains=location) |
                    Q(city__icontains=location) |
                    Q(state__icontains=location) |
                    Q(country__icontains=location)
                )
                search_query &= location_query
            
            if country:
                search_query &= Q(country__icontains=country)
            
            if state:
                search_query &= Q(state__icontains=state)
            
            if city:
                search_query &= Q(city__icontains=city)
            
            if verified_only:
                search_query &= Q(is_verified=True)
            
            if accreditation_status:
                search_query &= Q(accreditation_status=accreditation_status)
            
            # Date range filters for founding date
            if founded_after:
                try:
                    from datetime import datetime
                    after_date = datetime.strptime(founded_after, '%Y-%m-%d').date()
                    search_query &= Q(founded_date__gte=after_date)
                except ValueError:
                    return [], 0, 0, "Invalid founded_after date format. Use YYYY-MM-DD"
            
            if founded_before:
                try:
                    from datetime import datetime
                    before_date = datetime.strptime(founded_before, '%Y-%m-%d').date()
                    search_query &= Q(founded_date__lte=before_date)
                except ValueError:
                    return [], 0, 0, "Invalid founded_before date format. Use YYYY-MM-DD"
            
            # Get total count
            total_count = OrganizationProfile.objects(search_query).count()
            total_pages = (total_count + per_page - 1) // per_page
            
            # Apply pagination and sorting
            institutions = OrganizationProfile.objects(search_query).order_by(sort_by).skip((page - 1) * per_page).limit(per_page)
            
            # Convert to JSON
            results = []
            for inst in institutions:
                results.append(inst.to_json())
            
            logger.info(f"Found {total_count} institutions for user {user_id} with advanced filters")
            return results, total_count, total_pages, None
            
        except Exception as e:
            logger.error(f"Error searching institutions: {str(e)}")
            return [], 0, 0, f"Error searching institutions: {str(e)}"
    
    @staticmethod
    def search_students(
        user_id,
        query=None,
        institution=None,
        program=None,
        graduation_year=None,
        graduation_year_after=None,
        graduation_year_before=None,
        location=None,
        country=None,
        state=None,
        city=None,
        verified_only=False,
        has_credentials=False,
        has_experiences=False,
        sort_by='first_name',
        page=1,
        per_page=10
    ):
        """
        Search students directory with advanced filters.
        
        Args:
            user_id (str): User ID (must be institution admin)
            query (str, optional): Search query for name, email, program
            institution (str, optional): Filter by institution
            program (str, optional): Filter by program/degree
            graduation_year (str, optional): Filter by specific graduation year
            graduation_year_after (str, optional): Filter by graduation year after
            graduation_year_before (str, optional): Filter by graduation year before
            location (str, optional): Filter by location (general)
            country (str, optional): Filter by country
            state (str, optional): Filter by state/province
            city (str, optional): Filter by city
            verified_only (bool, optional): Include only verified students
            has_credentials (bool, optional): Include only students with credentials
            has_experiences (bool, optional): Include only students with experiences
            sort_by (str, optional): Field to sort by
            page (int, optional): Page number
            per_page (int, optional): Items per page
            
        Returns:
            tuple: (students list, total_count, total_pages, error)
        """
        try:
            # Verify user is institution admin
            user = User.objects.get(id=user_id)
            if user.role not in ['college', 'company', 'admin']:
                return [], 0, 0, "Access denied: Institution access required"
            
            # Build query
            search_query = Q()
            
            if query:
                # Search in name, email, username
                search_query &= (
                    Q(first_name__icontains=query) | 
                    Q(last_name__icontains=query) | 
                    Q(email__icontains=query) |
                    Q(username__icontains=query)
                )
            
            # Filter by institution if specified or user's institution
            if institution:
                # Find users with education from specified institution
                education_query = Q(education__institution__icontains=institution)
                search_query &= education_query
            else:
                # Default to users associated with current user's institution
                from models.organization_profile import OrganizationProfile
                org_profile = OrganizationProfile.objects(user_id=user_id).first()
                if org_profile:
                    education_query = Q(education__institution__icontains=org_profile.name)
                    search_query &= education_query
            
            if program:
                search_query &= Q(education__degree__icontains=program)
            
            # Graduation year filters
            if graduation_year:
                try:
                    year = int(graduation_year)
                    # Find users with education ending in specified year
                    search_query &= Q(education__end_date__gte=datetime(year, 1, 1)) & Q(education__end_date__lt=datetime(year + 1, 1, 1))
                except ValueError:
                    pass
            
            if graduation_year_after:
                try:
                    year = int(graduation_year_after)
                    search_query &= Q(education__end_date__gte=datetime(year, 1, 1))
                except ValueError:
                    pass
            
            if graduation_year_before:
                try:
                    year = int(graduation_year_before)
                    search_query &= Q(education__end_date__lt=datetime(year + 1, 1, 1))
                except ValueError:
                    pass
            
            # Location-based filters
            if location:
                # Search in address fields
                location_query = (
                    Q(address__icontains=location) |
                    Q(city__icontains=location) |
                    Q(state__icontains=location) |
                    Q(country__icontains=location)
                )
                search_query &= location_query
            
            if country:
                search_query &= Q(country__icontains=country)
            
            if state:
                search_query &= Q(state__icontains=state)
            
            if city:
                search_query &= Q(city__icontains=city)
            
            # Verification and content filters
            verified_user_ids = set()
            
            if verified_only or has_credentials or has_experiences:
                from models.credential import Credential
                from models.experience import Experience
                
                if has_credentials:
                    # Users with any credentials
                    cred_users = Credential.objects(user__in=User.objects(search_query)).distinct('user')
                    if cred_users:
                        verified_user_ids.update(str(u.id) for u in cred_users)
                    else:
                        return [], 0, 0, None
                
                if has_experiences:
                    # Users with any experiences
                    exp_users = Experience.objects(user__in=User.objects(search_query)).distinct('user')
                    if exp_users:
                        verified_user_ids.update(str(u.id) for u in exp_users)
                    else:
                        return [], 0, 0, None
                
                if verified_only:
                    # Users with verified credentials or experiences
                    verified_creds = Credential.objects(user__in=User.objects(search_query), status='verified').distinct('user')
                    verified_exps = Experience.objects(user__in=User.objects(search_query), is_verified=True).distinct('user')
                    
                    verified_ids = set(str(u.id) for u in verified_creds) | set(str(u.id) for u in verified_exps)
                    if verified_ids:
                        verified_user_ids.update(verified_ids)
                    else:
                        return [], 0, 0, None
                
                if verified_user_ids:
                    search_query &= Q(id__in=list(verified_user_ids))
            
            # Get total count
            total_count = User.objects(search_query).count()
            total_pages = (total_count + per_page - 1) // per_page
            
            # Apply pagination and sorting
            students = User.objects(search_query).order_by(sort_by).skip((page - 1) * per_page).limit(per_page)
            
            # Convert to JSON with additional info
            results = []
            for student in students:
                student_data = student.to_json()
                
                # Add education info
                if hasattr(student, 'education') and student.education:
                    current_edu = None
                    for edu in student.education:
                        if edu.current or not current_edu:
                            current_edu = edu
                    if current_edu:
                        student_data['current_program'] = f"{current_edu.degree} in {current_edu.field_of_study}"
                        student_data['current_institution'] = current_edu.institution
                        if current_edu.end_date:
                            student_data['graduation_year'] = current_edu.end_date.year
                
                # Add verification status
                verified_creds = Credential.objects(user=student, status='verified').count()
                verified_exps = Experience.objects(user=student, is_verified=True).count()
                student_data['verified_items'] = verified_creds + verified_exps
                student_data['total_credentials'] = Credential.objects(user=student).count()
                student_data['total_experiences'] = Experience.objects(user=student).count()
                
                results.append(student_data)
            
            logger.info(f"Found {total_count} students for institution user {user_id} with advanced filters")
            return results, total_count, total_pages, None
            
        except Exception as e:
            logger.error(f"Error searching students: {str(e)}")
            return [], 0, 0, f"Error searching students: {str(e)}"
