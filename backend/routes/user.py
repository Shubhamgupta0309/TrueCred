"""
User profile routes providing /api/user/profile endpoints that return raw user JSON.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import AuthService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__, url_prefix='/api/user')


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user, error = AuthService.get_user_by_id(current_user_id)
    if error:
        return jsonify({'error': error}), 404
    # Return the bare user object as expected by the frontend
    return jsonify(user.to_json()), 200


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    data = request.json or {}
    user, error = AuthService.get_user_by_id(current_user_id)
    if error:
        return jsonify({'error': error}), 404
    # Only allow a subset of fields to be updated
    updatable_fields = ['first_name', 'last_name', 'email']
    changes = {}
    for f in updatable_fields:
        if f in data and data[f] is not None:
            setattr(user, f, data[f])
            changes[f] = data[f]
    if changes:
        user.updated_at = datetime.utcnow()
        user.save()
    return jsonify(user.to_json()), 200
