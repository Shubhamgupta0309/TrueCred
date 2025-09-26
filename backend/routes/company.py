"""
Company profile routes for the TrueCred API.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models.user import User
from models.organization_profile import OrganizationProfile
from utils.api_response import success_response, error_response
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
company_bp = Blueprint('company', __name__, url_prefix='/api/company')

@company_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_company_profile():
    """
    Get the current user's company profile.

    Returns:
        Company profile data
    """
    try:
        current_user_id = get_jwt_identity()
        logger.info(f"Getting company profile for user_id: {current_user_id} (type: {type(current_user_id)})")
        
        # Try to get organization profile first
        org_profile = OrganizationProfile.objects(user_id=str(current_user_id)).first()
        logger.info(f"Query result - found organization profile: {org_profile}")
        
        if org_profile:
            logger.info(f"Organization profile data: {org_profile.to_json()}")
            return success_response(
                data=org_profile.to_json(),
                message="Company profile retrieved successfully"
            )
        else:
            logger.info(f"No organization profile found for user_id: {current_user_id}")
            # Fall back to user organization field
            user = User.objects.get(id=current_user_id)
            logger.info(f"Fallback user data: organization={user.organization}, email={user.email}")
            return success_response(
                data={
                    'name': user.organization or user.first_name or 'Company',
                    'fullName': '',
                    'address': '',
                    'city': '',
                    'state': '',
                    'country': '',
                    'postalCode': '',
                    'website': '',
                    'phone': '',
                    'email': user.email,
                    'accreditationBody': '',
                    'establishmentYear': '',
                    'description': ''
                },
                message="Company profile retrieved successfully"
            )

    except Exception as e:
        logger.error(f"Error fetching company profile: {str(e)}", exc_info=True)
        return error_response(
            message=f'Failed to fetch company profile: {str(e)}',
            status_code=500
        )


@company_bp.route('/profile', methods=['POST'])
@jwt_required()
def update_company_profile():
    """
    Update the current user's company profile.

    Returns:
        Success status
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        logger.info(f"Updating company profile for user_id: {current_user_id} (type: {type(current_user_id)}) with data: {data}")

        # Get or create organization profile
        org_profile = OrganizationProfile.objects(user_id=str(current_user_id)).first()
        if not org_profile:
            org_profile = OrganizationProfile(user_id=str(current_user_id))
            logger.info(f"Created new organization profile for user_id: {current_user_id}")
        
        # Update fields
        fields_to_update = [
            'name', 'fullName', 'address', 'city', 'state', 'country', 
            'postalCode', 'website', 'phone', 'email', 'accreditationBody',
            'establishmentYear', 'description'
        ]
        
        for field in fields_to_update:
            if field in data:
                setattr(org_profile, field, data[field])
        
        org_profile.updated_at = datetime.utcnow()
        org_profile.save()
        logger.info(f"Saved organization profile: {org_profile.to_json()}")

        return success_response(
            message="Company profile updated successfully"
        )

    except Exception as e:
        logger.error(f"Error updating company profile: {str(e)}", exc_info=True)
        return error_response(
            message=f'Failed to update company profile: {str(e)}',
            status_code=500
        )


@company_bp.route('/debug/profiles', methods=['GET'])
@jwt_required()
def debug_profiles():
    """
    Debug endpoint to see all organization profiles.
    """
    try:
        current_user_id = get_jwt_identity()
        logger.info(f"Debug - Current JWT user_id: {current_user_id} (type: {type(current_user_id)})")
        
        # Get all profiles
        all_profiles = OrganizationProfile.objects.all()
        logger.info(f"Total profiles in DB: {len(all_profiles)}")
        
        # Check if current user has a profile
        user_profile = OrganizationProfile.objects(user_id=str(current_user_id)).first()
        logger.info(f"User profile found: {user_profile}")
        
        result = []
        for p in all_profiles:
            result.append({
                'id': str(p.id),
                'user_id': p.user_id,
                'user_id_type': type(p.user_id).__name__,
                'name': p.name,
                'email': p.email,
                'matches_current_user': p.user_id == str(current_user_id)
            })
        
        return jsonify({
            'current_user_id': current_user_id,
            'current_user_id_str': str(current_user_id),
            'profiles': result
        }), 200
    except Exception as e:
        logger.error(f"Debug error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500