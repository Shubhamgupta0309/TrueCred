"""
Blockchain routes for the TrueCred application.
"""
from flask import Blueprint, request, jsonify, g
from mongoengine.errors import DoesNotExist, ValidationError

from models.credential import Credential
from models.experience import Experience
from services.digital_signature_service import DigitalSignatureService
from services.blockchain_service import BlockchainService
from middleware.auth_middleware import login_required, role_required
from utils.response import success_response, error_response

blockchain_bp = Blueprint('blockchain', __name__, url_prefix='/api/blockchain')

# Initialize blockchain service
blockchain_service = BlockchainService()

@blockchain_bp.route('/credentials/<credential_id>/prepare', methods=['POST'])
@login_required
def prepare_credential_for_blockchain(credential_id):
    """
    Prepare a credential for blockchain by generating its hash.
    
    Args:
        credential_id: ID of the credential to prepare
        
    Returns:
        JSON response with blockchain-ready credential data
    """
    try:
        user_id = g.user_id
        
        # Get the credential
        credential = Credential.objects.get(id=credential_id)
        
        # Ensure user owns the credential or has admin privileges
        if str(credential.user.id) != user_id and 'admin' not in g.user_roles:
            return error_response(message="You don't have permission to prepare this credential", status_code=403)
        
        # Ensure credential is verified
        if not credential.verified:
            return error_response(message="Credential must be verified before preparing for blockchain", status_code=400)
        
        # Prepare credential for blockchain
        blockchain_data = DigitalSignatureService.prepare_credential_for_blockchain(credential)
        
        # Update credential with blockchain data
        DigitalSignatureService.update_credential_blockchain_data(credential, blockchain_data)
        
        return success_response(
            message="Credential prepared for blockchain successfully",
            data={
                'credential_id': str(credential.id),
                'data_hash': blockchain_data['data_hash'],
                'timestamp': blockchain_data['timestamp'],
                'blockchain_ready': True
            }
        )
    except DoesNotExist:
        return error_response(message="Credential not found", status_code=404)
    except Exception as e:
        return error_response(message=f"Error preparing credential for blockchain: {str(e)}", status_code=500)

@blockchain_bp.route('/experiences/<experience_id>/prepare', methods=['POST'])
@login_required
def prepare_experience_for_blockchain(experience_id):
    """
    Prepare an experience for blockchain by generating its hash.
    
    Args:
        experience_id: ID of the experience to prepare
        
    Returns:
        JSON response with blockchain-ready experience data
    """
    try:
        user_id = g.user_id
        
        # Get the experience
        experience = Experience.objects.get(id=experience_id)
        
        # Ensure user owns the experience or has admin privileges
        if str(experience.user.id) != user_id and 'admin' not in g.user_roles:
            return error_response(message="You don't have permission to prepare this experience", status_code=403)
        
        # Ensure experience is verified
        if not experience.is_verified:
            return error_response(message="Experience must be verified before preparing for blockchain", status_code=400)
        
        # Prepare experience for blockchain
        blockchain_data = DigitalSignatureService.prepare_experience_for_blockchain(experience)
        
        # Update experience with blockchain data
        DigitalSignatureService.update_experience_blockchain_data(experience, blockchain_data)
        
        return success_response(
            message="Experience prepared for blockchain successfully",
            data={
                'experience_id': str(experience.id),
                'data_hash': blockchain_data['data_hash'],
                'timestamp': blockchain_data['timestamp'],
                'blockchain_ready': True
            }
        )
    except DoesNotExist:
        return error_response(message="Experience not found", status_code=404)
    except Exception as e:
        return error_response(message=f"Error preparing experience for blockchain: {str(e)}", status_code=500)

@blockchain_bp.route('/credentials/<credential_id>/store', methods=['POST'])
@login_required
@role_required(['admin', 'issuer'])
def store_credential_on_blockchain(credential_id):
    """
    Store a credential hash on the blockchain.
    
    Args:
        credential_id: ID of the credential to store
        
    Returns:
        JSON response with transaction details
    """
    try:
        # Get the credential
        credential = Credential.objects.get(id=credential_id)
        
        # Check if the credential has a blockchain hash
        if not credential.blockchain_hash:
            # If not, prepare it
            blockchain_data = DigitalSignatureService.prepare_credential_for_blockchain(credential)
            credential = DigitalSignatureService.update_credential_blockchain_data(credential, blockchain_data)
        
        # Store the credential hash on the blockchain
        transaction = blockchain_service.store_credential_hash(
            credential_id=str(credential.id),
            data_hash=credential.blockchain_hash
        )
        
        # Update credential with transaction data
        if not hasattr(credential, 'blockchain_data') or not credential.blockchain_data:
            credential.blockchain_data = {}
        
        credential.blockchain_data.update({
            'transaction_hash': transaction['transaction_hash'],
            'block_number': transaction['block_number'],
            'timestamp': transaction['timestamp'],
            'network': transaction['network'],
            'status': transaction['status']
        })
        
        credential.save()
        
        return success_response(
            message="Credential stored on blockchain successfully",
            data={
                'credential_id': str(credential.id),
                'transaction_hash': transaction['transaction_hash'],
                'block_number': transaction['block_number'],
                'network': transaction['network'],
                'status': transaction['status']
            }
        )
    except DoesNotExist:
        return error_response(message="Credential not found", status_code=404)
    except Exception as e:
        return error_response(message=f"Error storing credential on blockchain: {str(e)}", status_code=500)

@blockchain_bp.route('/experiences/<experience_id>/store', methods=['POST'])
@login_required
@role_required(['admin', 'verifier'])
def store_experience_on_blockchain(experience_id):
    """
    Store an experience hash on the blockchain.
    
    Args:
        experience_id: ID of the experience to store
        
    Returns:
        JSON response with transaction details
    """
    try:
        # Get the experience
        experience = Experience.objects.get(id=experience_id)
        
        # Check if the experience has blockchain data
        has_blockchain_data = (
            hasattr(experience, 'metadata') and 
            experience.metadata and 
            'blockchain' in experience.metadata and
            'hash' in experience.metadata['blockchain']
        )
        
        if not has_blockchain_data:
            # If not, prepare it
            blockchain_data = DigitalSignatureService.prepare_experience_for_blockchain(experience)
            experience = DigitalSignatureService.update_experience_blockchain_data(experience, blockchain_data)
        
        # Get the hash from metadata
        data_hash = experience.metadata.get('blockchain', {}).get('hash')
        
        if not data_hash:
            return error_response(message="Experience does not have a valid blockchain hash", status_code=400)
        
        # Store the experience hash on the blockchain
        transaction = blockchain_service.store_experience_hash(
            experience_id=str(experience.id),
            data_hash=data_hash
        )
        
        # Update experience with transaction data
        if not hasattr(experience, 'metadata') or not experience.metadata:
            experience.metadata = {}
        
        if 'blockchain' not in experience.metadata:
            experience.metadata['blockchain'] = {}
        
        experience.metadata['blockchain'].update({
            'transaction_hash': transaction['transaction_hash'],
            'block_number': transaction['block_number'],
            'timestamp': transaction['timestamp'],
            'network': transaction['network'],
            'status': transaction['status']
        })
        
        experience.save()
        
        return success_response(
            message="Experience stored on blockchain successfully",
            data={
                'experience_id': str(experience.id),
                'transaction_hash': transaction['transaction_hash'],
                'block_number': transaction['block_number'],
                'network': transaction['network'],
                'status': transaction['status']
            }
        )
    except DoesNotExist:
        return error_response(message="Experience not found", status_code=404)
    except Exception as e:
        return error_response(message=f"Error storing experience on blockchain: {str(e)}", status_code=500)

@blockchain_bp.route('/credentials/<credential_id>/verify', methods=['GET'])
@login_required
def verify_credential_on_blockchain(credential_id):
    """
    Verify a credential against the blockchain.
    
    Args:
        credential_id: ID of the credential to verify
        
    Returns:
        JSON response with verification result
    """
    try:
        # Get the credential
        credential = Credential.objects.get(id=credential_id)
        
        # Check if the credential has a blockchain hash
        if not credential.blockchain_hash:
            return error_response(message="Credential is not stored on the blockchain", status_code=400)
        
        # Check if credential has transaction data
        has_transaction_data = (
            hasattr(credential, 'blockchain_data') and 
            credential.blockchain_data and 
            'transaction_hash' in credential.blockchain_data
        )
        
        if not has_transaction_data:
            return error_response(message="Credential is prepared but not stored on the blockchain", status_code=400)
        
        # Prepare credential data (to verify hash hasn't changed)
        blockchain_data = DigitalSignatureService.prepare_credential_for_blockchain(credential)
        current_hash = blockchain_data['data_hash']
        
        # Verify against the blockchain
        is_verified = blockchain_service.verify_credential_hash(
            credential_id=str(credential.id),
            data_hash=current_hash
        )
        
        # Hash matching check
        hash_matches = (current_hash == credential.blockchain_hash)
        
        return success_response(
            message="Credential verification completed",
            data={
                'credential_id': str(credential.id),
                'is_verified_on_blockchain': is_verified,
                'hash_matches': hash_matches,
                'current_hash': current_hash,
                'stored_hash': credential.blockchain_hash
            }
        )
    except DoesNotExist:
        return error_response(message="Credential not found", status_code=404)
    except Exception as e:
        return error_response(message=f"Error verifying credential on blockchain: {str(e)}", status_code=500)

@blockchain_bp.route('/experiences/<experience_id>/verify', methods=['GET'])
@login_required
def verify_experience_on_blockchain(experience_id):
    """
    Verify an experience against the blockchain.
    
    Args:
        experience_id: ID of the experience to verify
        
    Returns:
        JSON response with verification result
    """
    try:
        # Get the experience
        experience = Experience.objects.get(id=experience_id)
        
        # Check if the experience has blockchain data
        has_blockchain_data = (
            hasattr(experience, 'metadata') and 
            experience.metadata and 
            'blockchain' in experience.metadata and
            'hash' in experience.metadata['blockchain']
        )
        
        if not has_blockchain_data:
            return error_response(message="Experience is not stored on the blockchain", status_code=400)
        
        # Check if experience has transaction data
        has_transaction_data = (
            hasattr(experience, 'metadata') and 
            experience.metadata and 
            'blockchain' in experience.metadata and
            'transaction_hash' in experience.metadata['blockchain']
        )
        
        if not has_transaction_data:
            return error_response(message="Experience is prepared but not stored on the blockchain", status_code=400)
        
        # Get the stored hash
        stored_hash = experience.metadata['blockchain']['hash']
        
        # Prepare experience data (to verify hash hasn't changed)
        blockchain_data = DigitalSignatureService.prepare_experience_for_blockchain(experience)
        current_hash = blockchain_data['data_hash']
        
        # Verify against the blockchain
        is_verified = blockchain_service.verify_experience_hash(
            experience_id=str(experience.id),
            data_hash=current_hash
        )
        
        # Hash matching check
        hash_matches = (current_hash == stored_hash)
        
        return success_response(
            message="Experience verification completed",
            data={
                'experience_id': str(experience.id),
                'is_verified_on_blockchain': is_verified,
                'hash_matches': hash_matches,
                'current_hash': current_hash,
                'stored_hash': stored_hash
            }
        )
    except DoesNotExist:
        return error_response(message="Experience not found", status_code=404)
    except Exception as e:
        return error_response(message=f"Error verifying experience on blockchain: {str(e)}", status_code=500)

@blockchain_bp.route('/transaction/<transaction_hash>', methods=['GET'])
@login_required
def get_transaction_status(transaction_hash):
    """
    Get the status of a blockchain transaction.
    
    Args:
        transaction_hash: Hash of the transaction
        
    Returns:
        JSON response with transaction status
    """
    try:
        # Get the transaction status
        status = blockchain_service.get_transaction_status(transaction_hash)
        
        return success_response(
            message="Transaction status retrieved",
            data=status
        )
    except Exception as e:
        return error_response(message=f"Error getting transaction status: {str(e)}", status_code=500)
