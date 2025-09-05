"""
Experience management routes for the TrueCred API.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import ValidationError, DoesNotExist
from models.experience import Experience
from models.user import User

# Create blueprint
experiences_bp = Blueprint('experiences', __name__)

@experiences_bp.route('/', methods=['GET'])
@jwt_required()
def get_experiences():
    """
    Get experiences for the current user.
    ---
    Requires authentication.
    """
    current_user_id = get_jwt_identity()
    try:
        user = User.objects.get(id=current_user_id)
        experiences = Experience.objects(user=user).order_by('-start_date')
        return jsonify({
            'success': True,
            'experiences': [exp.to_json() for exp in experiences]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving experiences: {str(e)}'
        }), 500

@experiences_bp.route('/', methods=['POST'])
@jwt_required()
def create_experience():
    """
    Create a new experience.
    ---
    Requires authentication.
    """
    current_user_id = get_jwt_identity()
    data = request.json
    
    try:
        user = User.objects.get(id=current_user_id)
        
        # Parse dates
        start_date = datetime.fromisoformat(data.get('start_date')) if data.get('start_date') else None
        end_date = datetime.fromisoformat(data.get('end_date')) if data.get('end_date') else None
        
        # Create experience
        experience = Experience(
            user=user,
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
        
        experience.save()
        
        return jsonify({
            'success': True,
            'message': 'Experience created successfully',
            'experience': experience.to_json()
        }), 201
    
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': f'Validation error: {str(e)}'
        }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating experience: {str(e)}'
        }), 500

@experiences_bp.route('/<experience_id>', methods=['GET'])
@jwt_required()
def get_experience(experience_id):
    """
    Get a specific experience.
    ---
    Requires authentication.
    """
    current_user_id = get_jwt_identity()
    
    try:
        user = User.objects.get(id=current_user_id)
        experience = Experience.objects.get(id=experience_id)
        
        # Check if the experience belongs to the user
        if str(experience.user.id) != current_user_id:
            return jsonify({
                'success': False,
                'message': 'You do not have permission to view this experience'
            }), 403
        
        return jsonify({
            'success': True,
            'experience': experience.to_json()
        }), 200
    
    except DoesNotExist:
        return jsonify({
            'success': False,
            'message': 'Experience not found'
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving experience: {str(e)}'
        }), 500

@experiences_bp.route('/<experience_id>', methods=['PUT'])
@jwt_required()
def update_experience(experience_id):
    """
    Update a specific experience.
    ---
    Requires authentication.
    """
    current_user_id = get_jwt_identity()
    data = request.json
    
    try:
        user = User.objects.get(id=current_user_id)
        experience = Experience.objects.get(id=experience_id)
        
        # Check if the experience belongs to the user
        if str(experience.user.id) != current_user_id:
            return jsonify({
                'success': False,
                'message': 'You do not have permission to update this experience'
            }), 403
        
        # Update fields
        if 'title' in data:
            experience.title = data['title']
        if 'organization' in data:
            experience.organization = data['organization']
        if 'start_date' in data:
            experience.start_date = datetime.fromisoformat(data['start_date'])
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
        
        experience.save()
        
        return jsonify({
            'success': True,
            'message': 'Experience updated successfully',
            'experience': experience.to_json()
        }), 200
    
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': f'Validation error: {str(e)}'
        }), 400
    
    except DoesNotExist:
        return jsonify({
            'success': False,
            'message': 'Experience not found'
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating experience: {str(e)}'
        }), 500

@experiences_bp.route('/<experience_id>', methods=['DELETE'])
@jwt_required()
def delete_experience(experience_id):
    """
    Delete a specific experience.
    ---
    Requires authentication.
    """
    current_user_id = get_jwt_identity()
    
    try:
        user = User.objects.get(id=current_user_id)
        experience = Experience.objects.get(id=experience_id)
        
        # Check if the experience belongs to the user
        if str(experience.user.id) != current_user_id:
            return jsonify({
                'success': False,
                'message': 'You do not have permission to delete this experience'
            }), 403
        
        # Delete the experience
        experience.delete()
        
        return jsonify({
            'success': True,
            'message': 'Experience deleted successfully'
        }), 200
    
    except DoesNotExist:
        return jsonify({
            'success': False,
            'message': 'Experience not found'
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting experience: {str(e)}'
        }), 500

@experiences_bp.route('/<experience_id>/verify', methods=['POST'])
@jwt_required()
def verify_experience(experience_id):
    """
    Verify a specific experience.
    ---
    Requires authentication.
    """
    current_user_id = get_jwt_identity()
    data = request.json
    
    try:
        verifier = User.objects.get(id=current_user_id)
        experience = Experience.objects.get(id=experience_id)
        
        # Verify the experience
        verification_data = data.get('verification_data', {})
        experience.verify(verifier, verification_data)
        
        return jsonify({
            'success': True,
            'message': 'Experience verified successfully',
            'experience': experience.to_json()
        }), 200
    
    except DoesNotExist:
        return jsonify({
            'success': False,
            'message': 'Experience not found'
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error verifying experience: {str(e)}'
        }), 500
