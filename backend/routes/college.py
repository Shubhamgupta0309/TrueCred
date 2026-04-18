"""
College profile routes for managing college institution profiles.
"""
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.queryset.visitor import Q
from models.user import User
from models.organization_profile import OrganizationProfile
from models.credential_request import CredentialRequest
from models.credential import Credential
from models.notification import Notification
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
        logger.info(f"Getting pending requests for user: {current_user_id}")
        logger.info(f"JWT identity type: {type(current_user_id)}")
        
        user = User.objects(id=current_user_id).first()
        logger.info(f"User found: {user}")
        if user:
            logger.info(f"User role: {user.role}, User ID: {user.id}, User email: {user.email}")
            logger.info(f"User object ID type: {type(user.id)}")
        else:
            logger.warning(f"User not found with ID: {current_user_id}")
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        if user.role != 'college':
            logger.warning(f"Access denied - user role is {user.role}, not college: {current_user_id}")
            return jsonify({'success': False, 'message': 'Only college accounts can access pending requests'}), 403

        # Build issuer matching criteria even when profile is missing.
        # This keeps dashboard data visible for legacy accounts where profile isn't completed.
        allowed_issuer_ids = {str(user.id)}
        if getattr(user, 'college_id', None):
            allowed_issuer_ids.add(str(user.college_id))

        issuer_name_candidates = set()
        for val in [getattr(user, 'username', None), getattr(user, 'email', None), getattr(user, 'organization', None)]:
            if val and str(val).strip():
                issuer_name_candidates.add(str(val).strip())

        org_profile = OrganizationProfile.objects(user_id=str(user.id)).first()
        if org_profile:
            allowed_issuer_ids.add(str(org_profile.id))
            if org_profile.name:
                issuer_name_candidates.add((org_profile.name or '').strip())
            if org_profile.fullName:
                issuer_name_candidates.add((org_profile.fullName or '').strip())

        issuer_match_q = Q(issuer_id__in=list(allowed_issuer_ids))
        for candidate in issuer_name_candidates:
            if candidate:
                issuer_match_q = issuer_match_q | Q(issuer__iexact=candidate)

        requests = CredentialRequest.objects(
            issuer_match_q & Q(status__in=['pending', 'Pending'])
        ).order_by('-updated_at', '-created_at')
        
        logger.info(f"Found {len(requests)} pending requests")
        for req in requests:
            logger.info(f"Request: {req.id}, Title: {req.title}, User: {req.user_id}, Issuer: {req.issuer_id}")
            logger.info(f"Request attachments: {req.attachments}")
            logger.info(f"Request attachments type: {type(req.attachments)}")

        # Convert to JSON with additional student information
        requests_data = []
        for req in requests:
            # Get student information
            student = User.objects(id=req.user_id).first()
            student_name = "Unknown Student"
            student_email = ""
            institution_name = "Not specified"
            education_info = []
            
            if student:
                student_name = f"{student.first_name} {student.last_name}".strip() if student.first_name and student.last_name else student.username
                student_email = student.email
                
                # Get education information
                if hasattr(student, 'education') and student.education:
                    for edu in student.education:
                        education_info.append({
                            'institution': edu.institution,
                            'degree': edu.degree,
                            'field_of_study': edu.field_of_study,
                            'current': edu.current
                        })
                        # Use the first/current institution as the primary one
                        if edu.current or not institution_name or institution_name == "Not specified":
                            institution_name = edu.institution
            
            request_data = {
                'id': str(req.id),
                'user_id': req.user_id,
                'title': req.title,
                'issuer': req.issuer,
                'issuer_id': req.issuer_id,
                'type': req.type,
                'status': req.status,
                'ocr_verified': req.ocr_verified,
                'confidence_score': req.confidence_score,
                'verification_status': req.verification_status,
                'matched_template_name': req.matched_template_name,
                'ocr_extracted_data': req.ocr_extracted_data or {},
                'ocr_decision_details': req.ocr_decision_details or {},
                'manual_review_required': req.manual_review_required,
                'created_at': req.created_at.isoformat() if req.created_at else None,
                'updated_at': req.updated_at.isoformat() if req.updated_at else None,
                'attachments': req.attachments or [],  # Include attachments for document viewing
                # Additional student information
                'student_name': student_name,
                'student_email': student_email,
                'institution_name': institution_name,
                'education_info': education_info
            }
            
            logger.info(f"Final request data attachments: {request_data.get('attachments')}")
            requests_data.append(request_data)

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
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        if user.role != 'college':
            return jsonify({'success': False, 'message': 'Only college users can access this endpoint'}), 403

        # Collect possible issuer identifiers used in requests.
        allowed_issuer_ids = {str(user.id)}
        if getattr(user, 'college_id', None):
            allowed_issuer_ids.add(str(user.college_id))

        profile = OrganizationProfile.objects(user_id=str(user.id)).first()
        issuer_name_candidates = set()
        for val in [getattr(user, 'username', None), getattr(user, 'email', None), getattr(user, 'organization', None)]:
            if val and str(val).strip():
                issuer_name_candidates.add(str(val).strip())

        if profile:
            allowed_issuer_ids.add(str(profile.id))
            if profile.name:
                issuer_name_candidates.add((profile.name or '').strip())
            if profile.fullName:
                issuer_name_candidates.add((profile.fullName or '').strip())

        # History = all finalized or verified requests handled by this issuer/college.
        # Includes legacy records where issuer_id may be empty but issuer text matches profile names.
        issuer_match_q = Q(issuer_id__in=list(allowed_issuer_ids))
        for candidate in issuer_name_candidates:
            if candidate:
                issuer_match_q = issuer_match_q | Q(issuer__iexact=candidate)

        finalized_or_verified_q = (
            Q(status__in=['issued', 'approved', 'rejected', 'verified']) |
            Q(verification_status='verified')
        )

        requests = CredentialRequest.objects(
            issuer_match_q & finalized_or_verified_q
        ).order_by('-updated_at', '-created_at').limit(200)

        history = []
        for req in requests:
            student = User.objects(id=req.user_id).first()
            student_name = (
                f"{(student.first_name or '').strip()} {(student.last_name or '').strip()}".strip()
                if student else 'Unknown Student'
            )
            if not student_name:
                student_name = student.username if student else 'Unknown Student'

            action_dt = req.updated_at or req.created_at
            display_status = (req.status or '').strip()
            if not display_status and req.verification_status:
                display_status = req.verification_status
            if req.verification_status == 'verified' and display_status.lower() not in ['issued', 'approved', 'verified']:
                display_status = 'verified'

            history.append({
                'id': str(req.id),
                'studentName': student_name,
                'studentEmail': student.email if student else None,
                'studentTruecredId': getattr(student, 'truecred_id', None) if student else None,
                'credentialTitle': req.title,
                'issuer': req.issuer,
                'verification_status': req.verification_status,
                'status': (display_status or 'verified').capitalize(),
                'actionDate': action_dt.strftime('%b %d, %Y') if action_dt else None,
                'created_at': req.created_at.isoformat() if req.created_at else None,
                'updated_at': action_dt.isoformat() if action_dt else None,
                'blockchain_tx_hash': getattr(req, 'blockchain_tx_hash', None),
            })

        return jsonify({'success': True, 'history': history}), 200
    except Exception as e:
        logger.error(f'Error getting verification history: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500


@college_bp.route('/verification-history/<request_id>', methods=['DELETE'])
@jwt_required()
def delete_verification_history_item(request_id):
    """
    Delete a college verification-history item.
    This removes the underlying request and any linked issued credential(s) so student view is updated too.
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        if user.role != 'college':
            return jsonify({'success': False, 'message': 'Only college users can access this endpoint'}), 403

        allowed_issuer_ids = {str(user.id)}
        if getattr(user, 'college_id', None):
            allowed_issuer_ids.add(str(user.college_id))

        profile = OrganizationProfile.objects(user_id=str(user.id)).first()
        issuer_name_candidates = set()
        for val in [getattr(user, 'username', None), getattr(user, 'email', None), getattr(user, 'organization', None)]:
            if val and str(val).strip():
                issuer_name_candidates.add(str(val).strip())

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

        req = CredentialRequest.objects(Q(id=request_id) & issuer_match_q).first()
        if not req:
            return jsonify({'success': False, 'message': 'History item not found or access denied'}), 404

        credential_ids_to_delete = set()

        # Primary linkage: credential metadata contains request_id
        student = User.objects(id=req.user_id).first()
        if student:
            for cred in Credential.objects(user=student, metadata__request_id=str(req.id)):
                credential_ids_to_delete.add(str(cred.id))

        # Secondary linkage via notifications that carry request_id -> credential_id mapping
        for note in Notification.objects(data__request_id=str(req.id)):
            try:
                credential_id = (note.data or {}).get('credential_id')
                if credential_id:
                    credential_ids_to_delete.add(str(credential_id))
            except Exception:
                continue

        # Legacy fallback: if request was issued, best-effort match by user/title/issuer
        if not credential_ids_to_delete and student and str(req.status or '').lower() in ['issued', 'approved', 'verified']:
            fallback_cred = Credential.objects(user=student, title=req.title, issuer=req.issuer).order_by('-created_at').first()
            if fallback_cred:
                credential_ids_to_delete.add(str(fallback_cred.id))

        deleted_credentials = 0
        if credential_ids_to_delete:
            deleted_credentials = Credential.objects(id__in=list(credential_ids_to_delete)).delete()

        # Remove notifications tied to this request or deleted credentials.
        Notification.objects(data__request_id=str(req.id)).delete()
        if credential_ids_to_delete:
            Notification.objects(data__credential_id__in=list(credential_ids_to_delete)).delete()

        req.delete()

        return jsonify({
            'success': True,
            'message': 'History item deleted successfully',
            'deleted_request_id': str(request_id),
            'deleted_credentials': int(deleted_credentials)
        }), 200
    except Exception as e:
        logger.exception(f'Error deleting verification history item {request_id}: {str(e)}')
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500
