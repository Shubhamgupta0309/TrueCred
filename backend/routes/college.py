"""
College profile routes for managing college institution profiles.
"""
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.organization_profile import OrganizationProfile
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

college_bp = Blueprint('college', __name__, url_prefix='/api/college')

@college_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_college_profile():
    """
    Get the college profile for the current authenticated user.
    
    Returns:
        A JSON response with the college profile information.
    """
    try:
        current_user_id = get_jwt_identity()
        logger.info(f"Getting college profile for user {current_user_id}")
        
        # First, get the user to verify they are a college
        user = User.objects(id=current_user_id).first()
        if not user:
            logger.warning(f"User not found: {current_user_id}")
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Check if the user is a college
        if user.role != 'college':
            logger.warning(f"User {current_user_id} with role {user.role} attempted to access college profile")
            return jsonify({
                'success': False,
                'message': 'Only college accounts can access this endpoint'
            }), 403
        
        # Get the organization profile
        profile = OrganizationProfile.objects(user_id=current_user_id).first()
        
        if not profile:
            logger.info(f"No college profile found for user {current_user_id}")
            return jsonify({
                'success': True,
                'data': {
                    'exists': False,
                    'message': 'No profile exists yet. Please create one.'
                }
            }), 200
        
        # Return the profile data
        profile_json = profile.to_json()
        logger.debug(f"Returning profile data: {profile_json}")
        return jsonify({
            'success': True,
            'data': profile_json
        }), 200
        
    except Exception as e:
        logger.error(f'Error getting college profile: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500

@college_bp.route('/profile', methods=['POST'])
@jwt_required()
def update_college_profile():
    """
    Update or create the college profile for the current authenticated user.
    
    Returns:
        A JSON response indicating success or failure.
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.json or {}
        
        logger.info(f"Processing college profile update for user {current_user_id}")
        logger.debug(f"Profile data: {data}")
        
        # First, get the user to verify they are a college
        user = User.objects(id=current_user_id).first()
        if not user:
            logger.warning(f"User not found: {current_user_id}")
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Check if the user is a college
        if user.role != 'college':
            logger.warning(f"User {current_user_id} with role {user.role} attempted to update college profile")
            return jsonify({
                'success': False,
                'message': 'Only college accounts can update college profiles'
            }), 403
        
        # Find or create the organization profile
        profile = OrganizationProfile.objects(user_id=current_user_id).first()
        
        if not profile:
            logger.info(f"Creating new organization profile for user {current_user_id}")
            profile = OrganizationProfile(user_id=current_user_id)
        else:
            logger.info(f"Updating existing organization profile for user {current_user_id}")
        
        # Update fields from request data
        fields_to_update = [
            'name', 'fullName', 'address', 'city', 'state', 'country', 
            'postalCode', 'website', 'phone', 'email', 'accreditationBody',
            'establishmentYear', 'description'
        ]
        
        for field in fields_to_update:
            if field in data:
                setattr(profile, field, data[field])
        
        # Update timestamps
        profile.updated_at = datetime.utcnow()
        
        # Save the profile
        profile.save()
        
        # Also update the organization field in the user document
        if 'name' in data and data['name']:
            user.organization = data['name']
            user.save()
        
        logger.info(f"College profile updated successfully for user {current_user_id}")
        return jsonify({
            'success': True,
            'message': 'College profile updated successfully',
            'data': profile.to_json()
        }), 200
        
    except Exception as e:
        logger.error(f'Error updating college profile: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500

@college_bp.route('/pending-requests', methods=['GET'])
@jwt_required()
def get_pending_requests():
    """
    Get all pending credential verification requests for the college.

    Returns:
        A JSON response with the pending requests.
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()
        if not user or user.role != 'college':
            return jsonify({'success': False, 'message': 'Only college accounts can access pending requests'}), 403

        # Use MongoEngine instead of PyMongo for consistency
        from models.credential_request import CredentialRequest

        # Query using MongoEngine - this is more reliable than PyMongo
        requests = CredentialRequest.objects(
            issuer_id=str(current_user_id),
            status='pending'
        ).order_by('-created_at')

        # Convert to JSON
        requests_data = []
        for req in requests:
            requests_data.append({
                'id': str(req.id),
                'user_id': req.user_id,
                'title': req.title,
                'issuer': req.issuer,
                'issuer_id': req.issuer_id,
                'type': req.type,
                'status': req.status,
                'created_at': req.created_at.isoformat() if req.created_at else None,
                'updated_at': req.updated_at.isoformat() if req.updated_at else None
            })

        return jsonify({'success': True, 'requests': requests_data}), 200

    except Exception as e:
        logger.exception(f'Error getting pending requests: {str(e)}')
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500

@college_bp.route('/verification-history', methods=['GET'])
@jwt_required()
def get_verification_history():
    """
    Get the verification history for the college.
    
    Returns:
        A JSON response with the verification history.
    """
    try:
        # This is a placeholder that would be implemented with actual database queries
        # For now, we'll return mock data
        return jsonify({
            'success': True,
            'history': [
                {
                    'id': 101,
                    'studentName': 'Emily White',
                    'credentialTitle': 'Graphic Design Certificate',
                    'status': 'Verified',
                    'actionDate': 'Nov 14, 2023'
                },
                {
                    'id': 102,
                    'studentName': 'David Green',
                    'credentialTitle': 'Business Administration Degree',
                    'status': 'Rejected',
                    'actionDate': 'Nov 12, 2023'
                }
            ]
        }), 200
    except Exception as e:
        logger.error(f'Error getting verification history: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500
