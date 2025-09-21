"""
Minimal company review endpoints to support the frontend's pending/history and approve/reject flows.

These are additive, scoped routes that don't disturb the existing Experiences API.
"""
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import DoesNotExist
import logging

from models.experience import Experience
from models.user import User
from services.ipfs_service import IPFSService

logger = logging.getLogger(__name__)

company_exp_bp = Blueprint('experiences_company', __name__, url_prefix='/api/experiences')

company_exp_bp = Blueprint('experiences_company', __name__, url_prefix='/api/experiences')


def _format_date(dt):
    try:
        return dt.strftime('%b %d, %Y') if dt else None
    except Exception:
        return None


@company_exp_bp.route('/pending', methods=['GET'])
@jwt_required()
def pending_experiences():
    # For now, return globally pending experiences
    exps = Experience.objects(verification_status='pending').order_by('-created_at')
    out = []
    ipfs = IPFSService()
    
    for x in exps:
        try:
            student = x.user
            # Generate document URLs from IPFS hashes
            document_urls = []
            if x.document_hashes:
                for filename, ipfs_hash in x.document_hashes.items():
                    try:
                        gateway_url = ipfs.get_gateway_url(ipfs_hash)
                        document_urls.append({
                            'filename': filename,
                            'url': gateway_url
                        })
                    except Exception as e:
                        logger.warning(f'Failed to generate gateway URL for {ipfs_hash}: {e}')
            
            out.append({
                'id': str(x.id),
                'studentName': f"{student.first_name or ''} {student.last_name or ''}".strip() or student.username,
                'experienceTitle': x.title,
                'company': x.organization,
                'duration': None,
                'submissionDate': _format_date(x.created_at) or _format_date(x.updated_at) or _format_date(datetime.utcnow()),
                'documentUrls': document_urls,
                'documentHashes': x.document_hashes or {},
                'document_url': x.document_url,
                'verificationStatus': x.verification_status,
                'pending_verification': x.pending_verification,
                'verification_attempts': x.verification_attempts or [],
                'metadata': x.metadata or {},
                'created_at': x.created_at.isoformat() if x.created_at else None,
                'updated_at': x.updated_at.isoformat() if x.updated_at else None
            })
        except Exception as e:
            logger.error(f'Error processing experience {x.id}: {e}')
            out.append({
                'id': str(x.id),
                'studentName': 'Student',
                'experienceTitle': x.title,
                'company': x.organization,
                'duration': None,
                'submissionDate': _format_date(x.created_at) or _format_date(datetime.utcnow()),
                'documentUrls': [],
                'documentHashes': {},
                'document_url': x.document_url,
                'verificationStatus': x.verification_status,
                'pending_verification': x.pending_verification,
                'verification_attempts': x.verification_attempts or [],
                'metadata': x.metadata or {},
                'created_at': x.created_at.isoformat() if x.created_at else None,
                'updated_at': x.updated_at.isoformat() if x.updated_at else None
            })
    return jsonify({'requests': out}), 200


@company_exp_bp.route('/history', methods=['GET'])
@jwt_required()
def experiences_history():
    exps = Experience.objects(verification_status__in=['verified', 'rejected']).order_by('-updated_at')
    out = []
    for x in exps:
        try:
            student = x.user
            out.append({
                'id': str(x.id),
                'studentName': f"{student.first_name or ''} {student.last_name or ''}".strip() or student.username,
                'experienceTitle': x.title,
                'status': 'verified' if x.is_verified else 'rejected',
                'actionDate': _format_date(x.updated_at) or _format_date(datetime.utcnow()),
            })
        except Exception:
            out.append({
                'id': str(x.id),
                'studentName': 'Student',
                'experienceTitle': x.title,
                'status': 'verified' if x.is_verified else 'rejected',
                'actionDate': _format_date(x.updated_at) or _format_date(datetime.utcnow()),
            })
    return jsonify({'history': out}), 200


@company_exp_bp.route('/request', methods=['POST'])
@jwt_required()
def request_experience_verification():
    """Create an experience verification request from minimal input."""
    data = request.json or {}
    logger.info(f"Experience request data: {data}")
    
    title = data.get('title') or data.get('experienceTitle')
    company = data.get('company') or data.get('organization')
    if not title or not company:
        return jsonify({'error': 'Missing field: title or company'}), 400

    # Build a minimal Experience record
    user_id = get_jwt_identity()
    try:
        user = User.objects.get(id=user_id)
    except Exception:
        return jsonify({'error': 'User not found'}), 404

    exp = Experience(
        user=user,
        title=title,
        organization=company,
        type=data.get('type', 'work'),
        start_date=datetime.utcnow(),
        description=data.get('description'),
        is_current=True,
        pending_verification=True,
        verification_status='pending',
        metadata=data.get('metadata') or {},
    )
    
    # Process attachments if provided
    attachments = data.get('attachments', [])
    logger.info(f"Processing {len(attachments)} attachments")
    document_hashes = {}
    first_hash = None
    
    if attachments:
        ipfs = IPFSService()
        for idx, att in enumerate(attachments):
            uri = att.get('uri') if isinstance(att, dict) else None
            filename = att.get('filename') if isinstance(att, dict) else f'attachment_{idx}'
            
            # Extract IPFS hash from URI
            def extract_ipfs_hash(uri):
                if not uri:
                    return None
                # Handle ipfs:// protocol
                if uri.startswith('ipfs://'):
                    return uri.replace('ipfs://', '')
                # Handle gateway URLs
                if 'ipfs.infura.io' in uri or 'gateway.pinata.cloud' in uri or 'ipfs.io' in uri:
                    parts = uri.split('/')
                    for i, part in enumerate(parts):
                        if part == 'ipfs':
                            return parts[i+1] if i+1 < len(parts) else None
                # Handle direct CID
                if len(uri) == 46 or len(uri) == 59:  # Typical CID lengths
                    return uri
                return None
            
            cid = extract_ipfs_hash(uri)
            if cid:
                try:
                    ipfs.pin_hash(cid)
                except Exception as e:
                    logger.warning('Pinning %s failed: %s', cid, e)

                document_hashes[filename] = cid
                if not first_hash:
                    first_hash = cid
            else:
                # If we couldn't extract a CID but URI is present, try to fetch and re-upload
                try:
                    import requests
                    resp = requests.get(uri, timeout=30)
                    if resp.ok:
                        # Upload bytes to IPFS
                        upload_result = ipfs.add_file(resp.content, filename)
                        if upload_result and 'Hash' in upload_result:
                            new_cid = upload_result['Hash']
                            try:
                                ipfs.pin_hash(new_cid)
                            except Exception:
                                pass
                            document_hashes[filename] = new_cid
                            if not first_hash:
                                first_hash = new_cid
                except Exception as e:
                    logger.warning('Failed to fetch/reupload attachment uri %s: %s', uri, e)
        
        # Store document hashes in experience
        if document_hashes:
            exp.document_hashes = document_hashes
            logger.info(f"Stored document hashes: {document_hashes}")
        
        # If we found hashes, set experience.document_url to the gateway of the first
        if first_hash:
            try:
                gateway = ipfs.get_gateway_url(first_hash)
                exp.document_url = gateway
                logger.info(f"Set document_url to: {gateway}")
            except Exception as e:
                logger.warning(f'Failed to generate gateway URL for first hash {first_hash}: {e}')
    
    exp.save()
    logger.info(f"Created experience {exp.id} with document_url: {exp.document_url}")
    return jsonify({'success': True, 'id': str(exp.id)}), 201


@company_exp_bp.route('/<experience_id>/approve', methods=['POST'])
@jwt_required()
def approve_experience(experience_id):
    try:
        exp = Experience.objects.get(id=experience_id)
    except DoesNotExist:
        return jsonify({'error': 'Experience not found'}), 404
    # Update fields to mark verified
    exp.is_verified = True
    exp.verification_status = 'verified'
    exp.rejection_reason = None
    exp.pending_verification = False
    exp.verified_at = datetime.utcnow()
    exp.save()
    return jsonify({'success': True}), 200


@company_exp_bp.route('/<experience_id>/reject', methods=['POST'])
@jwt_required()
def reject_experience(experience_id):
    try:
        exp = Experience.objects.get(id=experience_id)
    except DoesNotExist:
        return jsonify({'error': 'Experience not found'}), 404
    reason = (request.json or {}).get('reason')
    exp.is_verified = False
    exp.verification_status = 'rejected'
    exp.rejection_reason = reason
    exp.pending_verification = False
    exp.save()
    return jsonify({'success': True}), 200
