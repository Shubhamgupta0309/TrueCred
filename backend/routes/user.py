"""
User profile routes providing /api/user/profile endpoints that return raw user JSON.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import AuthService
from datetime import datetime
from models.user import Education
import logging
from mongoengine.errors import ValidationError

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
                # Validate each incoming education entry before modifying user
                new_education = []
                for idx, edu_data in enumerate(data['education']):
                    # Required fields check
                    inst = (edu_data.get('institution') or '').strip()
                    degree = (edu_data.get('degree') or '').strip()
                    field = (edu_data.get('field_of_study') or '').strip()
                    start = (edu_data.get('start_date') or '').strip()
                    end = (edu_data.get('end_date') or '').strip()
                    current = bool(edu_data.get('current', False))

                    if not inst or not degree or not field or not start:
                        return jsonify({
                            'success': False,
                            'message': f'Invalid education entry at index {idx}: institution, degree, field_of_study and start_date are required.'
                        }), 400

                    if not current and not end:
                        return jsonify({
                            'success': False,
                            'message': f'Invalid education entry at index {idx}: end_date is required when current is false.'
                        }), 400

                    # Create Education embedded document (will be validated on save)
                    education = Education(
                        institution=inst,
                        institution_id=edu_data.get('institution_id', ''),
                        degree=degree,
                        field_of_study=field,
                        start_date=start,
                        end_date=end,
                        current=current
                    )
                    # call embedded validation to catch issues early
                    education.clean()
                    new_education.append(education)

                # All entries validated: replace user's education list
                user.education = new_education
                user.profile_completed = True
                changes['profile_completed'] = True
                changes['education'] = f'Updated {len(new_education)} education entries'

            except ValidationError as e:
                logger.error(f"Validation error handling education data: {str(e)}", exc_info=True)
                return jsonify({
                    'success': False,
                    'message': f"Validation error processing education data: {str(e)}"
                }), 400
            except Exception as e:
                logger.error(f"Error handling education data: {str(e)}", exc_info=True)
                return jsonify({
                    'success': False,
                    'message': f"Error processing education data: {str(e)}"
                }), 500
            
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
