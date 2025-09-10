"""Service for blockchain wallet authentication."""
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
import logging
from datetime import datetime, timedelta
import jwt
from config import get_config

logger = logging.getLogger(__name__)

class WalletAuthService:
    """Service for handling blockchain wallet authentication."""
    
    def __init__(self):
        """Initialize the wallet authentication service."""
        self.config = get_config()
        self.web3 = Web3()
    
    def generate_nonce(self, address: str) -> str:
        """Generate a nonce for wallet authentication."""
        timestamp = datetime.utcnow().isoformat()
        return f"Welcome to TrueCred! Please sign this message to verify your ownership of the address: {address}\n\nTimestamp: {timestamp}"
    
    def verify_signature(self, address: str, signature: str, message: str) -> bool:
        """Verify a signature against a message and address."""
        try:
            # Recover the address from the signature
            message_hash = encode_defunct(text=message)
            recovered_address = Account.recover_message(message_hash, signature=signature)
            
            # Check if the recovered address matches
            return recovered_address.lower() == address.lower()
            
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False
    
    def generate_auth_tokens(self, address: str, role: str = 'user') -> dict:
        """Generate JWT tokens for authenticated wallet."""
        try:
            # Access token
            access_token = jwt.encode(
                {
                    'wallet_address': address,
                    'role': role,
                    'exp': datetime.utcnow() + self.config.JWT_ACCESS_TOKEN_EXPIRES
                },
                self.config.JWT_SECRET_KEY,
                algorithm='HS256'
            )
            
            # Refresh token
            refresh_token = jwt.encode(
                {
                    'wallet_address': address,
                    'exp': datetime.utcnow() + self.config.JWT_REFRESH_TOKEN_EXPIRES
                },
                self.config.JWT_SECRET_KEY,
                algorithm='HS256'
            )
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            
        except Exception as e:
            logger.error(f"Error generating tokens: {e}")
            return None
