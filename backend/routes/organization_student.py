"""
Routes for college/organization interaction with students.
"""
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.credential import Credential
from utils.api_response import success_response, error_response
from services.auth_service import AuthService
from services.credential_service import CredentialService
from mongoengine.queryset.visitor import Q
from mongoengine.errors import DoesNotExist
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
org_student_bp = Blueprint('org_student', __name__, url_prefix='/api/organization')

@org_student_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to check if the blueprint is working."""
    return success_response(
        data={'message': 'Organization student blueprint is working'},
        message='Test successful'
    )
    """
    Search for students by name, email, or TrueCred ID.
    
    Query Parameters:
        query: Search text (name, email, or TrueCred ID)
        
    Returns:
        List of matching students (limited fields)
    """
    try:
        # Get the current user
        current_user_id = get_jwt_identity()
        current_user = User.objects.get(id=current_user_id)
        
        # Check if the user is a college or company
        if current_user.role not in ['college', 'company']:
            return error_response(
                message="Only colleges and companies can search for students", 
                status_code=403
            )
        
        # Get the search query
        query = request.args.get('query', '')
        if not query or len(query) < 3:
            return error_response(
                message="Search query must be at least 3 characters long",
                status_code=400
            )
        
        # Search for students
        students = User.objects(
            role='student'
        ).filter(
            # Match on name, email, or TrueCred ID
            # Using Q operators for OR conditions
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(email__icontains=query) | 
            Q(truecred_id__icontains=query)
        ).only(
            'id', 'username', 'first_name', 'last_name', 'email', 
            'truecred_id', 'affiliated_organizations'
        ).limit(20)
        
        # Format the results
        results = []
        for student in students:
            results.append({
                'id': str(student.id),
                'username': student.username,
                'name': f"{student.first_name or ''} {student.last_name or ''}".strip() or student.username,
                'email': student.email,
                'truecred_id': student.truecred_id,
                'is_affiliated': current_user.organization in (student.affiliated_organizations or [])
            })
        
        return success_response(
            data={'students': results},
            message=f"Found {len(results)} students matching '{query}'"
        )
        
    except Exception as e:
        logger.error(f"Error searching for students: {e}")
        return error_response(
            message=f"Error searching for students: {str(e)}",
            status_code=500
        )

@org_student_bp.route('/upload-credential/<student_id>', methods=['POST'])
@jwt_required()
def upload_student_credential(student_id):
    """
    Upload a credential for a student.
    
    URL Parameters:
        student_id: ID of the student
        
    Request Body (FormData or JSON):
        title: Title of the credential
        description: Description of the credential
        type: Type of credential (diploma, degree, certificate, badge, award, license, other)
        issue_date: Date when the credential was issued (YYYY-MM-DD) - auto-generated if not provided
        expiry_date: Date when the credential expires (YYYY-MM-DD, optional)
        certificate: Certificate file (optional)
        
    Returns:
        The created credential
    """
    try:
        # Get the current user
        current_user_id = get_jwt_identity()
        current_user = User.objects.get(id=current_user_id)
        
        # Check if the user is a college or company
        if current_user.role not in ['college', 'company']:
            return error_response(
                message="Only colleges and companies can upload credentials for students", 
                status_code=403
            )
        
        # Get the student
        try:
            student = User.objects.get(id=student_id)
        except DoesNotExist:
            return error_response(
                message="Student not found",
                status_code=404
            )
        
        # Verify the student is a student
        if student.role != 'student':
            return error_response(
                message="User is not a student",
                status_code=400
            )
        
        # Get request data - support both FormData and JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle FormData
            data = request.form.to_dict()
            certificate_file = request.files.get('certificate')
        else:
            # Handle JSON
            data = request.json or {}
            certificate_file = None
        
        # Validate required fields
        required_fields = ['title', 'type']
        for field in required_fields:
            if field not in data:
                return error_response(
                    message=f"Missing required field: {field}",
                    status_code=400
                )
        
        # Set default issue date if not provided
        if 'issue_date' not in data or not data['issue_date']:
            data['issue_date'] = datetime.utcnow().strftime('%Y-%m-%d')
        
        # Parse dates
        try:
            issue_date = datetime.strptime(data['issue_date'], '%Y-%m-%d')
            expiry_date = None
            if 'expiry_date' in data and data['expiry_date']:
                expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d')
        except ValueError:
            return error_response(
                message="Invalid date format. Use YYYY-MM-DD",
                status_code=400
            )
        
        # Create the credential
        credential = Credential(
            user=student,
            title=data['title'],
            issuer=current_user.organization,
            description=data.get('description', ''),
            type=data['type'],
            issue_date=issue_date,
            expiry_date=expiry_date,
            verified=True,  # Auto-verify credentials from trusted sources
            verified_at=datetime.utcnow()
        )
        
        # Handle certificate file upload
        if certificate_file:
            # Validate file type - only PDFs allowed
            if not certificate_file.filename.lower().endswith('.pdf'):
                return error_response(
                    message="Only PDF files are allowed for certificate upload",
                    status_code=400
                )
            
            # Validate file size (max 10MB)
            certificate_file.seek(0, 2)  # Seek to end
            file_size = certificate_file.tell()
            certificate_file.seek(0)  # Seek back to beginning
            
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                return error_response(
                    message="Certificate file size must be less than 10MB",
                    status_code=400
                )
            
            try:
                from services.ipfs_service import IPFSService
                
                # Read file content
                file_content = certificate_file.read()
                
                # Store on IPFS
                ipfs = IPFSService()
                if ipfs.connect():
                    upload_result = ipfs.add_file(file_content, certificate_file.filename)
                    if upload_result and 'Hash' in upload_result:
                        ipfs_hash = upload_result['Hash']
                        gateway_url = ipfs.get_gateway_url(ipfs_hash)
                        
                        credential.document_url = gateway_url
                        credential.document_hashes = {
                            certificate_file.filename: ipfs_hash
                        }
                        
                        # Try to pin the hash
                        try:
                            ipfs.pin_hash(ipfs_hash)
                            logger.info(f'Certificate uploaded to IPFS: {ipfs_hash}')
                        except Exception as e:
                            logger.warning(f'Failed to pin certificate hash: {e}')
                    else:
                        logger.warning('Failed to upload certificate to IPFS')
                        return error_response(
                            message="Failed to upload certificate to IPFS",
                            status_code=500
                        )
                else:
                    logger.warning('IPFS service not available for certificate upload')
                    return error_response(
                        message="IPFS service not available. Certificate upload failed.",
                        status_code=503
                    )
                
                # Update metadata
                credential.metadata = {
                    'has_document': True,
                    'uploaded_by': str(current_user.id),
                    'organization': current_user.organization,
                    'original_filename': certificate_file.filename
                }
            except Exception as e:
                logger.error(f'Error handling certificate upload: {e}')
                # Continue without certificate if upload fails
        
        # Save the credential
        credential.save()
        
        # Add this organization to the student's affiliated organizations if not already there
        if current_user.organization and current_user.organization not in (student.affiliated_organizations or []):
            if not student.affiliated_organizations:
                student.affiliated_organizations = []
            student.affiliated_organizations.append(current_user.organization)
            student.save()

        # If this upload is in response to a credential request, mark it issued and create a verified credential
        try:
            request_id = data.get('request_id') if isinstance(data, dict) else None
            if request_id:
                from models.credential_request import CredentialRequest
                from services.credential_service import CredentialService
                cr = CredentialRequest.objects(id=request_id).first()
                if cr:
                    # Create a verified credential for the student
                    credential_data = {
                        'title': cr.title,
                        'issuer': current_user.organization or cr.issuer or 'Unknown Issuer',
                        'description': cr.metadata.get('description') if cr.metadata else '',
                        'type': cr.type or 'certificate',
                        'issue_date': datetime.utcnow().isoformat(),
                        'expiry_date': None,
                        'document_url': credential.document_url,
                        'metadata': cr.metadata or {}
                    }
                    
                    # Create the verified credential
                    verified_credential, err = CredentialService.create_credential(user_id=cr.user_id, data=credential_data)
                    if verified_credential:
                        # Mark as verified
                        verified_credential.verified = True
                        verified_credential.verified_at = datetime.utcnow()
                        
                        # Copy document hashes if available
                        if hasattr(credential, 'document_hashes') and credential.document_hashes:
                            verified_credential.document_hashes = credential.document_hashes
                        
                        verified_credential.save()
                        logger.info(f'Created verified credential {verified_credential.id} for request {cr.id}')
                    
                    # Mark request as issued
                    cr.status = 'issued'
                    cr.issuer = current_user.organization or cr.issuer
                    cr.issuer_id = current_user.organization or cr.issuer_id
                    cr.save()

                    # Create a notification for the student
                    try:
                        note = {
                            'user_id': str(student.id),
                            'type': 'credential_request_update',
                            'title': 'Credential request issued',
                            'message': f"Your credential request '{cr.title}' has been issued by {cr.issuer}.",
                            'data': {'request_id': str(cr.id), 'credential_id': str(verified_credential.id) if verified_credential else str(credential.id)},
                            'created_at': datetime.utcnow()
                        }
                        if hasattr(current_app, 'db') and current_app.db:
                            current_app.db.notifications.insert_one(note)
                        else:
                            logger.info('Notification (no db): %s', note)
                    except Exception:
                        logger.exception('Failed to create notification for issued credential')
        except Exception:
            logger.exception('Error while marking credential request as issued')
        
        # Return success response
        return success_response(
            data={
                'credential_id': str(credential.id),
                'student': {
                    'id': str(student.id),
                    'name': f"{student.first_name or ''} {student.last_name or ''}".strip() or student.username,
                    'truecred_id': student.truecred_id
                }
            },
            message=f"Credential uploaded successfully for {student.first_name or student.username}"
        )
        
    except Exception as e:
        logger.error(f"Error uploading credential: {e}")
        return error_response(
            message=f"Error uploading credential: {str(e)}",
            status_code=500
        )

@org_student_bp.route('/student/<truecred_id>', methods=['GET'])
@jwt_required()
def get_student_by_truecred_id(truecred_id):
    """
    Get a student by their TrueCred ID.
    
    URL Parameters:
        truecred_id: TrueCred ID of the student
        
    Returns:
        Student information
    """
    try:
        # Get the current user
        current_user_id = get_jwt_identity()
        current_user = User.objects.get(id=current_user_id)
        
        # Check if the user is a college or company
        if current_user.role not in ['college', 'company']:
            return error_response(
                message="Only colleges and companies can look up students by ID", 
                status_code=403
            )
        
        # Get the student
        try:
            student = User.objects.get(truecred_id=truecred_id, role='student')
        except DoesNotExist:
            return error_response(
                message=f"No student found with TrueCred ID: {truecred_id}",
                status_code=404
            )
        
        # Return student information
        return success_response(
            data={
                'student': {
                    'id': str(student.id),
                    'username': student.username,
                    'name': f"{student.first_name or ''} {student.last_name or ''}".strip() or student.username,
                    'email': student.email,
                    'truecred_id': student.truecred_id,
                    'is_affiliated': current_user.organization in (student.affiliated_organizations or [])
                }
            },
            message=f"Found student with TrueCred ID: {truecred_id}"
        )
        
    except Exception as e:
        logger.error(f"Error getting student by TrueCred ID: {e}")
        return error_response(
            message=f"Error getting student by TrueCred ID: {str(e)}",
            status_code=500
        )

@org_student_bp.route('/bulk-upload-credentials', methods=['POST'])
@jwt_required()
def bulk_upload_credentials():
    """
    Upload credentials for multiple students at once.
    
    Request Body:
        credentials: Array of credential objects, each containing:
            student_id: ID of the student
            title: Title of the credential
            description: Description of the credential
            type: Type of credential
            issue_date: Date when the credential was issued (YYYY-MM-DD)
            expiry_date: Date when the credential expires (YYYY-MM-DD, optional)
        
    Returns:
        Results of the bulk upload operation
    """
    try:
        # Get the current user
        current_user_id = get_jwt_identity()
        current_user = User.objects.get(id=current_user_id)
        
        # Check if the user is a college or company
        if current_user.role not in ['college', 'company']:
            return error_response(
                message="Only colleges and companies can upload credentials for students", 
                status_code=403
            )
        
        # Get request data
        data = request.json
        
        # Validate data
        if 'credentials' not in data or not isinstance(data['credentials'], list):
            return error_response(
                message="Request must include a 'credentials' array",
                status_code=400
            )
        
        if len(data['credentials']) == 0:
            return error_response(
                message="Credentials array cannot be empty",
                status_code=400
            )
        
        if len(data['credentials']) > 100:
            return error_response(
                message="Cannot process more than 100 credentials at once",
                status_code=400
            )
        
        # Process each credential
        results = {
            'successful': [],
            'failed': []
        }
        
        for credential_data in data['credentials']:
            try:
                # Validate required fields
                required_fields = ['student_id', 'title', 'type', 'issue_date']
                missing_fields = [field for field in required_fields if field not in credential_data]
                
                if missing_fields:
                    results['failed'].append({
                        'data': credential_data,
                        'error': f"Missing required fields: {', '.join(missing_fields)}"
                    })
                    continue
                
                # Get the student
                try:
                    student = User.objects.get(id=credential_data['student_id'])
                except DoesNotExist:
                    results['failed'].append({
                        'data': credential_data,
                        'error': f"Student with ID {credential_data['student_id']} not found"
                    })
                    continue
                
                # Verify the student is a student
                if student.role != 'student':
                    results['failed'].append({
                        'data': credential_data,
                        'error': f"User with ID {credential_data['student_id']} is not a student"
                    })
                    continue
                
                # Parse dates
                try:
                    issue_date = datetime.strptime(credential_data['issue_date'], '%Y-%m-%d')
                    expiry_date = None
                    if 'expiry_date' in credential_data and credential_data['expiry_date']:
                        expiry_date = datetime.strptime(credential_data['expiry_date'], '%Y-%m-%d')
                except ValueError:
                    results['failed'].append({
                        'data': credential_data,
                        'error': "Invalid date format. Use YYYY-MM-DD"
                    })
                    continue
                
                # Create the credential
                credential = Credential(
                    user=student,
                    title=credential_data['title'],
                    issuer=current_user.organization,
                    description=credential_data.get('description', ''),
                    type=credential_data['type'],
                    issue_date=issue_date,
                    expiry_date=expiry_date,
                    verified=True,  # Auto-verify credentials from trusted sources
                    verified_at=datetime.utcnow()
                )
                
                # Save the credential
                credential.save()
                
                # Add this organization to the student's affiliated organizations if not already there
                if current_user.organization and current_user.organization not in (student.affiliated_organizations or []):
                    if not student.affiliated_organizations:
                        student.affiliated_organizations = []
                    student.affiliated_organizations.append(current_user.organization)
                    student.save()
                
                # Record success
                results['successful'].append({
                    'credential_id': str(credential.id),
                    'student': {
                        'id': str(student.id),
                        'name': f"{student.first_name or ''} {student.last_name or ''}".strip() or student.username,
                        'truecred_id': student.truecred_id
                    }
                })
                
            except Exception as e:
                # Record failure
                logger.error(f"Error processing credential: {e}")
                results['failed'].append({
                    'data': credential_data,
                    'error': str(e)
                })
        
        # Return results
        return success_response(
            data=results,
            message=f"Processed {len(data['credentials'])} credentials: {len(results['successful'])} successful, {len(results['failed'])} failed"
        )
        
    except Exception as e:
        logger.error(f"Error in bulk upload: {e}")
        return error_response(
            message=f"Error in bulk upload: {str(e)}",
            status_code=500
        )
