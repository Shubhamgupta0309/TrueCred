"""
IPFS document API routes for TrueCred.

This module handles API routes for storing and retrieving documents from IPFS.
"""
from flask import Blueprint, request, jsonify, current_app, g
import base64
from bson import ObjectId
import logging

from models.user import User
from models.credential import Credential
from models.experience import Experience
from services.ipfs_service import IPFSService
from middleware.auth_middleware import login_required, admin_required
from utils.api_response import success_response, error_response

# Initialize logger
logger = logging.getLogger(__name__)

# Create a Blueprint for IPFS-related routes
ipfs_bp = Blueprint('ipfs', __name__, url_prefix='/api/ipfs')

# Initialize IPFS service
ipfs_service = None

def get_ipfs_service():
    """Get or initialize the IPFS service."""
    global ipfs_service
    if ipfs_service is None:
        ipfs_service = IPFSService()
    return ipfs_service

@ipfs_bp.route('/status', methods=['GET'])
@login_required
def get_ipfs_status():
    """
    Get IPFS node status.
    
    Returns:
        JSON response with IPFS node status
    """
    try:
        ipfs = get_ipfs_service()
        
        # Check connection to IPFS
        connected = ipfs.connect()
        
        if not connected:
            return error_response('Failed to connect to IPFS node', 503)
        
        # Get node info
        node_info = ipfs.get_node_info()
        
        if 'error' in node_info:
            return error_response(f"Error getting IPFS node info: {node_info['error']}", 503)
            
        # Return status
        return success_response({
            'status': 'connected',
            'node_id': node_info.get('ID'),
            'addresses': node_info.get('Addresses'),
            'gateway': ipfs.gateway_url
        })
    except Exception as e:
        logger.error(f"Error getting IPFS status: {str(e)}")
        return error_response(f"Error getting IPFS status: {str(e)}", 500)
    finally:
        # Disconnect to avoid keeping connection open
        if ipfs_service:
            ipfs_service.disconnect()

@ipfs_bp.route('/upload', methods=['POST'])
@login_required
def upload_document():
    """
    Upload a document to IPFS.
    
    Returns:
        JSON response with IPFS hashes
    """
    try:
        # Get user from token
        user_id = g.user_id
        user = User.objects.get(id=user_id)
        
        # Check if file is in request
        if 'file' not in request.files:
            # Try to get it from form data
            if 'file_data' not in request.form:
                return error_response('No file provided', 400)
            
            # Get file data from form
            file_data = request.form['file_data']
            
            # Check if it's base64 encoded
            if ';base64,' in file_data:
                # Extract base64 data
                header, encoded = file_data.split(';base64,')
                file_data = base64.b64decode(encoded)
            else:
                # Assume it's raw binary data
                file_data = file_data.encode('utf-8')
                
            # Get filename if provided
            filename = request.form.get('filename', 'document')
        else:
            # Get file from request
            file = request.files['file']
            file_data = file.read()
            filename = file.filename
            
        # Get metadata from request
        metadata = request.form.get('metadata', None)
        if metadata:
            import json
            try:
                metadata = json.loads(metadata)
            except json.JSONDecodeError:
                metadata = {'description': metadata}
        else:
            metadata = {}
            
        # Add user info to metadata
        metadata['user_id'] = str(user.id)
        metadata['username'] = user.username
        metadata['email'] = user.email
        metadata['filename'] = filename
            
        # Initialize IPFS service
        ipfs = get_ipfs_service()
        
        # Upload document to IPFS
        result = ipfs.store_document(file_data, metadata)
        
        if 'error' in result:
            return error_response(f"Error uploading to IPFS: {result['error']}", 500)
            
        # Get credential/experience ID if provided
        credential_id = request.form.get('credential_id', None)
        experience_id = request.form.get('experience_id', None)
        
        # If credential ID provided, link document to credential
        if credential_id:
            try:
                # Find credential
                credential = Credential.objects.get(id=credential_id, user=user)
                
                # Initialize document_hashes if needed
                if not hasattr(credential, 'document_hashes') or not credential.document_hashes:
                    credential.document_hashes = {}
                    
                # Add document hash to credential
                doc_name = request.form.get('document_name', filename)
                credential.document_hashes[doc_name] = result['document_hash']
                
                # Add metadata hash to credential
                if 'metadata_hash' in result:
                    credential.ipfs_metadata_hash = result['metadata_hash']
                    
                # Save changes
                credential.save()
                
                # Add credential info to response
                result['credential_id'] = str(credential.id)
                result['credential_title'] = credential.title
            except Credential.DoesNotExist:
                return error_response('Credential not found', 404)
                
        # If experience ID provided, link document to experience
        if experience_id:
            try:
                # Find experience
                experience = Experience.objects.get(id=experience_id, user=user)
                
                # Initialize document_hashes if needed
                if not hasattr(experience, 'document_hashes') or not experience.document_hashes:
                    experience.document_hashes = {}
                    
                # Add document hash to experience
                doc_name = request.form.get('document_name', filename)
                experience.document_hashes[doc_name] = result['document_hash']
                
                # Add metadata hash to experience
                if 'metadata_hash' in result:
                    experience.ipfs_metadata_hash = result['metadata_hash']
                    
                # Save changes
                experience.save()
                
                # Add experience info to response
                result['experience_id'] = str(experience.id)
                result['experience_title'] = experience.title
            except Experience.DoesNotExist:
                return error_response('Experience not found', 404)
        
        # Return result
        return success_response(result)
    except Exception as e:
        logger.error(f"Error uploading document to IPFS: {str(e)}")
        return error_response(f"Error uploading document: {str(e)}", 500)
    finally:
        # Disconnect to avoid keeping connection open
        if ipfs_service:
            ipfs_service.disconnect()

@ipfs_bp.route('/retrieve/<ipfs_hash>', methods=['GET'])
@login_required
def retrieve_document(ipfs_hash):
    """
    Retrieve a document from IPFS.
    
    Args:
        ipfs_hash: IPFS hash of the document
    
    Returns:
        JSON response with document data
    """
    try:
        # Initialize IPFS service
        ipfs = get_ipfs_service()
        
        # Check if metadata hash is provided
        metadata_hash = request.args.get('metadata_hash', None)
        
        # Retrieve document from IPFS
        result = ipfs.retrieve_document(ipfs_hash, metadata_hash)
        
        if 'error' in result:
            return error_response(f"Error retrieving from IPFS: {result['error']}", 404)
            
        # Return result
        return success_response(result)
    except Exception as e:
        logger.error(f"Error retrieving document from IPFS: {str(e)}")
        return error_response(f"Error retrieving document: {str(e)}", 500)
    finally:
        # Disconnect to avoid keeping connection open
        if ipfs_service:
            ipfs_service.disconnect()

@ipfs_bp.route('/pin/<ipfs_hash>', methods=['POST'])
@login_required
def pin_hash(ipfs_hash):
    """
    Pin an IPFS hash to keep it in the IPFS node.
    
    Args:
        ipfs_hash: IPFS hash to pin
    
    Returns:
        JSON response with pin status
    """
    try:
        # Initialize IPFS service
        ipfs = get_ipfs_service()
        
        # Pin hash
        result = ipfs.pin_hash(ipfs_hash)
        
        if 'error' in result:
            return error_response(f"Error pinning IPFS hash: {result['error']}", 500)
            
        # Return result
        return success_response({
            'hash': ipfs_hash,
            'pinned': True,
            'result': result
        })
    except Exception as e:
        logger.error(f"Error pinning IPFS hash: {str(e)}")
        return error_response(f"Error pinning hash: {str(e)}", 500)
    finally:
        # Disconnect to avoid keeping connection open
        if ipfs_service:
            ipfs_service.disconnect()

@ipfs_bp.route('/unpin/<ipfs_hash>', methods=['POST'])
@login_required
def unpin_hash(ipfs_hash):
    """
    Unpin an IPFS hash to allow garbage collection.
    
    Args:
        ipfs_hash: IPFS hash to unpin
    
    Returns:
        JSON response with unpin status
    """
    try:
        # Initialize IPFS service
        ipfs = get_ipfs_service()
        
        # Unpin hash
        result = ipfs.unpin_hash(ipfs_hash)
        
        if 'error' in result:
            return error_response(f"Error unpinning IPFS hash: {result['error']}", 500)
            
        # Return result
        return success_response({
            'hash': ipfs_hash,
            'unpinned': True,
            'result': result
        })
    except Exception as e:
        logger.error(f"Error unpinning IPFS hash: {str(e)}")
        return error_response(f"Error unpinning hash: {str(e)}", 500)
    finally:
        # Disconnect to avoid keeping connection open
        if ipfs_service:
            ipfs_service.disconnect()

@ipfs_bp.route('/credential/<credential_id>/documents', methods=['GET'])
@login_required
def get_credential_documents(credential_id):
    """
    Get all documents associated with a credential.
    
    Args:
        credential_id: ID of the credential
    
    Returns:
        JSON response with document hashes and gateway URLs
    """
    try:
        # Get user from token
        user_id = g.user_id
        
        # Find credential
        try:
            credential = Credential.objects.get(id=credential_id)
            
            # Check if user owns credential or is admin
            if str(credential.user.id) != user_id and not g.is_admin:
                return error_response('Unauthorized access to credential', 403)
                
            # Initialize IPFS service
            ipfs = get_ipfs_service()
            
            # Get document hashes
            document_hashes = getattr(credential, 'document_hashes', {})
            
            # Build response with gateway URLs
            documents = {}
            for doc_name, doc_hash in document_hashes.items():
                documents[doc_name] = {
                    'hash': doc_hash,
                    'gateway_url': ipfs.get_gateway_url(doc_hash)
                }
                
            # Add main IPFS hashes if they exist
            result = {
                'credential_id': str(credential.id),
                'documents': documents
            }
            
            if credential.ipfs_hash:
                result['ipfs_hash'] = credential.ipfs_hash
                result['ipfs_gateway_url'] = ipfs.get_gateway_url(credential.ipfs_hash)
                
            if credential.ipfs_metadata_hash:
                result['metadata_hash'] = credential.ipfs_metadata_hash
                result['metadata_gateway_url'] = ipfs.get_gateway_url(credential.ipfs_metadata_hash)
                
            # Return result
            return success_response(result)
        except Credential.DoesNotExist:
            return error_response('Credential not found', 404)
    except Exception as e:
        logger.error(f"Error getting credential documents: {str(e)}")
        return error_response(f"Error getting documents: {str(e)}", 500)
    finally:
        # Disconnect to avoid keeping connection open
        if ipfs_service:
            ipfs_service.disconnect()

@ipfs_bp.route('/experience/<experience_id>/documents', methods=['GET'])
@login_required
def get_experience_documents(experience_id):
    """
    Get all documents associated with an experience.
    
    Args:
        experience_id: ID of the experience
    
    Returns:
        JSON response with document hashes and gateway URLs
    """
    try:
        # Get user from token
        user_id = g.user_id
        
        # Find experience
        try:
            experience = Experience.objects.get(id=experience_id)
            
            # Check if user owns experience or is admin
            if str(experience.user.id) != user_id and not g.is_admin:
                return error_response('Unauthorized access to experience', 403)
                
            # Initialize IPFS service
            ipfs = get_ipfs_service()
            
            # Get document hashes
            document_hashes = getattr(experience, 'document_hashes', {})
            
            # Build response with gateway URLs
            documents = {}
            for doc_name, doc_hash in document_hashes.items():
                documents[doc_name] = {
                    'hash': doc_hash,
                    'gateway_url': ipfs.get_gateway_url(doc_hash)
                }
                
            # Add main IPFS hashes if they exist
            result = {
                'experience_id': str(experience.id),
                'documents': documents
            }
            
            if experience.ipfs_hash:
                result['ipfs_hash'] = experience.ipfs_hash
                result['ipfs_gateway_url'] = ipfs.get_gateway_url(experience.ipfs_hash)
                
            if experience.ipfs_metadata_hash:
                result['metadata_hash'] = experience.ipfs_metadata_hash
                result['metadata_gateway_url'] = ipfs.get_gateway_url(experience.ipfs_metadata_hash)
                
            # Return result
            return success_response(result)
        except Experience.DoesNotExist:
            return error_response('Experience not found', 404)
    except Exception as e:
        logger.error(f"Error getting experience documents: {str(e)}")
        return error_response(f"Error getting documents: {str(e)}", 500)
    finally:
        # Disconnect to avoid keeping connection open
        if ipfs_service:
            ipfs_service.disconnect()

@ipfs_bp.route('/gateway/<ipfs_hash>', methods=['GET'])
def gateway_redirect(ipfs_hash):
    """
    Get gateway URL for an IPFS hash.
    
    Args:
        ipfs_hash: IPFS hash
    
    Returns:
        Redirect to IPFS gateway URL
    """
    try:
        # Initialize IPFS service
        ipfs = get_ipfs_service()
        
        # Get gateway URL
        gateway_url = ipfs.get_gateway_url(ipfs_hash)
        
        # Redirect to gateway URL
        from flask import redirect
        return redirect(gateway_url)
    except Exception as e:
        logger.error(f"Error redirecting to IPFS gateway: {str(e)}")
        return error_response(f"Error redirecting to gateway: {str(e)}", 500)
    finally:
        # Disconnect to avoid keeping connection open
        if ipfs_service:
            ipfs_service.disconnect()

