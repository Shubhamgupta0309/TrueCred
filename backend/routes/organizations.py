"""
Routes for fetching organizations (companies and institutions).
"""
from flask import Blueprint, jsonify
from models.user import User

# Create a Blueprint for organization-related routes
org_bp = Blueprint('organizations', __name__, url_prefix='/api/organizations')

@org_bp.route('/companies', methods=['GET'])
def get_companies():
    """
    Get a list of all companies in the system.
    
    Returns:
        A JSON response with a list of companies.
    """
    try:
        # Find all users with role 'company' or all users with an organization and role 'company'
        companies = User.objects(role='company').only('id', 'organization')
        
        # Format the companies for the response
        company_list = [
            {
                'id': str(company.id),
                'name': company.organization
            }
            for company in companies
            if company.organization  # Only include if organization field is not empty
        ]
        
        return jsonify({
            'success': True,
            'companies': company_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch companies: {str(e)}'
        }), 500

@org_bp.route('/institutions', methods=['GET'])
def get_institutions():
    """
    Get a list of all educational institutions (colleges, universities) in the system.
    Query parameters:
        query: Optional search string to filter institutions
    
    Returns:
        A JSON response with a list of institutions.
    """
    from models.organization_profile import OrganizationProfile
    from flask import request
    import logging
    
    logger = logging.getLogger(__name__)
    search_query = request.args.get('query', '')
    
    try:
        logger.info(f"Fetching institutions with search query: '{search_query}'")
        
        # First get all college users to get the mapping between user_id and colleges
        college_users = User.objects(role='college').only('id', 'organization')
        college_user_ids = [str(user.id) for user in college_users]
        
        # Query organization profiles for college users
        query_filter = {'user_id__in': college_user_ids}
        
        # Add text search if query parameter is provided
        if search_query:
            # Case-insensitive search in both name and fullName fields
            # Using MongoEngine's Q objects for OR queries
            from mongoengine.queryset.visitor import Q
            query_filter = {
                'user_id__in': college_user_ids,
                '$or': [
                    Q(name__icontains=search_query) | 
                    Q(fullName__icontains=search_query)
                ]
            }
            
        # Fetch organization profiles
        org_profiles = OrganizationProfile.objects(**query_filter).only('id', 'user_id', 'name', 'fullName')
        
        # Format the institutions for the response
        institution_list = []
        for profile in org_profiles:
            institution_list.append({
                'id': str(profile.id),
                'user_id': profile.user_id,
                'name': profile.name,
                'fullName': profile.fullName
            })
        
        # Sort alphabetically by fullName or name
        institution_list.sort(key=lambda x: (x.get('fullName') or x.get('name', '')).lower())
        
        # If no organization profiles found, fall back to user organization field
        if not institution_list:
            logger.info("No organization profiles found, falling back to user.organization field")
            filtered_users = college_users
            if search_query:
                filtered_users = [user for user in college_users 
                                 if user.organization and search_query.lower() in user.organization.lower()]
            
            institution_list = [
                {
                    'id': str(user.id),
                    'user_id': str(user.id),
                    'name': user.organization
                }
                for user in filtered_users
                if user.organization  # Only include if organization field is not empty
            ]
            
            # Sort alphabetically
            institution_list.sort(key=lambda x: x['name'].lower())
        
        logger.info(f"Returning {len(institution_list)} institutions")
        return jsonify({
            'success': True,
            'institutions': institution_list
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching institutions: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to fetch institutions: {str(e)}'
        }), 500
