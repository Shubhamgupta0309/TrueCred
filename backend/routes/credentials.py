"""
Credential management routes for the TrueCred API.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from middleware.auth_middleware import admin_required, issuer_required
from services.credential_service import CredentialService
from utils.api_response import success_response, error_response, not_found_response, validation_error_response
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
credentials_bp = Blueprint('credentials', __name__)

@credentials_bp.route('/', methods=['GET'])
@jwt_required()
def get_credentials():
    """
    Get credentials for the current user.
    ---
    Requires authentication.
    
    Query Parameters:
      include_expired: Whether to include expired credentials (default: false)
      status: Filter by verification status (verified, unverified, all)
      type: Filter by credential type
    
    Returns:
      List of credentials
    """
    current_user_id = get_jwt_identity()
    
    # Get query parameters
    include_expired = request.args.get('include_expired', 'false').lower() == 'true'
    status = request.args.get('status')
    credential_type = request.args.get('type')
    
    # Get credentials
    credentials, error = CredentialService.get_user_credentials(
        user_id=current_user_id,
        include_expired=include_expired,
        status=status,
        credential_type=credential_type
    )
    
    if error:
        return error_response(message=error, status_code=400)
    
    # Return credentials
    return success_response(
        data=[cred.to_json() for cred in credentials],
        message=f"Retrieved {len(credentials)} credentials"
    )

@credentials_bp.route('/', methods=['POST'])
@jwt_required()
def create_credential():
    """
    Create a new credential.
    ---
    Requires authentication.
    
    Request Body:
      title: Credential title
      issuer: Organization that issued the credential
      description: Credential description (optional)
      type: Credential type (diploma, degree, certificate, badge, award, license, other)
      issue_date: Date when the credential was issued (ISO format, optional)
      expiry_date: Date when the credential expires (ISO format, optional)
      document_url: URL to the credential document (optional)
      metadata: Additional metadata (optional)
    
    Returns:
      Created credential
    """
    current_user_id = get_jwt_identity()
    data = request.json
    
    if not data:
        return validation_error_response(
            errors={"request": "No data provided"},
            message="Request body is required"
        )
    
    # Create credential
    credential, error = CredentialService.create_credential(
        user_id=current_user_id,
        data=data
    )
    
    if error:
        return validation_error_response(
            errors={"general": error},
            message="Failed to create credential"
        )
    
    # Return created credential
    return success_response(
        data=credential.to_json(),
        message="Credential created successfully",
        status_code=201
    )

@credentials_bp.route('/<credential_id>', methods=['GET'])
@jwt_required()
def get_credential(credential_id):
    """
    Get a specific credential by ID.
    ---
    Requires authentication.
    
    Path Parameters:
      credential_id: ID of the credential to retrieve
    
    Returns:
      Credential data
    """
    current_user_id = get_jwt_identity()
    
    # Get credential
    credential, error = CredentialService.get_credential_by_id(
        credential_id=credential_id,
        user_id=current_user_id
    )
    
    if error:
        return not_found_response(resource_type="Credential", resource_id=credential_id)
    
    # Return credential
    return success_response(
        data=credential.to_json(),
        message="Credential retrieved successfully"
    )

@credentials_bp.route('/<credential_id>', methods=['PUT'])
@jwt_required()
def update_credential(credential_id):
    """
    Update a specific credential.
    ---
    Requires authentication.
    
    Path Parameters:
      credential_id: ID of the credential to update
    
    Request Body:
      title: Credential title (optional)
      issuer: Organization that issued the credential (optional)
      description: Credential description (optional)
      type: Credential type (optional)
      issue_date: Date when the credential was issued (ISO format, optional)
      expiry_date: Date when the credential expires (ISO format, optional)
      document_url: URL to the credential document (optional)
      metadata: Additional metadata (optional)
    
    Returns:
      Updated credential
    """
    current_user_id = get_jwt_identity()
    data = request.json
    
    if not data:
        return validation_error_response(
            errors={"request": "No data provided"},
            message="Request body is required"
        )
    
    # Update credential
    credential, error = CredentialService.update_credential(
        credential_id=credential_id,
        user_id=current_user_id,
        data=data
    )
    
    if error:
        if "not found" in error.lower():
            return not_found_response(resource_type="Credential", resource_id=credential_id)
        return validation_error_response(
            errors={"general": error},
            message="Failed to update credential"
        )
    
    # Return updated credential
    return success_response(
        data=credential.to_json(),
        message="Credential updated successfully"
    )

@credentials_bp.route('/<credential_id>', methods=['DELETE'])
@jwt_required()
def delete_credential(credential_id):
    """
    Delete a specific credential.
    ---
    Requires authentication.
    
    Path Parameters:
      credential_id: ID of the credential to delete
    
    Returns:
      Success message
    """
    current_user_id = get_jwt_identity()
    
    # Delete credential
    success, error = CredentialService.delete_credential(
        credential_id=credential_id,
        user_id=current_user_id
    )
    
    if not success:
        if "not found" in error.lower():
            return not_found_response(resource_type="Credential", resource_id=credential_id)
        return error_response(
            message=error,
            status_code=400
        )
    
    # Return success
    return success_response(
        message="Credential deleted successfully"
    )

@credentials_bp.route('/<credential_id>/verify', methods=['POST'])
@jwt_required()
@issuer_required
def verify_credential(credential_id):
    """
    Verify a credential.
    ---
    Requires authentication and issuer role.
    
    Path Parameters:
      credential_id: ID of the credential to verify
    
    Request Body:
      verification_data: Additional verification data (optional)
    
    Returns:
      Verified credential
    """
    current_user_id = get_jwt_identity()
    data = request.json or {}
    
    # Verify credential
    credential, error = CredentialService.verify_credential(
        credential_id=credential_id,
        issuer_id=current_user_id,
        verification_data=data.get('verification_data')
    )
    
    if error:
        if "already verified" in error.lower():
            return success_response(
                data=credential.to_json(),
                message=error
            )
        if "not found" in error.lower():
            return not_found_response(resource_type="Credential", resource_id=credential_id)
        return error_response(
            message=error,
            status_code=400
        )
    
    # Return verified credential
    return success_response(
        data=credential.to_json(),
        message="Credential verified successfully"
    )

@credentials_bp.route('/verify-bulk', methods=['POST'])
@jwt_required()
@issuer_required
def verify_credentials_bulk():
    """
    Verify multiple credentials in bulk.
    ---
    Requires authentication and issuer role.
    
    Request Body:
      credential_ids: List of credential IDs to verify
      verification_data: Additional verification data (optional)
    
    Returns:
      Results of the verification process
    """
    current_user_id = get_jwt_identity()
    data = request.json
    
    if not data or 'credential_ids' not in data:
        return validation_error_response(
            errors={"credential_ids": "List of credential IDs is required"},
            message="Missing required field: credential_ids"
        )
    
    credential_ids = data.get('credential_ids', [])
    
    if not isinstance(credential_ids, list) or not credential_ids:
        return validation_error_response(
            errors={"credential_ids": "Must be a non-empty list"},
            message="Invalid credential_ids format"
        )
    
    # Verify credentials in bulk
    results, errors = CredentialService.bulk_verify_credentials(
        credential_ids=credential_ids,
        issuer_id=current_user_id,
        verification_data=data.get('verification_data')
    )
    
    # Return results
    return success_response(
        data={
            'results': results,
            'errors': errors,
            'success_count': len(results),
            'error_count': len(errors),
            'total': len(credential_ids)
        },
        message=f"Verified {len(results)} out of {len(credential_ids)} credentials"
    )

@credentials_bp.route('/public/verify/<credential_id>', methods=['GET'])
def public_verify_credential(credential_id):
    """
    Publicly verify a credential without authentication.
    ---
    Does not require authentication.
    
    Path Parameters:
      credential_id: ID of the credential to verify
    
    Returns:
      Verification result
    """
    # Get credential
    credential, error = CredentialService.get_credential_by_id(credential_id)
    
    if error:
        return not_found_response(resource_type="Credential", resource_id=credential_id)
    
    # Return verification status
    verification_info = {
        'credential_id': str(credential.id),
        'title': credential.title,
        'issuer': credential.issuer,
        'recipient': {
            'id': str(credential.user.id),
            'username': credential.user.username,
            'name': f"{credential.user.first_name} {credential.user.last_name}".strip()
        },
        'verified': credential.verified,
        'issue_date': credential.issue_date.isoformat() if credential.issue_date else None,
        'expiry_date': credential.expiry_date.isoformat() if credential.expiry_date else None,
        'expired': (credential.expiry_date and credential.expiry_date < current_app.config.get('CURRENT_TIME', datetime.utcnow())) if credential.expiry_date else False,
        'verification_timestamp': credential.verified_at.isoformat() if credential.verified_at else None,
    }
    
    return success_response(
        data=verification_info,
        message="Credential verification result"
    )
@jwt_required()
def verify_credential(credential_id):
    """
    Verify a credential.
    ---
    Requires authentication.
    """
    current_user = get_jwt_identity()
    # Placeholder for credential verification logic
    return jsonify({
        'message': 'Verify credential endpoint - to be implemented', 
        'user': current_user,
        'credential_id': credential_id
    }), 200
