"""
Verification routes for the TrueCred application.
"""
from flask import Blueprint, request, jsonify, g
from mongoengine.errors import DoesNotExist, ValidationError

from services.verification_service import VerificationService
from middleware.auth_middleware import login_required, role_required
from utils.response import success_response, error_response

verification_bp = Blueprint('verification', __name__, url_prefix='/api/verification')

@verification_bp.route('/experience/request/<experience_id>', methods=['POST'])
@login_required
def request_experience_verification(experience_id):
    """
    Request verification for an experience.
    
    Args:
        experience_id: ID of the experience to verify
        
    Returns:
        JSON response with updated experience
    """
    try:
        user_id = g.user_id
        verification_data = request.json or {}
        
        experience = VerificationService.request_experience_verification(
            experience_id=experience_id,
            user_id=user_id,
            verification_data=verification_data
        )
        
        return success_response(
            message="Verification request submitted successfully",
            data=experience.to_json()
        )
    except DoesNotExist as e:
        return error_response(message=str(e), status_code=404)
    except ValidationError as e:
        return error_response(message=str(e), status_code=400)
    except ValueError as e:
        return error_response(message=str(e), status_code=403)
    except Exception as e:
        return error_response(message=f"Error requesting verification: {str(e)}", status_code=500)

@verification_bp.route('/experience/verify/<experience_id>', methods=['POST'])
@login_required
@role_required(['verifier', 'admin'])
def verify_experience(experience_id):
    """
    Verify an experience.
    
    Args:
        experience_id: ID of the experience to verify
        
    Returns:
        JSON response with updated experience
    """
    try:
        verifier_id = g.user_id
        verification_data = request.json or {}
        
        experience = VerificationService.verify_experience(
            experience_id=experience_id,
            verifier_id=verifier_id,
            verification_data=verification_data
        )
        
        return success_response(
            message="Experience verified successfully",
            data=experience.to_json()
        )
    except DoesNotExist as e:
        return error_response(message=str(e), status_code=404)
    except ValidationError as e:
        return error_response(message=str(e), status_code=400)
    except ValueError as e:
        return error_response(message=str(e), status_code=403)
    except Exception as e:
        return error_response(message=f"Error verifying experience: {str(e)}", status_code=500)

@verification_bp.route('/experience/reject/<experience_id>', methods=['POST'])
@login_required
@role_required(['verifier', 'admin'])
def reject_experience_verification(experience_id):
    """
    Reject verification for an experience.
    
    Args:
        experience_id: ID of the experience to reject
        
    Body:
        reason: Reason for rejection
        verification_data: Optional verification data
        
    Returns:
        JSON response with updated experience
    """
    try:
        verifier_id = g.user_id
        data = request.json or {}
        
        # Require reason for rejection
        if 'reason' not in data or not data['reason']:
            return error_response(message="Reason for rejection is required", status_code=400)
        
        reason = data['reason']
        verification_data = data.get('verification_data', {})
        
        experience = VerificationService.reject_experience_verification(
            experience_id=experience_id,
            verifier_id=verifier_id,
            reason=reason,
            verification_data=verification_data
        )
        
        return success_response(
            message="Experience verification rejected",
            data=experience.to_json()
        )
    except DoesNotExist as e:
        return error_response(message=str(e), status_code=404)
    except ValidationError as e:
        return error_response(message=str(e), status_code=400)
    except ValueError as e:
        return error_response(message=str(e), status_code=403)
    except Exception as e:
        return error_response(message=f"Error rejecting experience verification: {str(e)}", status_code=500)

@verification_bp.route('/credential/request/<credential_id>', methods=['POST'])
@login_required
def request_credential_verification(credential_id):
    """
    Request verification for a credential.
    
    Args:
        credential_id: ID of the credential to verify
        
    Returns:
        JSON response with updated credential
    """
    try:
        user_id = g.user_id
        verification_data = request.json or {}
        
        credential = VerificationService.request_credential_verification(
            credential_id=credential_id,
            user_id=user_id,
            verification_data=verification_data
        )
        
        return success_response(
            message="Verification request submitted successfully",
            data=credential.to_json()
        )
    except DoesNotExist as e:
        return error_response(message=str(e), status_code=404)
    except ValidationError as e:
        return error_response(message=str(e), status_code=400)
    except ValueError as e:
        return error_response(message=str(e), status_code=403)
    except Exception as e:
        return error_response(message=f"Error requesting verification: {str(e)}", status_code=500)

@verification_bp.route('/credential/verify/<credential_id>', methods=['POST'])
@login_required
@role_required(['verifier', 'admin'])
def verify_credential(credential_id):
    """
    Verify a credential.
    
    Args:
        credential_id: ID of the credential to verify
        
    Returns:
        JSON response with updated credential
    """
    try:
        verifier_id = g.user_id
        verification_data = request.json or {}
        
        credential = VerificationService.verify_credential(
            credential_id=credential_id,
            verifier_id=verifier_id,
            verification_data=verification_data
        )
        
        return success_response(
            message="Credential verified successfully",
            data=credential.to_json()
        )
    except DoesNotExist as e:
        return error_response(message=str(e), status_code=404)
    except ValidationError as e:
        return error_response(message=str(e), status_code=400)
    except ValueError as e:
        return error_response(message=str(e), status_code=403)
    except Exception as e:
        return error_response(message=f"Error verifying credential: {str(e)}", status_code=500)

@verification_bp.route('/credential/reject/<credential_id>', methods=['POST'])
@login_required
@role_required(['verifier', 'admin'])
def reject_credential_verification(credential_id):
    """
    Reject verification for a credential.
    
    Args:
        credential_id: ID of the credential to reject
        
    Body:
        reason: Reason for rejection
        verification_data: Optional verification data
        
    Returns:
        JSON response with updated credential
    """
    try:
        verifier_id = g.user_id
        data = request.json or {}
        
        # Require reason for rejection
        if 'reason' not in data or not data['reason']:
            return error_response(message="Reason for rejection is required", status_code=400)
        
        reason = data['reason']
        verification_data = data.get('verification_data', {})
        
        credential = VerificationService.reject_credential_verification(
            credential_id=credential_id,
            verifier_id=verifier_id,
            reason=reason,
            verification_data=verification_data
        )
        
        return success_response(
            message="Credential verification rejected",
            data=credential.to_json()
        )
    except DoesNotExist as e:
        return error_response(message=str(e), status_code=404)
    except ValidationError as e:
        return error_response(message=str(e), status_code=400)
    except ValueError as e:
        return error_response(message=str(e), status_code=403)
    except Exception as e:
        return error_response(message=f"Error rejecting credential verification: {str(e)}", status_code=500)

@verification_bp.route('/pending', methods=['GET'])
@login_required
@role_required(['verifier', 'admin'])
def get_pending_verifications():
    """
    Get all pending verifications.
    
    Query parameters:
        type: Optional type of verification ('experience' or 'credential')
        user_id: Optional user ID to filter by
        
    Returns:
        JSON response with pending verifications
    """
    try:
        verification_type = request.args.get('type')
        user_id = request.args.get('user_id')
        
        results = VerificationService.get_pending_verifications(
            user_id=user_id,
            verification_type=verification_type
        )
        
        return success_response(
            message="Pending verifications retrieved successfully",
            data=results
        )
    except Exception as e:
        return error_response(message=f"Error getting pending verifications: {str(e)}", status_code=500)

@verification_bp.route('/link/<credential_id>/experience/<experience_id>', methods=['POST'])
@login_required
def link_credential_to_experience(credential_id, experience_id):
    """
    Link a credential to an experience.
    
    Args:
        credential_id: ID of the credential to link
        experience_id: ID of the experience to link to
        
    Returns:
        JSON response with updated credential
    """
    try:
        user_id = g.user_id
        
        credential = VerificationService.link_credential_to_experience(
            credential_id=credential_id,
            experience_id=experience_id,
            user_id=user_id
        )
        
        return success_response(
            message="Credential linked to experience successfully",
            data=credential.to_json()
        )
    except DoesNotExist as e:
        return error_response(message=str(e), status_code=404)
    except ValueError as e:
        return error_response(message=str(e), status_code=403)
    except Exception as e:
        return error_response(message=f"Error linking credential to experience: {str(e)}", status_code=500)

@verification_bp.route('/unlink/<credential_id>/experience/<experience_id>', methods=['POST'])
@login_required
def unlink_credential_from_experience(credential_id, experience_id):
    """
    Unlink a credential from an experience.
    
    Args:
        credential_id: ID of the credential to unlink
        experience_id: ID of the experience to unlink from
        
    Returns:
        JSON response with updated credential
    """
    try:
        user_id = g.user_id
        
        credential = VerificationService.unlink_credential_from_experience(
            credential_id=credential_id,
            experience_id=experience_id,
            user_id=user_id
        )
        
        return success_response(
            message="Credential unlinked from experience successfully",
            data=credential.to_json()
        )
    except DoesNotExist as e:
        return error_response(message=str(e), status_code=404)
    except ValueError as e:
        return error_response(message=str(e), status_code=403)
    except Exception as e:
        return error_response(message=f"Error unlinking credential from experience: {str(e)}", status_code=500)
