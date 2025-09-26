"""
Experience management routes for the TrueCred API.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.experience_service import ExperienceService
from utils.api_response import success_response, error_response, not_found_response, validation_error_response
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
experiences_bp = Blueprint('experiences', __name__)

@experiences_bp.route('/', methods=['GET'])
@jwt_required()
def get_experiences():
    """
    Get experiences for the current user.
    ---
    Requires authentication.
    
    Query Parameters:
      type: Filter by experience type (work, education)
      current: Filter by current status (true/false)
    
    Returns:
      List of experiences
    """
    current_user_id = get_jwt_identity()
    
    # Get query parameters
    exp_type = request.args.get('type')
    current_only = request.args.get('current', 'false').lower() == 'true'
    
    # Get experiences
    experiences, error = ExperienceService.get_user_experiences(
        user_id=current_user_id,
        exp_type=exp_type,
        current_only=current_only
    )
    
    if error:
        return error_response(message=error, status_code=400)
    
    # Return experiences
    return success_response(
        data=[exp.to_json() for exp in experiences],
        message=f"Retrieved {len(experiences)} experiences"
    )

@experiences_bp.route('/', methods=['POST'])
@jwt_required()
def create_experience():
    """
    Create a new experience.
    ---
    Requires authentication.
    
    Request Body:
      type: Experience type (work, education)
      organization: Organization or institution name
      title: Job title or degree name
      description: Experience description (optional)
      start_date: Start date (ISO format)
      end_date: End date (ISO format, optional, null for current experiences)
      location: Location (optional)
      current: Whether this is a current experience (default: false)
      skills: List of skills associated with this experience (optional)
      related_credentials: List of credential IDs related to this experience (optional)
      metadata: Additional metadata (optional)
    
    Returns:
      Created experience
    """
    current_user_id = get_jwt_identity()
    data = request.json
    
    if not data:
        return validation_error_response(
            errors={"request": "No data provided"},
            message="Request body is required"
        )
    
    # Create experience
    experience, error = ExperienceService.create_experience(
        user_id=current_user_id,
        data=data
    )
    
    if error:
        return validation_error_response(
            errors={"general": error},
            message="Failed to create experience"
        )
    
    # Return created experience
    return success_response(
        data=experience.to_json(),
        message="Experience created successfully",
        status_code=201
    )

@experiences_bp.route('/<experience_id>', methods=['GET'])
@jwt_required()
def get_experience(experience_id):
    """
    Get a specific experience by ID.
    ---
    Requires authentication.
    
    Path Parameters:
      experience_id: ID of the experience to retrieve
    
    Returns:
      Experience data
    """
    current_user_id = get_jwt_identity()
    
    # Get experience
    experience, error = ExperienceService.get_experience_by_id(
        experience_id=experience_id,
        user_id=current_user_id
    )
    
    if error:
        return not_found_response(resource_type="Experience", resource_id=experience_id)
    
    # Return experience
    return success_response(
        data=experience.to_json(),
        message="Experience retrieved successfully"
    )

@experiences_bp.route('/<experience_id>', methods=['PUT'])
@jwt_required()
def update_experience(experience_id):
    """
    Update a specific experience.
    ---
    Requires authentication.
    
    Path Parameters:
      experience_id: ID of the experience to update
    
    Request Body:
      type: Experience type (work, education) (optional)
      organization: Organization or institution name (optional)
      title: Job title or degree name (optional)
      description: Experience description (optional)
      start_date: Start date (ISO format, optional)
      end_date: End date (ISO format, optional, null for current experiences)
      location: Location (optional)
      current: Whether this is a current experience (optional)
      skills: List of skills associated with this experience (optional)
      related_credentials: List of credential IDs related to this experience (optional)
      metadata: Additional metadata (optional)
    
    Returns:
      Updated experience
    """
    current_user_id = get_jwt_identity()
    data = request.json
    
    if not data:
        return validation_error_response(
            errors={"request": "No data provided"},
            message="Request body is required"
        )
    
    # Update experience
    experience, error = ExperienceService.update_experience(
        experience_id=experience_id,
        user_id=current_user_id,
        data=data
    )
    
    if error:
        if "not found" in error.lower():
            return not_found_response(resource_type="Experience", resource_id=experience_id)
        return validation_error_response(
            errors={"general": error},
            message="Failed to update experience"
        )
    
    # Return updated experience
    return success_response(
        data=experience.to_json(),
        message="Experience updated successfully"
    )

@experiences_bp.route('/<experience_id>', methods=['DELETE'])
@jwt_required()
def delete_experience(experience_id):
    """
    Delete a specific experience.
    ---
    Requires authentication.
    
    Path Parameters:
      experience_id: ID of the experience to delete
    
    Returns:
      Success message
    """
    current_user_id = get_jwt_identity()
    
    # Delete experience
    success, error = ExperienceService.delete_experience(
        experience_id=experience_id,
        user_id=current_user_id
    )
    
    if not success:
        if "not found" in error.lower():
            return not_found_response(resource_type="Experience", resource_id=experience_id)
        return error_response(
            message=error,
            status_code=400
        )
    
    # Return success
    return success_response(
        message="Experience deleted successfully"
    )

@experiences_bp.route('/<experience_id>/verify', methods=['POST'])
@jwt_required()
def verify_experience(experience_id):
    """
    Verify a specific experience.
    ---
    Requires authentication.
    
    Path Parameters:
      experience_id: ID of the experience to verify
    
    Request Body:
      verification_data: Additional verification data (optional)
    
    Returns:
      Verified experience
    """
    current_user_id = get_jwt_identity()
    data = request.json or {}
    
    # Verify experience
    experience, error = ExperienceService.verify_experience(
        experience_id=experience_id,
        verifier_id=current_user_id,
        verification_data=data.get('verification_data')
    )
    
    if error:
        if "already verified" in error.lower():
            return success_response(
                data=experience.to_json(),
                message=error
            )
        if "not found" in error.lower():
            return not_found_response(resource_type="Experience", resource_id=experience_id)
        return error_response(
            message=error,
            status_code=400
        )
    
    # Return verified experience
    return success_response(
        data=experience.to_json(),
        message="Experience verified successfully"
    )

@experiences_bp.route('/<experience_id>/reject', methods=['POST'])
@jwt_required()
def reject_experience(experience_id):
    """
    Reject a specific experience verification request.
    ---
    Requires authentication.
    
    Path Parameters:
      experience_id: ID of the experience to reject
    
    Request Body:
      reason: Reason for rejection (optional)
    
    Returns:
      Rejected experience
    """
    current_user_id = get_jwt_identity()
    data = request.json or {}
    
    # Get the rejection reason
    reason = data.get('reason', 'No reason provided')
    
    # For rejection, we'll update the experience status and add rejection reason
    from models.experience import Experience
    try:
        experience = Experience.objects.get(id=experience_id)
    except Experience.DoesNotExist:
        return not_found_response(resource_type="Experience", resource_id=experience_id)
    
    # Check if the current user is from the same organization
    from models.user import User
    try:
        user = User.objects.get(id=current_user_id)
        if user.role != 'company' or experience.organization != user.organization:
            return error_response(
                message="Only the associated company can reject this experience",
                status_code=403
            )
    except User.DoesNotExist:
        return error_response(message="User not found", status_code=404)
    
    # Update experience status
    experience.is_verified = False
    experience.pending_verification = False
    experience.verification_status = 'rejected'
    experience.rejection_reason = reason
    experience.verified_by = None
    experience.verified_at = None
    experience.save()
    
    logger.info(f"Experience {experience_id} rejected by user {current_user_id} for reason: {reason}")
    
    return success_response(
        data=experience.to_json(),
        message="Experience verification rejected"
    )

@experiences_bp.route('/<experience_id>/credentials', methods=['GET'])
@jwt_required()
def get_experience_credentials(experience_id):
    """
    Get credentials associated with an experience.
    ---
    Requires authentication.
    
    Path Parameters:
      experience_id: ID of the experience
    
    Returns:
      List of associated credentials
    """
    current_user_id = get_jwt_identity()
    
    # Get experience credentials
    credentials, error = ExperienceService.get_experience_credentials(
        experience_id=experience_id,
        user_id=current_user_id
    )
    
    if error:
        if "not found" in error.lower():
            return not_found_response(resource_type="Experience", resource_id=experience_id)
        return error_response(
            message=error,
            status_code=400
        )
    
    # Return credentials
    return success_response(
        data=[cred.to_json() for cred in credentials],
        message=f"Retrieved {len(credentials)} credentials for this experience"
    )

@experiences_bp.route('/<experience_id>/credentials', methods=['POST'])
@jwt_required()
def link_credentials_to_experience(experience_id):
    """
    Link credentials to an experience.
    ---
    Requires authentication.
    
    Path Parameters:
      experience_id: ID of the experience
    
    Request Body:
      credential_ids: List of credential IDs to link
    
    Returns:
      Updated experience with linked credentials
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
    
    # Link credentials
    experience, error = ExperienceService.link_credentials(
        experience_id=experience_id,
        user_id=current_user_id,
        credential_ids=credential_ids
    )
    
    if error:
        if "not found" in error.lower():
            return not_found_response(resource_type="Experience", resource_id=experience_id)
        return error_response(
            message=error,
            status_code=400
        )
    
    # Return updated experience
    return success_response(
        data=experience.to_json(),
        message="Credentials linked successfully"
    )

@experiences_bp.route('/<experience_id>/credentials/<credential_id>', methods=['DELETE'])
@jwt_required()
def unlink_credential_from_experience(experience_id, credential_id):
    """
    Unlink a credential from an experience.
    ---
    Requires authentication.
    
    Path Parameters:
      experience_id: ID of the experience
      credential_id: ID of the credential to unlink
    
    Returns:
      Updated experience
    """
    current_user_id = get_jwt_identity()
    
    # Unlink credential
    experience, error = ExperienceService.unlink_credential(
        experience_id=experience_id,
        user_id=current_user_id,
        credential_id=credential_id
    )
    
    if error:
        if "not found" in error.lower():
            if "experience not found" in error.lower():
                return not_found_response(resource_type="Experience", resource_id=experience_id)
            else:
                return not_found_response(resource_type="Credential", resource_id=credential_id)
        return error_response(
            message=error,
            status_code=400
        )
    
    # Return updated experience
    return success_response(
        data=experience.to_json(),
        message="Credential unlinked successfully"
    )

@experiences_bp.route('/pending', methods=['GET'])
@jwt_required()
def get_pending_experiences():
    """
    Get pending experiences for verification by the current company.
    ---
    Requires authentication and company role.
    
    Returns:
      List of experiences pending verification for the current user's company
    """
    current_user_id = get_jwt_identity()
    
    # Get current user to verify they are a company
    from models.user import User
    try:
        user = User.objects.get(id=current_user_id)
        if user.role != 'company':
            return error_response(
                message="Only companies can access pending experiences",
                status_code=403
            )
    except User.DoesNotExist:
        return error_response(
            message="User not found",
            status_code=404
        )
    
    # Get company name from user's organization field
    company_name = user.organization
    if not company_name:
        return success_response(
            data=[],
            message="No company name found for user"
        )
    
    # Query for experiences that match the company and are pending verification
    from models.experience import Experience
    pending_experiences = Experience.objects(
        organization=company_name,
        is_verified=False
    ).filter(
        __raw__={
            '$or': [
                {'pending_verification': True},
                {'verification_status': 'pending'}
            ]
        }
    ).order_by('-created_at')
    
    # Convert to JSON and include user information
    result = []
    for exp in pending_experiences:
        exp_data = exp.to_json()
        # Add formatted data for frontend
        exp_data['experienceTitle'] = exp.title
        exp_data['submissionDate'] = exp.created_at.strftime('%B %d, %Y') if exp.created_at else 'Unknown'
        
        # Add user information
        if exp.user:
            exp_data['student'] = {
                'id': str(exp.user.id),
                'name': exp.user.first_name + ' ' + (exp.user.last_name or ''),
                'email': exp.user.email,
                'truecred_id': exp.user.truecred_id
            }
            exp_data['studentName'] = exp_data['student']['name'].strip()
            # For college name, we might need to get it from somewhere else
            # For now, use organization or a placeholder
            exp_data['collegeName'] = exp.user.organization or 'Not specified'
        else:
            exp_data['student'] = None
            exp_data['studentName'] = 'Unknown Student'
            exp_data['collegeName'] = 'Unknown'
        
        # Add IPFS document URLs if available
        from services.ipfs_service import IPFSService
        ipfs_service = IPFSService()
        
        exp_data['documentUrls'] = []
        if exp.ipfs_hash:
            exp_data['documentUrls'].append({
                'name': 'Experience Document',
                'url': ipfs_service.get_gateway_url(exp.ipfs_hash)
            })
        
        # Add document hashes from document_hashes dict
        if exp.document_hashes:
            for doc_name, doc_hash in exp.document_hashes.items():
                if doc_hash:
                    exp_data['documentUrls'].append({
                        'name': doc_name,
                        'url': ipfs_service.get_gateway_url(doc_hash)
                    })
        
        result.append(exp_data)
    
    logger.info(f"Found {len(result)} pending experiences for company {company_name}")
    
    return success_response(
        data=result,
        message=f"Retrieved {len(result)} pending experiences"
    )
