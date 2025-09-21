"""
Search routes for the TrueCred API.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.search_service import SearchService
from utils.api_response import success_response, error_response, validation_error_response
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
search_bp = Blueprint('search', __name__)

@search_bp.route('/credentials', methods=['GET'])
@jwt_required()
def search_credentials():
    """
    Search credentials with filters and pagination.
    ---
    Requires authentication.
    
    Query Parameters:
      q: Search query for title, description
      issuer: Filter by issuer
      type: Filter by credential type
      verified: Filter by verification status (true/false)
      include_expired: Include expired credentials (true/false)
      start_date: Filter by issue date (from) in ISO format
      end_date: Filter by issue date (to) in ISO format
      sort_by: Field to sort by (created_at, title, issuer, etc., prepend with - for descending)
      page: Page number (default: 1)
      per_page: Results per page (default: 10)
    
    Returns:
      List of matching credentials with pagination metadata
    """
    current_user_id = get_jwt_identity()
    
    # Get query parameters with defaults
    query = request.args.get('q')
    issuer = request.args.get('issuer')
    credential_type = request.args.get('type')
    verified_only = request.args.get('verified', 'false').lower() == 'true'
    include_expired = request.args.get('include_expired', 'false').lower() == 'true'
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sort_by = request.args.get('sort_by', '-created_at')
    
    # Pagination parameters
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 50)  # Cap at 50 items per page
        
        if page < 1 or per_page < 1:
            return validation_error_response(
                errors={"pagination": "Page and per_page must be positive integers"},
                message="Invalid pagination parameters"
            )
    except ValueError:
        return validation_error_response(
            errors={"pagination": "Page and per_page must be valid integers"},
            message="Invalid pagination parameters"
        )
    
    # Perform search
    credentials, total_count, total_pages, error = SearchService.search_credentials(
        user_id=current_user_id,
        query=query,
        issuer=issuer,
        credential_type=credential_type,
        verified_only=verified_only,
        include_expired=include_expired,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        page=page,
        per_page=per_page
    )
    
    if error:
        return error_response(message=error, status_code=400)
    
    # Return search results
    return success_response(
        data={
            'credentials': [cred.to_json() for cred in credentials],
            'pagination': {
                'total_count': total_count,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        },
        message=f"Found {total_count} credentials matching your search"
    )

@search_bp.route('/experiences', methods=['GET'])
@jwt_required()
def search_experiences():
    """
    Search experiences with filters and pagination.
    ---
    Requires authentication.
    
    Query Parameters:
      q: Search query for title, description, organization
      organization: Filter by organization
      type: Filter by experience type (work, education)
      current: Filter by current status (true/false)
      verified: Filter by verification status (true/false)
      has_credentials: Filter to experiences with linked credentials (true/false)
      start_date: Filter by start date (from) in ISO format
      end_date: Filter by start date (to) in ISO format
      sort_by: Field to sort by (start_date, title, organization, etc., prepend with - for descending)
      page: Page number (default: 1)
      per_page: Results per page (default: 10)
    
    Returns:
      List of matching experiences with pagination metadata
    """
    current_user_id = get_jwt_identity()
    
    # Get query parameters with defaults
    query = request.args.get('q')
    organization = request.args.get('organization')
    exp_type = request.args.get('type')
    current_only = request.args.get('current', 'false').lower() == 'true'
    verified_only = request.args.get('verified', 'false').lower() == 'true'
    has_credentials = request.args.get('has_credentials', 'false').lower() == 'true'
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sort_by = request.args.get('sort_by', '-start_date')
    
    # Pagination parameters
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 50)  # Cap at 50 items per page
        
        if page < 1 or per_page < 1:
            return validation_error_response(
                errors={"pagination": "Page and per_page must be positive integers"},
                message="Invalid pagination parameters"
            )
    except ValueError:
        return validation_error_response(
            errors={"pagination": "Page and per_page must be valid integers"},
            message="Invalid pagination parameters"
        )
    
    # Perform search
    experiences, total_count, total_pages, error = SearchService.search_experiences(
        user_id=current_user_id,
        query=query,
        organization=organization,
        exp_type=exp_type,
        current_only=current_only,
        verified_only=verified_only,
        has_credentials=has_credentials,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        page=page,
        per_page=per_page
    )
    
    if error:
        return error_response(message=error, status_code=400)
    
    # Return search results
    return success_response(
        data={
            'experiences': [exp.to_json() for exp in experiences],
            'pagination': {
                'total_count': total_count,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        },
        message=f"Found {total_count} experiences matching your search"
    )

@search_bp.route('/', methods=['GET'])
@jwt_required()
def search_all():
    """
    Perform a combined search across credentials and experiences.
    ---
    Requires authentication.
    
    Query Parameters:
      q: Search query (required)
      include_credentials: Include credentials in search (true/false, default: true)
      include_experiences: Include experiences in search (true/false, default: true)
      page: Page number (default: 1)
      per_page: Results per page (default: 10)
    
    Returns:
      Combined search results with pagination metadata
    """
    current_user_id = get_jwt_identity()
    
    # Get search query
    query = request.args.get('q')
    if not query or len(query.strip()) < 2:
        return validation_error_response(
            errors={"q": "Search query must be at least 2 characters"},
            message="Invalid search query"
        )
    
    # Get search options
    include_credentials = request.args.get('include_credentials', 'true').lower() == 'true'
    include_experiences = request.args.get('include_experiences', 'true').lower() == 'true'
    
    # Ensure at least one type is included
    if not include_credentials and not include_experiences:
        return validation_error_response(
            errors={"search_types": "At least one of credentials or experiences must be included"},
            message="Invalid search parameters"
        )
    
    # Pagination parameters
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 50)  # Cap at 50 items per page
        
        if page < 1 or per_page < 1:
            return validation_error_response(
                errors={"pagination": "Page and per_page must be positive integers"},
                message="Invalid pagination parameters"
            )
    except ValueError:
        return validation_error_response(
            errors={"pagination": "Page and per_page must be valid integers"},
            message="Invalid pagination parameters"
        )
    
    # Perform search
    results, total_count, total_pages, error = SearchService.search_all(
        user_id=current_user_id,
        query=query,
        include_credentials=include_credentials,
        include_experiences=include_experiences,
        page=page,
        per_page=per_page
    )
    
    if error:
        return error_response(message=error, status_code=400)
    
    # Return search results
    return success_response(
        data={
            'results': results,
            'pagination': {
                'total_count': total_count,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        },
        message=f"Found {total_count} items matching your search"
    )
