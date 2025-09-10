"""Routes for wallet-based authentication."""
from flask import Blueprint, request
from utils.api_response import success_response, error_response
from utils.database import get_db
from services.wallet_auth_service import WalletAuthService

wallet_auth_bp = Blueprint('wallet_auth', __name__, url_prefix='/api/auth')

@wallet_auth_bp.route('/wallet-auth', methods=['POST'])
def wallet_auth():
    """Authenticate using a blockchain wallet."""
    data = request.get_json()
    if not data or 'address' not in data:
        return error_response('Missing wallet address', 400)
    
    wallet_service = WalletAuthService()
    
    # If signature is provided, verify it
    if 'signature' in data and 'message' in data:
        if not wallet_service.verify_signature(data['address'], data['signature'], data['message']):
            return error_response('Invalid signature', 401)
        
        # Generate tokens
        tokens = wallet_service.generate_auth_tokens(data['address'])
        if not tokens:
            return error_response('Failed to generate tokens', 500)
        
        return success_response(data=tokens)
    
    # If no signature, generate nonce
    nonce = wallet_service.generate_nonce(data['address'])
    return success_response(data={'message': nonce})
