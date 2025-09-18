from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import AuthService
from datetime import datetime
from models.user import Education
import logging
from mongoengine.errors import ValidationError

logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

# Endpoint to fetch all students (for college dashboard dropdown)
@user_bp.route('/all-students', methods=['GET'])
@jwt_required()
def get_all_students():
    """
    Fetch all users with role 'student'.
    Returns: list of students with email, name, and education info
    """
    try:
        from models.user import User
        students = User.objects(role='student')
        result = []
        for user in students:
            result.append({
                'id': str(user.id),
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username,
                'education': [e.to_mongo().to_dict() for e in user.education]
            })
        return jsonify({'success': True, 'students': result}), 200
    except Exception as e:
        logger.error(f"Error fetching all students: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500

logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

# ...existing code...

@user_bp.route('/students/by-college', methods=['GET'])
@jwt_required()
def get_students_by_college():
    """
    Fetch students who have added the given college name in their education.
    Query param: college_name (required)
    Returns: list of students with email, name, and education info
    """
    college_name = request.args.get('college_name', '').strip()
    if not college_name:
        return jsonify({'success': False, 'message': 'college_name is required'}), 400

    try:
        from models.user import User
        # Find users with role 'student' and education.institution matching college_name
        students = User.objects(role='student', education__institution=college_name)
        result = []
        for user in students:
            edu_match = [edu for edu in user.education if edu.institution == college_name]
            result.append({
                'id': str(user.id),
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username,
                'education': [e.to_mongo().to_dict() for e in edu_match]
            })
        return jsonify({'success': True, 'students': result}), 200
    except Exception as e:
        logger.error(f"Error fetching students by college: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
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


@user_bp.route('/requests', methods=['GET'])
@jwt_required()
def get_my_requests():
    """Return credential requests created by the current student."""
    try:
        current_user_id = get_jwt_identity()
        db = getattr(__import__('flask').current_app, 'db', None)
        if db is not None:
            cursor = db.credential_requests.find({'user_id': str(current_user_id)}).sort('created_at', -1)
            results = []
            for doc in cursor:
                doc['id'] = str(doc.get('_id'))
                doc.pop('_id', None)
                results.append(doc)
            return jsonify({'success': True, 'requests': results}), 200
        return jsonify({'success': True, 'requests': []}), 200
    except Exception as e:
        logger.exception(e)
        return jsonify({'success': False, 'message': str(e)}), 500
