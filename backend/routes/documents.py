"""
Document management routes for TrueCred.

This module provides endpoints for secure document upload,
IPFS integration, and document verification.
"""
import os
import uuid
import hashlib
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from services.auth_service import require_auth
from services.ipfs_service import IPFSService
from services.web3_service import web3_service
from models.document import Document
from models.user import User
from middleware.security import rate_limit, validate_input, require_https, sanitize_string, validate_file_type

logger = logging.getLogger(__name__)

documents_bp = Blueprint('documents', __name__)

# Configure upload settings
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file) -> bool:
    """Check if file size is within limits."""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= MAX_FILE_SIZE

def calculate_file_hash(file) -> str:
    """Calculate SHA-256 hash of file."""
    file.seek(0)
    hash_sha256 = hashlib.sha256()
    for chunk in iter(lambda: file.read(4096), b""):
        hash_sha256.update(chunk)
    file.seek(0)
    return hash_sha256.hexdigest()

@documents_bp.route('/api/documents/upload', methods=['POST'])
@require_auth
@rate_limit('upload')
@require_https
def upload_document():
    """
    Upload a document and store it on IPFS.

    Expected form data:
    - file: The document file
    - document_type: Type of document (degree, transcript, certificate, etc.)
    - title: Document title
    - description: Optional description
    - is_public: Whether document should be publicly accessible
    """
    try:
        user_id = request.user_id

        # Check if file is present
        if 'file' not in request.files:
            return ApiResponse.error("No file provided")

        file = request.files['file']
        if file.filename == '':
            return ApiResponse.error("No file selected")

        # Validate file
        if not allowed_file(file.filename):
            return ApiResponse.error(f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")

        if not validate_file_size(file):
            return ApiResponse.error(f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB")

        # Get form data with sanitization
        document_type = sanitize_string(request.form.get('document_type', 'general'), 50)
        title = sanitize_string(request.form.get('title', file.filename), 200)
        description = sanitize_string(request.form.get('description', ''), 500)
        is_public = request.form.get('is_public', 'false').lower() == 'true'

        # Secure filename and generate unique ID
        filename = secure_filename(file.filename)
        document_id = str(uuid.uuid4())

        # Calculate file hash
        file_hash = calculate_file_hash(file)

        # Upload to IPFS
        ipfs_service = IPFSService()
        ipfs_result = ipfs_service.add_file(file, filename)

        if not ipfs_result or 'error' in ipfs_result:
            return ApiResponse.error(f"Failed to upload to IPFS: {ipfs_result.get('error', 'Unknown error')}")

        ipfs_hash = ipfs_result['Hash']

        # Store document metadata in database
        document = Document(
            document_id=document_id,
            user_id=user_id,
            filename=filename,
            original_filename=file.filename,
            document_type=document_type,
            title=title,
            description=description,
            file_size=file.content_length or 0,
            mime_type=file.content_type,
            ipfs_hash=ipfs_hash,
            file_hash=file_hash,
            is_public=is_public,
            upload_status='completed',
            blockchain_status='pending'  # Will be updated when stored on blockchain
        )
        document.save()

        logger.info(f"Document uploaded successfully: {document_id} by user {user_id}")

        return ApiResponse.success({
            'document_id': document_id,
            'ipfs_hash': ipfs_hash,
            'file_hash': file_hash,
            'filename': filename,
            'document_type': document_type,
            'title': title,
            'upload_timestamp': datetime.utcnow().isoformat()
        }, "Document uploaded successfully")

    except ValidationError as e:
        return ApiResponse.error(str(e))
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return ApiResponse.error("Failed to upload document")

@documents_bp.route('/api/documents/<document_id>', methods=['GET'])
@require_auth
def get_document(document_id: str):
    """Get document metadata and access information."""
    try:
        user_id = request.user_id

        # Find document
        document = Document.objects(document_id=document_id).first()
        if not document:
            return ApiResponse.error("Document not found")

        # Check access permissions
        if str(document.user_id) != user_id and not document.is_public:
            # Check if user has been granted access (future feature)
            return ApiResponse.error("Access denied")

        # Get IPFS access URL
        ipfs_service = IPFSService()
        ipfs_url = ipfs_service.get_gateway_url(document.ipfs_hash)

        return ApiResponse.success({
            'document_id': document.document_id,
            'filename': document.filename,
            'original_filename': document.original_filename,
            'document_type': document.document_type,
            'title': document.title,
            'description': document.description,
            'file_size': document.file_size,
            'mime_type': document.mime_type,
            'ipfs_hash': document.ipfs_hash,
            'file_hash': document.file_hash,
            'ipfs_url': ipfs_url,
            'is_public': document.is_public,
            'upload_status': document.upload_status,
            'blockchain_status': document.blockchain_status,
            'upload_timestamp': document.upload_timestamp.isoformat(),
            'verification_status': document.verification_status,
            'verified_by': document.verified_by,
            'verified_at': document.verified_at.isoformat() if document.verified_at else None
        }, "Document retrieved successfully")

    except Exception as e:
        logger.error(f"Error retrieving document: {str(e)}")
        return ApiResponse.error("Failed to retrieve document")

@documents_bp.route('/api/documents/<document_id>/download', methods=['GET'])
@require_auth
def download_document(document_id: str):
    """Download document from IPFS."""
    try:
        user_id = request.user_id

        # Find document
        document = Document.objects(document_id=document_id).first()
        if not document:
            return ApiResponse.error("Document not found")

        # Check access permissions
        if str(document.user_id) != user_id and not document.is_public:
            return ApiResponse.error("Access denied")

        # Download from IPFS
        ipfs_service = IPFSService()
        download_result = ipfs_service.get_file(document.ipfs_hash)

        if not download_result:
            return ApiResponse.error(f"Failed to download from IPFS: File not found")

        # Return file data (in a real implementation, you'd stream the file)
        return ApiResponse.success({
            'document_id': document.document_id,
            'filename': document.original_filename,
            'data': download_result.decode('latin-1') if isinstance(download_result, bytes) else download_result,
            'mime_type': document.mime_type
        }, "Document downloaded successfully")

    except Exception as e:
        logger.error(f"Error downloading document: {str(e)}")
        return ApiResponse.error("Failed to download document")

@documents_bp.route('/api/documents/<document_id>/verify', methods=['POST'])
@require_auth
def verify_document(document_id: str):
    """
    Manually verify a document.

    Expected JSON data:
    - verification_status: 'verified' or 'rejected'
    - comments: Optional verification comments
    - verified_by: Name/ID of verifier
    """
    try:
        user_id = request.user_id
        data = request.get_json()

        # Find document
        document = Document.objects(document_id=document_id).first()
        if not document:
            return ApiResponse.error("Document not found")

        # Check if user has verification permissions (issuer role)
        user = User.objects(id=user_id).first()
        if not user or user.role not in ['college', 'company', 'admin']:
            return ApiResponse.error("Insufficient permissions to verify documents")

        verification_status = data.get('verification_status')
        if verification_status not in ['verified', 'rejected']:
            return ApiResponse.error("Invalid verification status")

        # Update document verification status
        document.verification_status = verification_status
        document.verified_by = data.get('verified_by', user.email)
        document.verified_at = datetime.utcnow()
        document.verification_comments = data.get('comments', '')

        # If verified, store hash on blockchain
        if verification_status == 'verified':
            document.blockchain_status = 'storing'

            # Store credential on blockchain (this would be called asynchronously in production)
            try:
                blockchain_result = web3_service.store_credential_on_blockchain(
                    title=document.title,
                    student_id=str(document.user_id),  # This should be the actual student ID
                    student_name="Student Name",  # This should come from user profile
                    ipfs_hash=document.ipfs_hash,
                    metadata=json.dumps({
                        'document_type': document.document_type,
                        'file_hash': document.file_hash,
                        'verification_comments': document.verification_comments
                    }),
                    credential_type=2,  # Document type
                    issuer_private_key=os.getenv('ISSUER_PRIVATE_KEY')
                )

                if blockchain_result[0]:  # Success
                    document.blockchain_tx_hash = blockchain_result[2]
                    document.blockchain_status = 'stored'
                    document.credential_id = blockchain_result[1]
                else:
                    document.blockchain_status = 'failed'
                    logger.error(f"Failed to store document on blockchain: {blockchain_result[2]}")

            except Exception as e:
                logger.error(f"Blockchain storage error: {str(e)}")
                document.blockchain_status = 'failed'

        document.save()

        logger.info(f"Document {document_id} verification updated to {verification_status} by {user_id}")

        return ApiResponse.success({
            'document_id': document.document_id,
            'verification_status': document.verification_status,
            'verified_by': document.verified_by,
            'verified_at': document.verified_at.isoformat(),
            'blockchain_status': document.blockchain_status,
            'blockchain_tx_hash': document.blockchain_tx_hash,
            'credential_id': document.credential_id
        }, f"Document {verification_status} successfully")

    except Exception as e:
        logger.error(f"Error verifying document: {str(e)}")
        return ApiResponse.error("Failed to verify document")

@documents_bp.route('/api/documents/<document_id>/blockchain-status', methods=['GET'])
@require_auth
def get_blockchain_status(document_id: str):
    """Get blockchain storage status for a document."""
    try:
        user_id = request.user_id

        # Find document
        document = Document.objects(document_id=document_id).first()
        if not document:
            return ApiResponse.error("Document not found")

        # Check access permissions
        if str(document.user_id) != user_id and not document.is_public:
            return ApiResponse.error("Access denied")

        # If blockchain status is stored, verify the credential
        verification_result = None
        if document.blockchain_status == 'stored' and document.credential_id:
            verification_result = web3_service.verify_credential(document.credential_id)

        return ApiResponse.success({
            'document_id': document.document_id,
            'blockchain_status': document.blockchain_status,
            'blockchain_tx_hash': document.blockchain_tx_hash,
            'credential_id': document.credential_id,
            'verification_result': verification_result
        }, "Blockchain status retrieved successfully")

    except Exception as e:
        logger.error(f"Error getting blockchain status: {str(e)}")
        return ApiResponse.error("Failed to get blockchain status")

@documents_bp.route('/api/documents/user/<user_id>', methods=['GET'])
@require_auth
def get_user_documents(user_id: str):
    """Get all documents for a specific user."""
    try:
        current_user_id = request.user_id

        # Check if user can access these documents
        if current_user_id != user_id:
            # Check if current user is an issuer/admin
            current_user = User.objects(id=current_user_id).first()
            if not current_user or current_user.role not in ['college', 'company', 'admin']:
                return ApiResponse.error("Access denied")

        # Get user's documents
        documents = Document.objects(user_id=user_id).order_by('-upload_timestamp')

        document_list = []
        for doc in documents:
            document_list.append({
                'document_id': doc.document_id,
                'filename': doc.filename,
                'original_filename': doc.original_filename,
                'document_type': doc.document_type,
                'title': doc.title,
                'description': doc.description,
                'file_size': doc.file_size,
                'upload_status': doc.upload_status,
                'blockchain_status': doc.blockchain_status,
                'verification_status': doc.verification_status,
                'upload_timestamp': doc.upload_timestamp.isoformat(),
                'ipfs_hash': doc.ipfs_hash
            })

        return ApiResponse.success(document_list, f"Retrieved {len(document_list)} documents")

    except Exception as e:
        logger.error(f"Error getting user documents: {str(e)}")
        return ApiResponse.error("Failed to get user documents")

@documents_bp.route('/api/documents/pending-verification', methods=['GET'])
@require_auth
def get_pending_verification():
    """Get documents pending verification (for issuers)."""
    try:
        user_id = request.user_id

        # Check if user has verification permissions
        user = User.objects(id=user_id).first()
        if not user or user.role not in ['college', 'company', 'admin']:
            return ApiResponse.error("Insufficient permissions")

        # Get pending documents
        pending_documents = Document.objects(
            verification_status='pending'
        ).order_by('-upload_timestamp')

        document_list = []
        for doc in pending_documents:
            # Get user info
            doc_user = User.objects(id=doc.user_id).first()

            document_list.append({
                'document_id': doc.document_id,
                'filename': doc.filename,
                'original_filename': doc.original_filename,
                'document_type': doc.document_type,
                'title': doc.title,
                'description': doc.description,
                'file_size': doc.file_size,
                'upload_timestamp': doc.upload_timestamp.isoformat(),
                'user_name': doc_user.first_name + ' ' + doc_user.last_name if doc_user else 'Unknown',
                'user_email': doc_user.email if doc_user else 'Unknown',
                'ipfs_hash': doc.ipfs_hash
            })

        return ApiResponse.success(document_list, f"Retrieved {len(document_list)} pending documents")

    except Exception as e:
        logger.error(f"Error getting pending documents: {str(e)}")
        return ApiResponse.error("Failed to get pending documents")

@documents_bp.route('/api/documents/<document_id>/share', methods=['POST'])
@require_auth
def share_document(document_id: str):
    """
    Generate a shareable link for a document.

    Expected JSON data:
    - expires_in: Expiration time in hours (optional)
    - access_level: 'view' or 'download' (optional)
    """
    try:
        user_id = request.user_id
        data = request.get_json()

        # Find document
        document = Document.objects(document_id=document_id).first()
        if not document:
            return ApiResponse.error("Document not found")

        # Check ownership
        if str(document.user_id) != user_id:
            return ApiResponse.error("Access denied")

        # Generate share token (simplified - in production use JWT)
        share_token = str(uuid.uuid4())
        expires_in = data.get('expires_in', 24)  # Default 24 hours
        access_level = data.get('access_level', 'view')

        # In a real implementation, you'd store this in a database
        share_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/shared/{share_token}"

        return ApiResponse.success({
            'share_token': share_token,
            'share_url': share_url,
            'expires_in': expires_in,
            'access_level': access_level,
            'document_id': document.document_id,
            'document_title': document.title
        }, "Share link generated successfully")

    except Exception as e:
        logger.error(f"Error sharing document: {str(e)}")
        return ApiResponse.error("Failed to share document")