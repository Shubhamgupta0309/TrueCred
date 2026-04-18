"""OCR-based certificate verification route."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.template_matching_service import template_matching_service
from models.credential_request import CredentialRequest
from models.notification import Notification
from models.user import User
from utils.api_response import success_response, error_response
import logging

logger = logging.getLogger(__name__)

ocr_verification_bp = Blueprint('ocr_verification', __name__)


@ocr_verification_bp.route('/verify-credential-ocr', methods=['POST'])
@jwt_required()
def verify_credential_with_ocr():
    """
    Verify a credential using OCR against stored templates.
    
    Expected form data:
    - credential_file: Certificate image file
    - organization_id: Organization ID to match against
    - template_type: Optional template type filter
    - template_title: Optional template title for pre-filtering by template name
    - credential_request_id: Optional - if this is for an existing request
    """
    try:
        current_user_id = get_jwt_identity()
        request_update = {
            'linked': False,
            'updated': False,
            'credential_request_id': None,
            'error': None
        }
        
        # Check for file
        if 'credential_file' not in request.files:
            return error_response('No credential file provided', 400)
        
        file = request.files['credential_file']
        if file.filename == '':
            return error_response('No file selected', 400)
        
        # Get parameters
        organization_id = request.form.get('organization_id')
        template_type = request.form.get('template_type')
        template_title = request.form.get('template_title')
        credential_request_id = request.form.get('credential_request_id')
        request_update['credential_request_id'] = credential_request_id
        
        if not organization_id:
            return error_response('organization_id is required', 400)
        
        # Read file data
        file_data = file.read()
        
        # Perform OCR verification
        verification_result = template_matching_service.verify_certificate_against_templates(
            image_data=file_data,
            organization_id=organization_id,
            template_type=template_type,
            template_title=template_title
        )
        
        if not verification_result['success']:
            # Persist failure details if request id is provided, so UI can show exact reason.
            if credential_request_id:
                try:
                    cred_request = CredentialRequest.objects(id=credential_request_id).first()
                    if cred_request and cred_request.user_id == current_user_id:
                        cred_request.ocr_verified = False
                        cred_request.confidence_score = 0
                        cred_request.verification_status = verification_result.get('verification_status', 'failed')
                        cred_request.manual_review_required = True
                        cred_request.ocr_decision_details = {
                            'decision_reason': verification_result.get('error', 'OCR verification failed'),
                            'matching_details': verification_result.get('details', {}),
                            'template_title_filter': template_title,
                            'thresholds': {}
                        }
                        cred_request.save()
                except Exception as update_error:
                    logger.error(f"Failed to persist OCR failure details: {str(update_error)}")

            return error_response(
                verification_result.get('error', 'Verification failed'),
                500
            )
        
        # Update credential request if provided
        if credential_request_id:
            request_update['linked'] = True
            try:
                cred_request = CredentialRequest.objects(id=credential_request_id).first()
                if cred_request and cred_request.user_id == current_user_id:
                    # Update with OCR results
                    cred_request.ocr_verified = True
                    cred_request.confidence_score = verification_result['confidence_score']
                    cred_request.verification_status = verification_result['verification_status']
                    cred_request.matched_template_id = verification_result.get('matched_template_id')
                    cred_request.matched_template_name = verification_result.get('matched_template_name')
                    cred_request.ocr_extracted_data = verification_result.get('key_fields', {})
                    cred_request.ocr_decision_details = {
                        'decision_reason': verification_result.get('decision_reason'),
                        'matching_details': verification_result.get('matching_details', {}),
                        'template_title_filter': verification_result.get('template_title_filter'),
                        'thresholds': verification_result.get('thresholds', {})
                    }
                    cred_request.manual_review_required = (
                        verification_result['verification_status'] == 'pending_review'
                    )
                    
                    # Keep request status aligned with OCR decision for clearer UI behavior.
                    if verification_result['verification_status'] == 'verified':
                        cred_request.status = 'issued'
                        cred_request.manual_review_required = False
                    elif verification_result['verification_status'] == 'pending_review':
                        cred_request.status = 'pending'
                    elif verification_result['verification_status'] == 'rejected':
                        cred_request.status = 'rejected'
                    
                    # Set issuer_id so college dashboard can find approved credentials
                    cred_request.issuer_id = organization_id
                    
                    cred_request.save()
                    request_update['updated'] = True

                    # Notify the user about the OCR decision so the dashboard stays in sync.
                    notification_map = {
                        'verified': {
                            'type': 'credential_approved',
                            'title': 'Credential approved',
                            'message': f"Your credential request '{cred_request.title}' was approved.",
                        },
                        'pending_review': {
                            'type': 'credential_review',
                            'title': 'Credential needs review',
                            'message': f"Your credential request '{cred_request.title}' needs manual review.",
                        },
                        'rejected': {
                            'type': 'credential_rejected',
                            'title': 'Credential rejected',
                            'message': f"Your credential request '{cred_request.title}' was rejected.",
                        },
                    }
                    notification_payload = notification_map.get(verification_result['verification_status'])
                    if notification_payload:
                        Notification.create_notification(
                            user_id=cred_request.user_id,
                            notification_type=notification_payload['type'],
                            title=notification_payload['title'],
                            message=notification_payload['message'],
                            data={
                                'request_id': str(cred_request.id),
                                'verification_status': verification_result['verification_status'],
                                'confidence_score': verification_result.get('confidence_score', 0),
                            }
                        )
                    
                    logger.info(
                        f"Updated credential request {credential_request_id} with OCR results. "
                        f"Confidence: {verification_result['confidence_score']}%"
                    )
                else:
                    request_update['error'] = 'Credential request not found or not owned by current user'
            except Exception as e:
                logger.error(f"Failed to update credential request: {str(e)}")
                request_update['error'] = str(e)
        
        # Return verification results
        return success_response({
            'verification_status': verification_result['verification_status'],
            'confidence_score': verification_result['confidence_score'],
            'matched_template': verification_result.get('matched_template_name'),
            'extracted_data': verification_result.get('key_fields'),
            'matching_details': verification_result.get('matching_details'),
            'decision_reason': verification_result.get('decision_reason'),
            'template_title_filter': verification_result.get('template_title_filter'),
            'thresholds': verification_result.get('thresholds'),
            'request_update': request_update,
            'message': _get_status_message(verification_result['verification_status'])
        })
        
    except Exception as e:
        logger.error(f"OCR verification error: {str(e)}")
        return error_response(str(e), 500)


def _get_status_message(status):
    """Get user-friendly message based on verification status."""
    messages = {
        'verified': 'Certificate verified successfully! High confidence match.',
        'pending_review': 'Certificate submitted for manual review. Moderate confidence.',
        'rejected': 'Certificate verification failed. Low confidence match.',
        'no_template': 'No matching template found for this organization.',
        'failed': 'Verification failed due to technical error.',
        'error': 'An error occurred during verification.'
    }
    return messages.get(status, 'Unknown verification status')
