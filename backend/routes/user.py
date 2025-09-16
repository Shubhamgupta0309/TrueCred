"""
User profile routes providing /api/user/profile endpoints that return raw user JSON.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import AuthService
from datetime import datetime
from models.user import Education
import logging

logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__, url_prefix='/api/user')


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user, error = AuthService.get_user_by_id(current_user_id)
    if error:
        return jsonify({
            'success': False,
            'message': error
        }), 404
        
    # Return user profile with success flag
    return jsonify({
        'success': True,
        'user': user.to_json()
    }), 200


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    data = request.json or {}
    logger.info(f"Profile update request received for user {current_user_id}: {data}")
    
    user, error = AuthService.get_user_by_id(current_user_id)
    if error:
        logger.error(f"User not found: {error}")
        return jsonify({
            'success': False,
            'message': error
        }), 404
        
    try:
        # Basic fields
        updatable_fields = ['first_name', 'last_name', 'email']
        changes = {}
        for f in updatable_fields:
            if f in data and data[f] is not None:
                setattr(user, f, data[f])
                changes[f] = data[f]
        
        # Handle education data
        if 'education' in data and isinstance(data['education'], list):
            try:
                # Clear current education list
                user.education = []
                
                # Add each education entry as an Education embedded document
                for edu_data in data['education']:
                    education = Education(
                        institution=edu_data.get('institution', ''),
                        institution_id=edu_data.get('institution_id', ''),
                        degree=edu_data.get('degree', ''),
                        field_of_study=edu_data.get('field_of_study', ''),
                        start_date=edu_data.get('start_date', ''),
                        end_date=edu_data.get('end_date', ''),
                        current=edu_data.get('current', False)
                    )
                    user.education.append(education)
                    
                # Mark profile as completed
                user.profile_completed = True
                changes['profile_completed'] = True
                changes['education'] = 'Updated education data'
                
            except Exception as e:
                logger.error(f"Error handling education data: {str(e)}", exc_info=True)
                return jsonify({
                    'success': False,
                    'message': f"Error processing education data: {str(e)}"
                }), 400
            
        if changes:
            user.updated_at = datetime.utcnow()
            user.save()
            
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': user.to_json()
        }), 200
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f"Error updating profile: {str(e)}"
        }), 500
