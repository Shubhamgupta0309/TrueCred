"""Routes for certificate template management."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.template_matching_service import template_matching_service
from services.ipfs_service import IPFSService
from models.user import User
from models.organization_profile import OrganizationProfile
from models.certificate_template import CertificateTemplate
from utils.api_response import success_response, error_response
import logging
import hashlib
from datetime import datetime
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

template_management_bp = Blueprint('template_management', __name__)
ipfs_service = IPFSService()
MAX_DAILY_TEMPLATES_PER_ORG = 20


@template_management_bp.route('/upload', methods=['OPTIONS'])
@template_management_bp.route('/organization/<organization_id>', methods=['OPTIONS'])
@template_management_bp.route('/<template_id>', methods=['OPTIONS'])
@template_management_bp.route('/<template_id>/deactivate', methods=['OPTIONS'])
@template_management_bp.route('/<template_id>/statistics', methods=['OPTIONS'])
def template_options(organization_id=None, template_id=None):
    """Handle CORS preflight for template routes."""
    return '', 200


@template_management_bp.route('/upload', methods=['POST'])
@template_management_bp.route('/templates/upload', methods=['POST'])
@jwt_required()
def upload_template():
    """
    Upload a new certificate template for an organization.
    
    Expected form data:
    - template_file: Image file (PNG, JPG)
    - template_name: Name for the template
    - template_type: Type (degree, internship, work_experience, etc.)
    - organization_id: Organization ID
    - organization_name: Organization name
    - organization_type: 'college' or 'company'
    - required_fields: JSON array of required fields
    - optional_fields: JSON array of optional fields
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Verify user has permission (must be from the organization)
        user = User.objects(id=current_user_id).first()
        if not user:
            return error_response('User not found', 404)
        
        # Get form data
        if 'template_file' not in request.files:
            return error_response('No template file provided', 400)
        
        file = request.files['template_file']
        if file.filename == '':
            return error_response('No file selected', 400)
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'pdf'}
        if not file.filename.lower().endswith(tuple(allowed_extensions)):
            return error_response('Invalid file type. Allowed: PNG, JPG, JPEG, PDF', 400)
        
        # Get other parameters
        template_name = request.form.get('template_name')
        template_type = request.form.get('template_type')
        organization_id = request.form.get('organization_id')
        organization_name = request.form.get('organization_name')
        organization_type = request.form.get('organization_type')
        
        if not all([template_name, template_type, organization_id, organization_name, organization_type]):
            return error_response('Missing required fields', 400)
        
        # Verify user belongs to this organization
        if organization_type not in ('college', 'company'):
            return error_response('Invalid organization_type. Use college or company', 400)

        if user.role != organization_type:
            return error_response('Unauthorized: Role does not match organization type', 403)

        user_id = str(user.id)
        user_college_id = str(getattr(user, 'college_id', '')) if getattr(user, 'college_id', None) else ''
        user_company_id = str(getattr(user, 'company_id', '')) if getattr(user, 'company_id', None) else ''

        # Accept direct ownership by user id or explicit organization ids if present
        allowed_org_ids = {user_id}
        if user_college_id:
            allowed_org_ids.add(user_college_id)
        if user_company_id:
            allowed_org_ids.add(user_company_id)

        # Also accept linked organization profile id for this user
        profile = OrganizationProfile.objects(user_id=user_id).first()
        if profile:
            allowed_org_ids.add(str(profile.id))

        if str(organization_id) not in allowed_org_ids:
            return error_response('Unauthorized: You do not belong to this organization', 403)

        # Canonicalize to organization profile id when available so student request matching is consistent.
        canonical_org_id = str(profile.id) if profile else str(organization_id)
        
        # Read file data
        file_data = file.read()
        file_hash = hashlib.sha256(file_data).hexdigest()

        # Guardrail 1: prevent duplicate template uploads by file hash.
        duplicate_by_hash = CertificateTemplate.objects(
            organization_id=canonical_org_id,
            file_hash=file_hash,
            is_active=True
        ).first()
        if duplicate_by_hash:
            return error_response('Duplicate template: this file is already uploaded for this organization', 409)

        # Guardrail 2: prevent active duplicate template names per type.
        duplicate_by_name = CertificateTemplate.objects(
            organization_id=canonical_org_id,
            template_name=template_name,
            template_type=template_type,
            is_active=True
        ).first()
        if duplicate_by_name:
            return error_response('Duplicate template: same template name and type already exists', 409)

        # Guardrail 3: daily upload cap per organization.
        now_utc = datetime.utcnow()
        day_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        uploads_today = CertificateTemplate.objects(
            organization_id=canonical_org_id,
            created_at__gte=day_start
        ).count()
        if uploads_today >= MAX_DAILY_TEMPLATES_PER_ORG:
            return error_response(
                f'Daily upload limit reached ({MAX_DAILY_TEMPLATES_PER_ORG} templates per day)',
                429
            )
        
        # Upload to IPFS
        ipfs_result = ipfs_service.add_file(file_data, secure_filename(file.filename))
        if not ipfs_result or ipfs_result.get('error') or not ipfs_result.get('Hash'):
            return error_response('Failed to upload to IPFS', 500)

        file_url = ipfs_service.get_gateway_url(ipfs_result['Hash'])
        
        # Get optional fields
        import json
        required_fields = json.loads(request.form.get('required_fields', '[]'))
        optional_fields = json.loads(request.form.get('optional_fields', '[]'))
        
        # Process template
        result = template_matching_service.process_and_store_template(
            image_data=file_data,
            organization_id=canonical_org_id,
            organization_name=organization_name,
            organization_type=organization_type,
            template_name=template_name,
            template_type=template_type,
            file_url=file_url,
            file_hash=file_hash,
            uploaded_by=current_user_id,
            required_fields=required_fields,
            optional_fields=optional_fields
        )
        
        if not result['success']:
            return error_response(result.get('error', 'Template processing failed'), 500)
        
        logger.info(f"Template uploaded: {template_name} by user {current_user_id}")
        
        return success_response({
            'message': 'Template uploaded successfully',
            'template_id': result['template_id'],
            'confidence': result['confidence'],
            'key_fields': result['key_fields']
        })
        
    except Exception as e:
        logger.error(f"Template upload error: {str(e)}")
        return error_response(str(e), 500)


@template_management_bp.route('/organization/<organization_id>', methods=['GET'])
@template_management_bp.route('/templates/organization/<organization_id>', methods=['GET'])
@jwt_required()
def get_organization_templates(organization_id):
    """Get all templates for an organization."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get templates
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        templates = template_matching_service.get_templates_by_organization(
            organization_id,
            include_inactive
        )
        
        return success_response({
            'templates': templates,
            'count': len(templates)
        })
        
    except Exception as e:
        logger.error(f"Get templates error: {str(e)}")
        return error_response(str(e), 500)


@template_management_bp.route('/<template_id>', methods=['GET'])
@template_management_bp.route('/templates/<template_id>', methods=['GET'])
@jwt_required()
def get_template(template_id):
    """Get a specific template by ID."""
    try:
        from models.certificate_template import CertificateTemplate
        
        template = CertificateTemplate.objects(id=template_id).first()
        if not template:
            return error_response('Template not found', 404)
        
        return success_response(template.to_json())
        
    except Exception as e:
        logger.error(f"Get template error: {str(e)}")
        return error_response(str(e), 500)


@template_management_bp.route('/<template_id>/deactivate', methods=['POST'])
@template_management_bp.route('/templates/<template_id>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_template(template_id):
    """Deactivate a template."""
    try:
        current_user_id = get_jwt_identity()
        
        # Verify user has permission
        from models.certificate_template import CertificateTemplate
        template = CertificateTemplate.objects(id=template_id).first()
        
        if not template:
            return error_response('Template not found', 404)
        
        # Verify user belongs to organization
        user = User.objects(id=current_user_id).first()
        if not user or user.role != template.organization_type:
            return error_response('Unauthorized', 403)

        user_id = str(user.id)
        user_college_id = str(getattr(user, 'college_id', '')) if getattr(user, 'college_id', None) else ''
        user_company_id = str(getattr(user, 'company_id', '')) if getattr(user, 'company_id', None) else ''
        allowed_org_ids = {user_id}
        if user_college_id:
            allowed_org_ids.add(user_college_id)
        if user_company_id:
            allowed_org_ids.add(user_company_id)

        profile = OrganizationProfile.objects(user_id=user_id).first()
        if profile:
            allowed_org_ids.add(str(profile.id))

        if str(template.organization_id) not in allowed_org_ids:
            return error_response('Unauthorized', 403)
        
        # Deactivate
        success = template_matching_service.deactivate_template(template_id)
        
        if success:
            return success_response({'message': 'Template deactivated successfully'})
        else:
            return error_response('Failed to deactivate template', 500)
        
    except Exception as e:
        logger.error(f"Deactivate template error: {str(e)}")
        return error_response(str(e), 500)


@template_management_bp.route('/<template_id>/statistics', methods=['GET'])
@template_management_bp.route('/templates/<template_id>/statistics', methods=['GET'])
@jwt_required()
def get_template_statistics(template_id):
    """Get verification statistics for a template."""
    try:
        from models.certificate_template import CertificateTemplate
        
        template = CertificateTemplate.objects(id=template_id).first()
        if not template:
            return error_response('Template not found', 404)
        
        stats = {
            'template_id': str(template.id),
            'template_name': template.template_name,
            'total_verifications': template.total_verifications,
            'successful_matches': template.successful_matches,
            'failed_matches': template.total_verifications - template.successful_matches,
            'average_confidence': template.average_confidence,
            'success_rate': round(
                (template.successful_matches / template.total_verifications * 100)
                if template.total_verifications > 0 else 0,
                2
            )
        }
        
        return success_response(stats)
        
    except Exception as e:
        logger.error(f"Get statistics error: {str(e)}")
        return error_response(str(e), 500)
