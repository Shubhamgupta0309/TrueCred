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

    # Normalize JWT identity (some backends put a dict into the identity)
    try:
        orig_identity = current_user_id
        if isinstance(current_user_id, dict):
            for key in ('user_id', 'id', '_id', 'sub', 'username'):
                if key in current_user_id:
                    current_user_id = str(current_user_id[key])
                    break
        elif current_user_id is not None:
            current_user_id = str(current_user_id)
    except Exception:
        logger.exception('Failed to normalize JWT identity')

    # Get query parameters
    include_expired = request.args.get('include_expired', 'false').lower() == 'true'
    status = request.args.get('status')
    credential_type = request.args.get('type')

    logger.debug('GET /api/credentials called by identity=%s include_expired=%s status=%s type=%s', orig_identity, include_expired, status, credential_type)
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


@credentials_bp.route('/debug/me', methods=['GET'])
@jwt_required()
def debug_me():
    """Return debug information about the current JWT identity and DB lookups."""
    current_identity = get_jwt_identity()
    # Normalize identity similar to get_credentials
    normalized = current_identity
    try:
        if isinstance(normalized, dict):
            for key in ('user_id', 'id', '_id', 'sub', 'username'):
                if key in normalized:
                    normalized = str(normalized[key])
                    break
        elif normalized is not None:
            normalized = str(normalized)
    except Exception:
        logger.exception('Failed to normalize identity in debug')

    # Try to resolve a user document and sample credentials
    user_doc = None
    creds = []
    try:
        from models.user import User
        from models.credential import Credential
        # Try common lookups
        if normalized:
            # Prefer lookup by id if looks like an ObjectId
            try:
                u = User.objects(id=normalized).first()
            except Exception:
                u = None

            if not u:
                # attempt by username or email
                u = User.objects(username=normalized).first() or User.objects(email=normalized).first()

            if u:
                user_doc = u.to_json()
                # sample credentials
                cs = Credential.objects(user=str(u.id)).limit(10)
                creds = [c.to_json() for c in cs]
    except Exception as e:
        logger.exception('Debug lookup error: %s', e)

    return success_response(
        data={
            'identity_raw': current_identity,
            'identity_normalized': normalized,
            'user': user_doc,
            'sample_credentials': creds
        },
        message='Debug info'
    )
    
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


@credentials_bp.route('/request', methods=['POST'])
@jwt_required()
def request_credential():
    """Create a credential request (student -> issuer).

    Persists a CredentialRequest document with status 'pending' and creates a minimal notification.
    """
    current_user_id = get_jwt_identity()
    data = request.json or {}

    # Basic validation
    title = (data.get('title') or '').strip()
    if not title:
        return validation_error_response(errors={'title': 'Title is required'}, message='Missing title')

    # Build the request object
    try:
        from models.credential_request import CredentialRequest

        cr = CredentialRequest(
            user_id=str(current_user_id),
            title=title,
            issuer=data.get('issuer') or data.get('metadata', {}).get('institution') or '',
            issuer_id=data.get('issuer_id') or data.get('metadata', {}).get('institution_id') or '',
            type=data.get('type') or 'credential',
            metadata=data.get('metadata') or {},
            attachments=data.get('attachments') or [],
            status='pending'
        )
        cr.save()

        # Store credential request hash on blockchain for immutability
        blockchain_result = None
        try:
            from services.blockchain_service import BlockchainService
            blockchain = BlockchainService()
            if blockchain.is_connected():
                # Create a hash of the credential request data
                import hashlib
                request_data = f"{str(cr.id)}:{cr.user_id}:{cr.title}:{cr.issuer}:{datetime.utcnow().isoformat()}"
                request_hash = hashlib.sha256(request_data.encode()).hexdigest()
                
                # Store on blockchain
                blockchain_result = blockchain.store_credential_hash(
                    title=f"Request: {cr.title}",
                    issuer=cr.issuer or "Unknown Issuer",
                    student_id=cr.user_id,
                    ipfs_hash=request_hash  # Using request hash as IPFS hash for now
                )
                
                if blockchain_result and blockchain_result.get('status') == 'success':
                    # Update credential request with blockchain info
                    cr.blockchain_tx_hash = blockchain_result.get('transaction_hash')
                    cr.blockchain_credential_id = blockchain_result.get('credential_id')
                    cr.save()
                    logger.info(f"Credential request {cr.id} stored on blockchain: {blockchain_result.get('transaction_hash')}")
                else:
                    logger.warning(f"Failed to store credential request on blockchain: {blockchain_result}")
            else:
                logger.info("Blockchain service not connected, skipping blockchain storage")
        except Exception as e:
            logger.error(f"Error storing credential request on blockchain: {e}")
            # Don't fail the request if blockchain storage fails

        # Minimal notification hook: insert into notifications collection if available
        try:
            note = {
                'user_id': str(current_user_id),
                'type': 'credential_request',
                'title': 'Credential request submitted',
                'message': f"Your request '{title}' was created and is pending review.",
                'data': {'request_id': str(cr.id)},
                'created_at': datetime.utcnow()
            }
            if hasattr(current_app, 'db') and current_app.db:
                # Use pymongo directly if available
                try:
                    current_app.db.notifications.insert_one(note)
                except Exception:
                    # Fall back to logging
                    logger.info('Notification creation failed, falling back to log')
                    logger.info(note)
            else:
                logger.info('Notification (no db): %s', note)
        except Exception as e:
            logger.error('Failed to create notification: %s', e)

        return success_response(data={'request_id': str(cr.id)}, message='Credential request submitted', status_code=201)
    except Exception as e:
        logger.error('Error creating credential request: %s', e, exc_info=True)
        return error_response(message=str(e), status_code=500)


@credentials_bp.route('/user/requests', methods=['GET'])
@jwt_required()
def get_user_requests():
    """
    Get credential requests for the authenticated user.
    Returns a list of CredentialRequest documents.
    """
    try:
        current_user_id = get_jwt_identity()
        # Normalize identity
        try:
            if isinstance(current_user_id, dict):
                for key in ('user_id', 'id', '_id', 'sub', 'username'):
                    if key in current_user_id:
                        current_user_id = str(current_user_id[key])
                        break
            elif current_user_id is not None:
                current_user_id = str(current_user_id)
        except Exception:
            logger.exception('Failed to normalize JWT identity for user requests')

        from models.credential_request import CredentialRequest
        # Try MongoEngine query first
        try:
            logger.debug('Fetching CredentialRequest objects for user_id=%s', str(current_user_id))
            reqs = CredentialRequest.objects(user_id=str(current_user_id)).order_by('-created_at')
            count = reqs.count()
            logger.debug('MongoEngine returned %s CredentialRequest records for user %s', count, current_user_id)
            if count > 0:
                data = [r.to_mongo().to_dict() for r in reqs]
                for d in data:
                    if d.get('_id'):
                        d['id'] = str(d['_id'])
                        d.pop('_id', None)
                return success_response(data={'requests': data}, message=f'Retrieved {len(data)} requests')
        except Exception as e:
            logger.exception('Error querying CredentialRequest via MongoEngine: %s', e)

        # If no results via MongoEngine, try PyMongo directly if available on current_app
        try:
            db = getattr(current_app, 'db', None)
            if db is not None:
                logger.debug('Falling back to PyMongo for user_id=%s', str(current_user_id))
                cursor = db.credential_requests.find({'user_id': str(current_user_id)}).sort('created_at', -1)
                requests = []
                for doc in cursor:
                    doc['id'] = str(doc.get('_id'))
                    doc.pop('_id', None)
                    requests.append(doc)
                logger.debug('PyMongo returned %s documents for user %s', len(requests), current_user_id)
                return success_response(data={'requests': requests}, message=f'Retrieved {len(requests)} requests (via pymongo)')
        except Exception as e:
            logger.exception('Error querying credential_requests via PyMongo fallback: %s', e)

        # Nothing found
        logger.info('No credential requests found for user %s', current_user_id)
        return success_response(data={'requests': []}, message='Retrieved 0 requests')
    except Exception as e:
        logger.exception('Error fetching user credential requests: %s', e)
        return error_response(message='Failed to fetch user requests', status_code=500)

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


@credentials_bp.route('/<request_id>/approve', methods=['POST'])
@jwt_required()
@issuer_required
def approve_request(request_id):
    """
    Approve a credential request: create a Credential from the CredentialRequest,
    mark the request as issued and create notifications for the student.
    """
    current_user_id = get_jwt_identity()
    try:
        from models.credential_request import CredentialRequest
        from models.user import User

        cr = CredentialRequest.objects(id=request_id).first()
        if not cr:
            return not_found_response(resource_type='CredentialRequest', resource_id=request_id)

        # Create credential data based on the request
        credential_data = {
            'title': cr.title,
            'issuer': cr.issuer or '',
            'description': cr.metadata.get('description') if cr.metadata else '',
            'type': cr.type or 'credential',
            'issue_date': datetime.utcnow().isoformat(),
            'expiry_date': None,
            'document_url': None,
            'metadata': cr.metadata or {}
        }

        # Use CredentialService to create the credential for the user referenced by the request
        credential, err = CredentialService.create_credential(user_id=cr.user_id, data=credential_data)
        if err:
            return error_response(message=f"Failed to create credential: {err}", status_code=400)

        # If there are attachments on the request, attempt to pin them and store hashes on the credential
        try:
            attachments = cr.attachments or []
            if attachments:
                from services.ipfs_service import IPFSService
                import re

                def extract_ipfs_hash(uri: str):
                    if not uri or not isinstance(uri, str):
                        return None
                    uri = uri.strip()
                    # ipfs://CID
                    m = re.search(r'ipfs://(?P<h>[A-Za-z0-9]+)', uri)
                    if m:
                        return m.group('h')
                    # gateway /ipfs/{cid}
                    m = re.search(r'/ipfs/(?P<h>[A-Za-z0-9]+)', uri)
                    if m:
                        return m.group('h')
                    # CIDv0 (Qm...) common form
                    m = re.search(r'(Qm[1-9A-HJ-NP-Za-km-z]{44})', uri)
                    if m:
                        return m.group(1)
                    # Fallback: any long alphanumeric sequence (CIDv1)
                    m = re.search(r'([A-Za-z0-9]{46,})', uri)
                    if m:
                        return m.group(1)
                    return None

                ipfs = IPFSService()
                if ipfs.connect():
                    # Ensure credential has a document_hashes dict
                    if not hasattr(credential, 'document_hashes') or not credential.document_hashes:
                        credential.document_hashes = {}

                    first_hash = None
                    for idx, att in enumerate(attachments):
                        uri = att.get('uri') if isinstance(att, dict) else None
                        filename = att.get('filename') if isinstance(att, dict) else f'attachment_{idx}'
                        cid = extract_ipfs_hash(uri)
                        if cid:
                            try:
                                ipfs.pin_hash(cid)
                            except Exception as e:
                                logger.warning('Pinning %s failed: %s', cid, e)

                            credential.document_hashes[filename] = cid
                            if not first_hash:
                                first_hash = cid
                        else:
                            # If we couldn't extract a CID but URI is present (maybe gateway URL), try to fetch and re-upload
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
                                        credential.document_hashes[filename] = new_cid
                                        if not first_hash:
                                            first_hash = new_cid
                            except Exception as e:
                                logger.warning('Failed to fetch/reupload attachment uri %s: %s', uri, e)

                    # If we found hashes, set credential.document_url to the gateway of the first
                    if first_hash:
                        try:
                            gateway = ipfs.get_gateway_url(first_hash)
                            credential.document_url = gateway
                        except Exception:
                            pass

                    # Save credential with added document hashes
                    credential.save()
                else:
                    logger.info('IPFS not available; skipping attachment pinning')
        except Exception as e:
            logger.exception('Error while pinning attachments: %s', e)

        # Mark request as issued and save
        cr.status = 'issued'
        cr.save()

        # Store issued credential hash on blockchain
        blockchain_result = None
        try:
            from services.blockchain_service import BlockchainService
            blockchain = BlockchainService()
            if blockchain.is_connected():
                # Store the issued credential on blockchain
                blockchain_result = blockchain.store_credential_hash(
                    title=credential.title,
                    issuer=credential.issuer or "Unknown Issuer",
                    student_id=cr.user_id,
                    ipfs_hash=credential.document_url or credential.document_hash or ""
                )
                
                if blockchain_result and blockchain_result.get('status') == 'success':
                    # Update credential with blockchain info
                    credential.blockchain_tx_hash = blockchain_result.get('transaction_hash')
                    credential.blockchain_credential_id = blockchain_result.get('credential_id')
                    credential.save()
                    logger.info(f"Credential {credential.id} stored on blockchain: {blockchain_result.get('transaction_hash')}")
                else:
                    logger.warning(f"Failed to store credential on blockchain: {blockchain_result}")
            else:
                logger.info("Blockchain service not connected, skipping blockchain storage")
        except Exception as e:
            logger.error(f"Error storing credential on blockchain: {e}")
            # Don't fail the approval if blockchain storage fails

        # Create notifications: notify student and optionally log for issuer
        note_student = {
            'user_id': cr.user_id,
            'type': 'credential_issued',
            'title': 'Credential issued',
            'message': f"Your credential request '{cr.title}' was approved and issued.",
            'data': {'request_id': str(cr.id), 'credential_id': str(credential.id)},
            'created_at': datetime.utcnow()
        }
        try:
            if hasattr(current_app, 'db') and current_app.db:
                current_app.db.notifications.insert_one(note_student)
        except Exception:
            logger.info('Failed to persist student notification, logging instead: %s', note_student)

        # Return created credential
        return success_response(data=credential.to_json(), message='Request approved and credential issued')
    except Exception as e:
        logger.exception('Error approving request: %s', e)
        return error_response(message=str(e), status_code=500)


@credentials_bp.route('/organization/upload-credential/<student_id>', methods=['POST'])
@jwt_required()
@issuer_required
def upload_credential_for_student(student_id):
    """
    Endpoint for an issuer to upload an authoritative credential for a specific student.

    Path parameter:
      student_id: ID of the student (user) to receive the credential

    Request body (JSON):
      request_id: Optional credential request ID to mark as issued
      title: Optional title (falls back to request.title)
      type: Optional type
      description: Optional description
      issue_date/expiry_date: Optional ISO dates
      attachments: Optional list of attachments (same shape as CredentialRequest.attachments)

    Returns:
      Created credential
    """
    current_user_id = get_jwt_identity()
    data = request.json or {}

    # Optional request_id to mark existing request as issued
    request_id = data.get('request_id')

    try:
        from models.credential_request import CredentialRequest

        # If request_id provided, try to load it for metadata
        cr = None
        if request_id:
            cr = CredentialRequest.objects(id=request_id).first()
            if not cr:
                return not_found_response(resource_type='CredentialRequest', resource_id=request_id)

        # Build credential data
        credential_data = {
            'title': data.get('title') or (cr.title if cr else None),
            'issuer': data.get('issuer') or (cr.issuer if cr else ''),
            'description': data.get('description') or (cr.metadata.get('description') if cr and cr.metadata else ''),
            'type': data.get('type') or (cr.type if cr else 'credential'),
            'issue_date': data.get('issue_date') or datetime.utcnow().isoformat(),
            'expiry_date': data.get('expiry_date'),
            'document_url': None,
            'metadata': data.get('metadata') or (cr.metadata if cr else {})
        }

        # Use CredentialService to create the credential for the student
        credential, err = CredentialService.create_credential(user_id=student_id, data=credential_data)
        if err:
            return error_response(message=f"Failed to create credential: {err}", status_code=400)
        # First: support issuer-provided base64 document(s) in the JSON body
        try:
            # `document` may be a single base64 string or data URL; `documents` may be a list of base64 strings or dicts
            doc_field = data.get('document')
            docs_field = data.get('documents')
            if doc_field or docs_field:
                from services.ipfs_service import IPFSService
                import base64 as _b64

                ipfs = IPFSService()
                if ipfs.connect():
                    if not hasattr(credential, 'document_hashes') or not credential.document_hashes:
                        credential.document_hashes = {}

                    first_hash = None

                    def _process_base64_entry(entry, idx=0):
                        nonlocal first_hash
                        # entry can be a dict with keys {document, filename} or a raw base64/dataurl string
                        if isinstance(entry, dict):
                            content = entry.get('document') or entry.get('data') or entry.get('file') or ''
                            filename = entry.get('filename') or f'attachment_{idx}'
                        else:
                            content = entry
                            filename = f'attachment_{idx}'

                        if not content:
                            return

                        # Strip data URL prefix if present
                        if isinstance(content, str) and ';base64,' in content:
                            try:
                                _, encoded = content.split(';base64,', 1)
                            except Exception:
                                encoded = content
                        else:
                            encoded = content

                        try:
                            file_bytes = _b64.b64decode(encoded)
                        except Exception as e:
                            logger.warning('Failed to decode base64 document entry: %s', e)
                            return

                        # Prepare metadata for IPFS
                        metadata = credential_data.get('metadata', {}) if isinstance(credential_data, dict) else {}
                        metadata = metadata.copy()
                        metadata.update({'filename': filename, 'issuer': credential_data.get('issuer')})

                        try:
                            store_res = ipfs.store_document(file_bytes, metadata)
                            if store_res and 'document_hash' in store_res:
                                cid = store_res.get('document_hash')
                                credential.document_hashes[filename] = cid
                                if not first_hash:
                                    first_hash = cid
                        except Exception as e:
                            logger.warning('Failed to store base64 document to IPFS: %s', e)

                    # Process single document
                    if doc_field:
                        _process_base64_entry(doc_field, 0)

                    # Process list of documents
                    if docs_field and isinstance(docs_field, list):
                        for i, entry in enumerate(docs_field):
                            _process_base64_entry(entry, i)

                    # If we stored at least one doc, set document_url to gateway of first
                    if first_hash:
                        try:
                            credential.document_url = ipfs.get_gateway_url(first_hash)
                        except Exception:
                            pass

                    credential.save()
                else:
                    logger.info('IPFS not available; skipping issuer-provided base64 document storage')
        except Exception as e:
            logger.exception('Error while storing issuer-provided base64 document(s): %s', e)

        # Process attachments (from request or body)
        try:
            attachments = data.get('attachments') or (cr.attachments if cr else [])
            if attachments:
                from services.ipfs_service import IPFSService
                import re

                def extract_ipfs_hash(uri: str):
                    if not uri or not isinstance(uri, str):
                        return None
                    uri = uri.strip()
                    m = re.search(r'ipfs://(?P<h>[A-Za-z0-9]+)', uri)
                    if m:
                        return m.group('h')
                    m = re.search(r'/ipfs/(?P<h>[A-Za-z0-9]+)', uri)
                    if m:
                        return m.group('h')
                    m = re.search(r'(Qm[1-9A-HJ-NP-Za-km-z]{44})', uri)
                    if m:
                        return m.group(1)
                    m = re.search(r'([A-Za-z0-9]{46,})', uri)
                    if m:
                        return m.group(1)
                    return None

                ipfs = IPFSService()
                if ipfs.connect():
                    if not hasattr(credential, 'document_hashes') or not credential.document_hashes:
                        credential.document_hashes = {}

                    first_hash = None
                    for idx, att in enumerate(attachments):
                        uri = att.get('uri') if isinstance(att, dict) else None
                        filename = att.get('filename') if isinstance(att, dict) else f'attachment_{idx}'
                        cid = extract_ipfs_hash(uri)
                        if cid:
                            try:
                                ipfs.pin_hash(cid)
                            except Exception as e:
                                logger.warning('Pinning %s failed: %s', cid, e)

                            credential.document_hashes[filename] = cid
                            if not first_hash:
                                first_hash = cid
                        else:
                            # try to fetch and re-upload
                            try:
                                import requests
                                resp = requests.get(uri, timeout=30)
                                if resp.ok:
                                    upload_result = ipfs.add_file(resp.content, filename)
                                    if upload_result and 'Hash' in upload_result:
                                        new_cid = upload_result['Hash']
                                        try:
                                            ipfs.pin_hash(new_cid)
                                        except Exception:
                                            pass
                                        credential.document_hashes[filename] = new_cid
                                        if not first_hash:
                                            first_hash = new_cid
                            except Exception as e:
                                logger.warning('Failed to fetch/reupload attachment uri %s: %s', uri, e)

                    if first_hash:
                        try:
                            gateway = ipfs.get_gateway_url(first_hash)
                            credential.document_url = gateway
                        except Exception:
                            pass

                    credential.save()
                else:
                    logger.info('IPFS not available; skipping attachment pinning')
        except Exception as e:
            logger.exception('Error while processing attachments for uploaded credential: %s', e)

        # If a request was provided, mark it as issued
        if cr:
            cr.status = 'issued'
            cr.save()

            # Notify student about issued credential
            note_student = {
                'user_id': cr.user_id,
                'type': 'credential_issued',
                'title': 'Credential issued',
                'message': f"Your credential request '{cr.title}' was approved and issued.",
                'data': {'request_id': str(cr.id), 'credential_id': str(credential.id)},
                'created_at': datetime.utcnow()
            }
            try:
                if hasattr(current_app, 'db') and current_app.db:
                    current_app.db.notifications.insert_one(note_student)
            except Exception:
                logger.info('Failed to persist student notification, logging instead: %s', note_student)

        # Also, if no request was provided, create a lightweight notification for the student
        if not cr:
            try:
                note_student = {
                    'user_id': str(student_id),
                    'type': 'credential_issued',
                    'title': 'Credential issued',
                    'message': f"An issuer uploaded a credential for your account: {credential.title}",
                    'data': {'credential_id': str(credential.id)},
                    'created_at': datetime.utcnow()
                }
                if hasattr(current_app, 'db') and current_app.db:
                    current_app.db.notifications.insert_one(note_student)
            except Exception:
                logger.info('Failed to persist student notification, logging instead: %s', note_student)

        return success_response(data=credential.to_json(), message='Credential uploaded/issued successfully')
    except Exception as e:
        logger.exception('Error uploading credential for student: %s', e)
        return error_response(message=str(e), status_code=500)


@credentials_bp.route('/<request_id>/reject', methods=['POST'])
@jwt_required()
@issuer_required
def reject_request(request_id):
    """
    Reject a credential request. Marks the request as rejected and notifies the student.
    Request body may include optional 'reason'.
    """
    current_user_id = get_jwt_identity()
    data = request.json or {}
    reason = data.get('reason')
    try:
        from models.credential_request import CredentialRequest

        cr = CredentialRequest.objects(id=request_id).first()
        if not cr:
            return not_found_response(resource_type='CredentialRequest', resource_id=request_id)

        cr.status = 'rejected'
        cr.save()

        note_student = {
            'user_id': cr.user_id,
            'type': 'credential_rejected',
            'title': 'Credential request rejected',
            'message': f"Your credential request '{cr.title}' was rejected." + (f" Reason: {reason}" if reason else ''),
            'data': {'request_id': str(cr.id)},
            'created_at': datetime.utcnow()
        }
        try:
            if hasattr(current_app, 'db') and current_app.db:
                current_app.db.notifications.insert_one(note_student)
        except Exception:
            logger.info('Failed to persist student rejection notification, logging instead: %s', note_student)

        return success_response(message='Request rejected')
    except Exception as e:
        logger.exception('Error rejecting request: %s', e)
        return error_response(message=str(e), status_code=500)

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


@credentials_bp.route('/blockchain/verify/<credential_id>', methods=['GET'])
@jwt_required()
def verify_credential_blockchain(credential_id):
    """
    Verify a credential using blockchain data.
    ---
    Requires authentication.
    """
    try:
        from models.credential import Credential
        
        # Find the credential in database
        credential = Credential.objects(id=credential_id).first()
        if not credential:
            return not_found_response(resource_type='Credential', resource_id=credential_id)
        
        # Check if credential has blockchain data
        if not credential.blockchain_credential_id:
            return error_response(
                message="Credential not stored on blockchain",
                status_code=400
            )
        
        # Verify using blockchain
        from services.blockchain_service import BlockchainService
        blockchain = BlockchainService()
        
        verification_result = blockchain.verify_credential(credential.blockchain_credential_id)
        
        if verification_result and verification_result.get('status') == 'success':
            # Update credential verification status if blockchain confirms validity
            if verification_result.get('is_valid') and not credential.verified:
                credential.verified = True
                credential.verified_at = datetime.utcnow()
                credential.save()
            
            return success_response(
                data={
                    'credential_id': credential_id,
                    'blockchain_verified': True,
                    'blockchain_data': verification_result,
                    'database_match': (
                        verification_result.get('title') == credential.title and
                        verification_result.get('issuer') == credential.issuer
                    ),
                    'mock_mode': verification_result.get('mock', False)
                },
                message="Credential verified successfully via blockchain"
            )
        else:
            return error_response(
                message="Blockchain verification failed",
                error_code="blockchain_verification_failed",
                status_code=400
            )
            
    except Exception as e:
        logger.exception(f"Error verifying credential {credential_id}: {e}")
        return error_response(message=str(e), status_code=500)
