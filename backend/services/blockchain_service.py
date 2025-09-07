"""
Blockchain service for the TrueCred application.

This service provides functionality to interact with Ethereum blockchain
for storing and verifying credential and experience hashes.
"""
import json
import time
import logging
import os
from datetime import datetime
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.signers.local import LocalAccount

# Set up logging
logger = logging.getLogger(__name__)

class BlockchainService:
    """
    Service for interacting with the Ethereum blockchain for TrueCred.
    
    This service provides:
    - Ethereum testnet integration 
    - Credential hash storage and verification
    - Experience hash storage and verification
    - Transaction status tracking
    """
    
    def __init__(self, contract_address=None, contract_abi=None, network='goerli'):
        """
        Initialize the blockchain service.
        
        Args:
            contract_address (str, optional): Address of deployed contract
            contract_abi (dict, optional): ABI of the deployed contract
            network (str): Network to use ('goerli', 'sepolia', 'mainnet')
        """
        # Load configuration
        self.network = network
        self.contract_address = contract_address or os.getenv('CONTRACT_ADDRESS')
        self.provider_url = os.getenv('ETHEREUM_PROVIDER_URL', f'https://{network}.infura.io/v3/{os.getenv("INFURA_API_KEY", "")}')
        self.private_key = os.getenv('ETHEREUM_PRIVATE_KEY')
        self.chain_id = int(os.getenv('ETHEREUM_CHAIN_ID', self._get_chain_id(network)))
        
        # Load contract ABI
        if contract_abi:
            self.contract_abi = contract_abi
        else:
            try:
                with open(os.path.join(os.path.dirname(__file__), '../contracts/build/TrueCred.json'), 'r') as f:
                    contract_data = json.load(f)
                    self.contract_abi = contract_data['abi']
            except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error loading contract ABI: {str(e)}")
                self.contract_abi = None
        
        # Initialize Web3 connection
        try:
            self.web3 = Web3(Web3.HTTPProvider(self.provider_url))
            
            # Add middleware for testnet compatibility
            if network in ['goerli', 'sepolia']:
                self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            # Set up account if private key is available
            if self.private_key:
                self.account = Account.from_key(self.private_key)
                logger.info(f"Account loaded: {self.account.address}")
            else:
                self.account = None
                logger.warning("No private key provided. Transactions will not be possible.")
            
            # Set up contract if address and ABI are available
            if self.contract_address and self.contract_abi:
                self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.contract_abi)
                logger.info(f"Contract loaded at {self.contract_address}")
            else:
                self.contract = None
                logger.warning("Contract not loaded. Check address and ABI.")
            
            logger.info(f"Connected to Ethereum {network} network. Chain ID: {self.chain_id}")
        except Exception as e:
            logger.error(f"Failed to initialize blockchain service: {str(e)}")
            self.web3 = None
            self.contract = None
            self.account = None
            
    def _get_chain_id(self, network):
        """Get the chain ID for a given network."""
        chain_ids = {
            'mainnet': 1,
            'goerli': 5,
            'sepolia': 11155111,
        }
        return chain_ids.get(network, 5)  # Default to Goerli
    
    def store_credential_hash(self, credential_id, data_hash, issuer_address=None):
        """
        Store a credential hash on the blockchain.
        
        Args:
            credential_id (str): ID of the credential
            data_hash (str): Hash of credential data
            issuer_address (str, optional): Ethereum address of issuer
            
        Returns:
            dict: Transaction information
        """
        if not self.web3 or not self.contract or not self.account:
            logger.error("Blockchain service not properly initialized")
            return self._mock_transaction_data(credential_id, data_hash, issuer_address, 'failed')
        
        try:
            # Use the account address if no issuer address is provided
            issuer_address = issuer_address or self.account.address
            
            # Build transaction
            tx = self.contract.functions.storeCredentialHash(
                credential_id,
                data_hash
            ).build_transaction({
                'chainId': self.chain_id,
                'gas': 2000000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.account.address),
                'from': self.account.address
            })
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            logger.info(f"Transaction sent: {tx_hash.hex()}")
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            # Get block information
            block = self.web3.eth.get_block(receipt.blockNumber)
            
            # Create transaction data
            transaction = {
                'credential_id': credential_id,
                'data_hash': data_hash,
                'issuer_address': issuer_address,
                'transaction_hash': receipt.transactionHash.hex(),
                'block_number': receipt.blockNumber,
                'timestamp': datetime.utcfromtimestamp(block.timestamp).isoformat(),
                'network': self.network,
                'status': 'confirmed' if receipt.status == 1 else 'failed',
                'gas_used': receipt.gasUsed
            }
            
            logger.info(f"Credential hash stored on blockchain. Transaction: {transaction['transaction_hash']}")
            return transaction
            
        except Exception as e:
            logger.error(f"Error storing credential hash: {str(e)}")
            return self._mock_transaction_data(credential_id, data_hash, issuer_address, 'failed')
    
    def _mock_transaction_data(self, item_id, data_hash, address=None, status='pending'):
        """Create mock transaction data when actual blockchain interaction fails."""
        return {
            'item_id': item_id,
            'data_hash': data_hash,
            'address': address or '0x0000000000000000000000000000000000000000',
            'transaction_hash': f"0x{data_hash[:40]}",  # Mock transaction hash
            'block_number': 0,
            'timestamp': datetime.utcnow().isoformat(),
            'network': self.network,
            'status': status,
            'error': 'Blockchain service not properly initialized or connection failed',
            'is_mock': True
        }
    
    def store_experience_hash(self, experience_id, data_hash, verifier_address=None):
        """
        Store an experience hash on the blockchain.
        
        Args:
            experience_id (str): ID of the experience
            data_hash (str): Hash of experience data
            verifier_address (str, optional): Ethereum address of verifier
            
        Returns:
            dict: Transaction information
        """
        if not self.web3 or not self.contract or not self.account:
            logger.error("Blockchain service not properly initialized")
            return self._mock_transaction_data(experience_id, data_hash, verifier_address, 'failed')
        
        try:
            # Use the account address if no verifier address is provided
            verifier_address = verifier_address or self.account.address
            
            # Build transaction
            tx = self.contract.functions.storeExperienceHash(
                experience_id,
                data_hash
            ).build_transaction({
                'chainId': self.chain_id,
                'gas': 2000000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.account.address),
                'from': self.account.address
            })
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            logger.info(f"Transaction sent: {tx_hash.hex()}")
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            # Get block information
            block = self.web3.eth.get_block(receipt.blockNumber)
            
            # Create transaction data
            transaction = {
                'experience_id': experience_id,
                'data_hash': data_hash,
                'verifier_address': verifier_address,
                'transaction_hash': receipt.transactionHash.hex(),
                'block_number': receipt.blockNumber,
                'timestamp': datetime.utcfromtimestamp(block.timestamp).isoformat(),
                'network': self.network,
                'status': 'confirmed' if receipt.status == 1 else 'failed',
                'gas_used': receipt.gasUsed
            }
            
            logger.info(f"Experience hash stored on blockchain. Transaction: {transaction['transaction_hash']}")
            return transaction
            
        except Exception as e:
            logger.error(f"Error storing experience hash: {str(e)}")
            return self._mock_transaction_data(experience_id, data_hash, verifier_address, 'failed')
    
    def verify_credential_hash(self, credential_id, data_hash):
        """
        Verify a credential hash against the blockchain.
        
        Args:
            credential_id (str): ID of the credential
            data_hash (str): Hash to verify
            
        Returns:
            bool: True if verified, False otherwise
        """
        if not self.web3 or not self.contract:
            logger.error("Blockchain service not properly initialized")
            return False
        
        try:
            # Call the contract to get the stored hash
            stored_hash = self.contract.functions.getCredentialHash(credential_id).call()
            
            # Compare with the provided hash
            is_verified = (stored_hash == data_hash)
            logger.info(f"Credential hash verification for {credential_id}: {'Successful' if is_verified else 'Failed'}")
            
            # Also check if the credential is revoked
            is_revoked = self.contract.functions.isCredentialRevoked(credential_id).call()
            if is_revoked:
                logger.warning(f"Credential {credential_id} is revoked")
                return False
            
            return is_verified
            
        except Exception as e:
            logger.error(f"Error verifying credential hash: {str(e)}")
            return False
    
    def verify_experience_hash(self, experience_id, data_hash):
        """
        Verify an experience hash against the blockchain.
        
        Args:
            experience_id (str): ID of the experience
            data_hash (str): Hash to verify
            
        Returns:
            bool: True if verified, False otherwise
        """
        if not self.web3 or not self.contract:
            logger.error("Blockchain service not properly initialized")
            return False
        
        try:
            # Call the contract to get the stored hash
            stored_hash = self.contract.functions.getExperienceHash(experience_id).call()
            
            # Compare with the provided hash
            is_verified = (stored_hash == data_hash)
            logger.info(f"Experience hash verification for {experience_id}: {'Successful' if is_verified else 'Failed'}")
            return is_verified
            
        except Exception as e:
            logger.error(f"Error verifying experience hash: {str(e)}")
            return False
    
    def get_transaction_status(self, transaction_hash):
        """
        Get the status of a blockchain transaction.
        
        Args:
            transaction_hash (str): Hash of the transaction
            
        Returns:
            dict: Transaction status information
        """
        if not self.web3:
            logger.error("Blockchain service not properly initialized")
            return {
                'transaction_hash': transaction_hash,
                'status': 'unknown',
                'error': 'Blockchain service not properly initialized'
            }
        
        try:
            # Get transaction receipt
            receipt = self.web3.eth.get_transaction_receipt(transaction_hash)
            
            if not receipt:
                # Transaction is pending
                return {
                    'transaction_hash': transaction_hash,
                    'status': 'pending',
                    'confirmations': 0
                }
            
            # Get block information
            block = self.web3.eth.get_block(receipt['blockNumber'])
            current_block = self.web3.eth.block_number
            confirmations = current_block - receipt['blockNumber'] + 1
            
            # Status information
            status = {
                'transaction_hash': transaction_hash,
                'block_number': receipt['blockNumber'],
                'block_hash': receipt['blockHash'].hex(),
                'gas_used': receipt['gasUsed'],
                'status': 'confirmed' if receipt['status'] == 1 else 'failed',
                'confirmations': confirmations,
                'timestamp': datetime.utcfromtimestamp(block['timestamp']).isoformat(),
                'network': self.network
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting transaction status: {str(e)}")
            return {
                'transaction_hash': transaction_hash,
                'status': 'error',
                'error': str(e)
            }
    
    def get_contract_events(self, event_name, from_block=0, to_block='latest'):
        """
        Get events emitted by the smart contract.
        
        Args:
            event_name (str): Name of the event to filter by
            from_block (int): Starting block number
            to_block (str/int): Ending block number
            
        Returns:
            list: List of events
        """
        if not self.web3 or not self.contract:
            logger.error("Blockchain service not properly initialized")
            return []
        
        try:
            # Get the event filter
            event = getattr(self.contract.events, event_name)
            if not event:
                logger.error(f"Event {event_name} not found in contract")
                return []
            
            # Get logs for the event
            logs = event.get_logs(fromBlock=from_block, toBlock=to_block)
            
            # Process logs to get event data
            events = []
            for log in logs:
                # Get block information for timestamp
                block = self.web3.eth.get_block(log['blockNumber'])
                
                # Create event data
                event_data = {
                    'event': event_name,
                    'args': dict(log['args']),
                    'block_number': log['blockNumber'],
                    'transaction_hash': log['transactionHash'].hex(),
                    'log_index': log['logIndex'],
                    'timestamp': datetime.utcfromtimestamp(block['timestamp']).isoformat()
                }
                
                events.append(event_data)
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting contract events: {str(e)}")
            return []
    
    def revoke_credential(self, credential_id, reason=None):
        """
        Revoke a credential on the blockchain.
        
        Args:
            credential_id (str): ID of the credential to revoke
            reason (str, optional): Reason for revocation
            
        Returns:
            dict: Transaction information
        """
        if not self.web3 or not self.contract or not self.account:
            logger.error("Blockchain service not properly initialized")
            return {
                'status': 'failed',
                'error': 'Blockchain service not properly initialized'
            }
        
        try:
            # Build transaction
            tx = self.contract.functions.revokeCredential(
                credential_id,
                reason or "Credential revoked"
            ).build_transaction({
                'chainId': self.chain_id,
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.account.address),
                'from': self.account.address
            })
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            logger.info(f"Revocation transaction sent: {tx_hash.hex()}")
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            # Get block information
            block = self.web3.eth.get_block(receipt.blockNumber)
            
            # Create transaction data
            transaction = {
                'credential_id': credential_id,
                'transaction_hash': receipt.transactionHash.hex(),
                'block_number': receipt.blockNumber,
                'timestamp': datetime.utcfromtimestamp(block.timestamp).isoformat(),
                'network': self.network,
                'status': 'confirmed' if receipt.status == 1 else 'failed',
                'gas_used': receipt.gasUsed,
                'reason': reason
            }
            
            logger.info(f"Credential revoked on blockchain. Transaction: {transaction['transaction_hash']}")
            return transaction
            
        except Exception as e:
            logger.error(f"Error revoking credential: {str(e)}")
            return {
                'credential_id': credential_id,
                'status': 'failed',
                'error': str(e)
            }
