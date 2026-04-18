"""
Notifications routes for the TrueCred API.

This module defines the notifications endpoints for the TrueCred API.
"""
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.api_response import success_response, error_response
from models.user import User
from models.notification import Notification
from models.organization_profile import OrganizationProfile
from models.credential_request import CredentialRequest
from models.experience import Experience
from mongoengine.queryset.visitor import Q
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Notifications blueprint
notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/')
@jwt_required()
def get_notifications():
    """
    Get notifications for the current user.
    
    Returns:
        JSON response with the user's notifications
    """
    # Get the current user ID from the JWT and resolve to canonical user id.
    current_user_identity = get_jwt_identity()
    if isinstance(current_user_identity, dict):
        current_user_identity = (
            current_user_identity.get('user_id') or
            current_user_identity.get('id') or
            current_user_identity.get('_id') or
            current_user_identity.get('sub') or
            current_user_identity.get('username')
        )
    current_user_identity = str(current_user_identity) if current_user_identity is not None else None
    
    try:
        # Ensure the user exists and resolve by id/username/email.
        user = None
        if current_user_identity:
            user = User.objects(id=current_user_identity).first()
            if not user:
                user = (
                    User.objects(username=current_user_identity).first() or
                    User.objects(email=current_user_identity).first()
                )
        if not user:
            return error_response(
                message="User not found",
                status_code=404,
                error_code="user_not_found"
            )

        current_user_id = str(user.id)

        # Primary source: Notification model collection.
        notifications = []
        try:
            docs = Notification.objects(user_id=str(current_user_id)).order_by('-created_at').limit(50)
            notifications = [doc.to_json() for doc in docs]
        except Exception as e:
            logger.exception('Failed to fetch notifications via Notification model: %s', e)

        # Backward-compatible fallback for deployments that still use a raw pymongo collection.
        if not notifications:
            try:
                if hasattr(current_app, 'db') and current_app.db is not None:
                    query = {'user_id': str(current_user_id)}
                    query_options = [query]
                    try:
                        from bson import ObjectId
                        if ObjectId.is_valid(str(current_user_id)):
                            query_options.append({'user_id': ObjectId(str(current_user_id))})
                    except Exception:
                        pass

                    cursor = current_app.db.notifications.find({'$or': query_options}).sort('created_at', -1).limit(50)
                    raw_docs = list(cursor)
                    for n in raw_docs:
                        n['_id'] = str(n.get('_id'))
                        if 'created_at' in n and hasattr(n['created_at'], 'isoformat'):
                            n['created_at'] = n['created_at'].isoformat()
                    notifications = raw_docs
            except Exception as e:
                logger.exception('Fallback pymongo notifications fetch failed: %s', e)

        # Final fallback for college dashboards: synthesize recent pending-request notifications
        # when no notification records exist yet for older data.
        if not notifications and user.role == 'college':
            try:
                allowed_issuer_ids = {str(user.id)}
                if getattr(user, 'college_id', None):
                    allowed_issuer_ids.add(str(user.college_id))

                issuer_name_candidates = set()
                for val in [getattr(user, 'username', None), getattr(user, 'email', None), getattr(user, 'organization', None)]:
                    if val and str(val).strip():
                        issuer_name_candidates.add(str(val).strip())

                profile = OrganizationProfile.objects(user_id=str(user.id)).first()
                if profile:
                    allowed_issuer_ids.add(str(profile.id))
                    if profile.name:
                        issuer_name_candidates.add((profile.name or '').strip())
                    if profile.fullName:
                        issuer_name_candidates.add((profile.fullName or '').strip())

                issuer_match_q = Q(issuer_id__in=list(allowed_issuer_ids))
                for candidate in issuer_name_candidates:
                    if candidate:
                        issuer_match_q = issuer_match_q | Q(issuer__iexact=candidate)

                pending = CredentialRequest.objects(
                    issuer_match_q & Q(status__in=['pending', 'Pending'])
                ).order_by('-updated_at', '-created_at').limit(20)

                synthetic = []
                for req in pending:
                    synthetic.append({
                        'id': f"pending-{str(req.id)}",
                        'user_id': current_user_id,
                        'type': 'verification_request',
                        'title': 'New verification request',
                        'message': f"'{req.title}' is pending review.",
                        'data': {'request_id': str(req.id)},
                        'created_at': (req.updated_at or req.created_at).isoformat() if (req.updated_at or req.created_at) else None,
                        'read_at': None
                    })

                notifications = synthetic
            except Exception as e:
                logger.exception('Failed to build synthetic college notifications: %s', e)

        # Final fallback for company dashboards: synthesize from pending experience requests.
        if not notifications and user.role == 'company':
            try:
                org_name = (user.organization or '').strip()
                if org_name:
                    pending_experiences = Experience.objects(
                        organization=org_name,
                        verification_status='pending'
                    ).order_by('-updated_at', '-created_at').limit(20)
                else:
                    pending_experiences = Experience.objects(
                        verification_status='pending'
                    ).order_by('-updated_at', '-created_at').limit(20)

                synthetic = []
                for exp in pending_experiences:
                    student_name = 'Student'
                    try:
                        if exp.user:
                            student_name = (
                                f"{(exp.user.first_name or '').strip()} {(exp.user.last_name or '').strip()}".strip()
                                or exp.user.username
                            )
                    except Exception:
                        pass

                    synthetic.append({
                        'id': f"pending-exp-{str(exp.id)}",
                        'user_id': current_user_id,
                        'type': 'verification_request',
                        'title': 'New verification request',
                        'message': f"'{exp.title}' from {student_name} is pending review.",
                        'data': {'experience_id': str(exp.id)},
                        'created_at': (exp.updated_at or exp.created_at).isoformat() if (exp.updated_at or exp.created_at) else None,
                        'read_at': None
                    })

                notifications = synthetic
            except Exception as e:
                logger.exception('Failed to build synthetic company notifications: %s', e)

        return success_response(
            data={"notifications": notifications},
            message="Notifications retrieved successfully"
        )
    except Exception as e:
        logger.exception(f"Error getting notifications: {str(e)}")
        return error_response(
            message="Failed to retrieve notifications",
            status_code=500,
            error_code="notifications_fetch_error"
        )
