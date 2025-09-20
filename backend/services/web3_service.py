"""
Web3 service for TrueCred blockchain integration.

This service provides functionality to interact with TrueCred smart contracts
deployed on various networks.
"""
import os
import json
import logging
from typing import Dict, Any, Tuple, List
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from utils.web3_error_handler import Web3ErrorHandler, Web3TransactionManager

logger = logging.getLogger(__name__)

class Web3Service:
    """
    Service for Web3 integration with TrueCred smart contracts.
    """

    def __init__(self):
        self.web3 = None
        self.contracts = {}
        self.network_configs = {
            'development': {
                'rpc_url': 'http://127.0.0.1:7545',
                'chain_id': 1337,
                'contracts': {}
            },
            'goerli': {
                'rpc_url': f"https://goerli.infura.io/v3/{os.getenv('INFURA_PROJECT_ID', '')}",
                'chain_id': 5,
                'contracts': {}
            },
            'sepolia': {
                'rpc_url': f"https://sepolia.infura.io/v3/{os.getenv('INFURA_PROJECT_ID', '')}",
                'chain_id': 11155111,
                'contracts': {}
            },
            'mainnet': {
                'rpc_url': f"https://mainnet.infura.io/v3/{os.getenv('INFURA_PROJECT_ID', '')}",
                'chain_id': 1,
                'contracts': {}
            }
        }

        # Load contract ABIs
        self._load_contract_abis()

    def _load_contract_abis(self):
        """Load contract ABIs from build files."""
        try:
            build_dir = os.path.join(os.path.dirname(__file__), '..', 'truffle', 'build', 'contracts')

            # Load TrueCred contract
            truecred_path = os.path.join(build_dir, 'TrueCred.json')
            if os.path.exists(truecred_path):
                with open(truecred_path, 'r') as f:
                    truecred_data = json.load(f)
                    self.contracts['TrueCred'] = {
                        'abi': truecred_data['abi'],
                        'bytecode': truecred_data['bytecode']
                    }
                logger.info("TrueCred contract ABI loaded successfully")

            # Load Simple contract
            simple_path = os.path.join(build_dir, 'Simple.json')
            if os.path.exists(simple_path):
                with open(simple_path, 'r') as f:
                    simple_data = json.load(f)
                    self.contracts['Simple'] = {
                        'abi': simple_data['abi'],
                        'bytecode': simple_data['bytecode']
                    }
                logger.info("Simple contract ABI loaded successfully")

        except Exception as e:
            logger.error(f"Error loading contract ABIs: {str(e)}")

    def connect_to_network(self, network_name: str = 'development') -> bool:
        """
        Connect to a blockchain network.

        Args:
            network_name: Name of the network to connect to

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if network_name not in self.network_configs:
                logger.error(f"Unknown network: {network_name}")
                return False

            config = self.network_configs[network_name]
            self.web3 = Web3(Web3.HTTPProvider(config['rpc_url']))

            # Add middleware for PoA networks
            if network_name in ['goerli', 'sepolia']:
                self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)

            # Test connection
            if not self.web3.is_connected():
                logger.error(f"Failed to connect to {network_name} network")
                return False

            logger.info(f"Successfully connected to {network_name} network")
            logger.info(f"Current block number: {self.web3.eth.block_number}")

            return True

        except Exception as e:
            logger.error(f"Error connecting to network {network_name}: {str(e)}")
            return False

    def get_contract_instance(self, contract_name: str, network_name: str = 'development'):
        """
        Get a contract instance for the specified network.

        Args:
            contract_name: Name of the contract
            network_name: Network name

        Returns:
            Contract instance or None if not found
        """
        try:
            if contract_name not in self.contracts:
                logger.error(f"Contract {contract_name} not found")
                return None

            if network_name not in self.network_configs:
                logger.error(f"Network {network_name} not configured")
                return None

            # Get contract address from environment or config
            contract_address = os.getenv(f'{contract_name.upper()}_CONTRACT_ADDRESS')
            if not contract_address:
                logger.error(f"Contract address for {contract_name} not found in environment")
                return None

            contract = self.web3.eth.contract(
                address=self.web3.to_checksum_address(contract_address),
                abi=self.contracts[contract_name]['abi']
            )

            return contract

        except Exception as e:
            logger.error(f"Error getting contract instance: {str(e)}")
            return None

    def store_credential_on_blockchain(
        self,
        title: str,
        student_id: str,
        student_name: str,
        ipfs_hash: str,
        metadata: str = "",
        expiration_date: int = 0,
        credential_type: int = 0,
        issuer_private_key: str = None
    ) -> Tuple[bool, str, str]:
        """
        Store a credential on the blockchain with enhanced error handling.

        Args:
            title: Credential title
            student_id: Student ID
            student_name: Student name
            ipfs_hash: IPFS hash of the document
            metadata: Additional metadata as JSON string
            expiration_date: Expiration timestamp (0 for no expiration)
            credential_type: Type of credential (0-3)
            issuer_private_key: Private key for transaction signing

        Returns:
            Tuple of (success, credential_id, transaction_hash_or_error)
        """
        try:
            contract = self.get_contract_instance('TrueCred')
            if not contract:
                return False, "", "Contract not available"

            if not issuer_private_key:
                return False, "", "Issuer private key required"

            # Prepare transaction data
            account = Account.from_key(issuer_private_key)
            tx_data = contract.functions.storeCredential(
                title,
                student_id,
                student_name,
                ipfs_hash,
                metadata,
                expiration_date,
                credential_type
            ).build_transaction({
                'from': account.address,
                'chainId': self.web3.eth.chain_id
            })

            # Use transaction manager for sending with retry
            tx_manager = Web3TransactionManager(self.web3)
            result = tx_manager.send_transaction_with_retry(
                tx_data,
                issuer_private_key,
                "credential storage"
            )

            if result['success']:
                # Extract credential ID from transaction logs
                receipt = result['receipt']
                credential_id = self._extract_credential_id_from_logs(receipt.logs, contract)
                return True, credential_id, result['transaction_hash']
            else:
                return False, "", result['error']

        except Exception as e:
            error_info = Web3ErrorHandler.handle_transaction_error(e, "credential storage")
            logger.error(f"Error storing credential on blockchain: {error_info['technical_details']}")
            return False, "", error_info['user_message']

    def verify_credential(self, credential_id: str) -> Dict[str, Any]:
        """
        Verify a credential on the blockchain with enhanced error handling.

        Args:
            credential_id: Credential ID to verify

        Returns:
            Dictionary with verification result
        """
        try:
            contract = self.get_contract_instance('TrueCred')
            if not contract:
                return {'valid': False, 'error': 'Contract not available'}

            # Call verify function with error handling
            try:
                result = contract.functions.verifyCredential(bytes.fromhex(credential_id[2:])).call()

                return {
                    'valid': True,
                    'title': result[0],
                    'issuer': result[1],
                    'student_id': result[2],
                    'student_name': result[3],
                    'ipfs_hash': result[4],
                    'metadata': result[5],
                    'timestamp': result[6],
                    'expiration_date': result[7],
                    'is_valid': result[8],
                    'credential_type': result[9]
                }
            except Exception as e:
                error_info = Web3ErrorHandler.handle_contract_call_error(e, "credential verification")
                logger.error(f"Error verifying credential on blockchain: {error_info['technical_details']}")
                return {'valid': False, 'error': error_info['user_message']}

        except Exception as e:
            error_info = Web3ErrorHandler.handle_transaction_error(e, "credential verification")
            logger.error(f"Error verifying credential on blockchain: {error_info['technical_details']}")
            return {'valid': False, 'error': error_info['user_message']}

    def get_credential_details(self, credential_id: str) -> Dict[str, Any]:
        """
        Get detailed credential information from blockchain with enhanced error handling.

        Args:
            credential_id: Credential ID

        Returns:
            Dictionary with credential details
        """
        try:
            contract = self.get_contract_instance('TrueCred')
            if not contract:
                return {'error': 'Contract not available'}

            # Call getCredential function with error handling
            try:
                result = contract.functions.getCredential(bytes.fromhex(credential_id[2:])).call()

                return {
                    'title': result[0],
                    'issuer': result[1],
                    'student_id': result[2],
                    'student_name': result[3],
                    'ipfs_hash': result[4],
                    'metadata': result[5],
                    'timestamp': result[6],
                    'expiration_date': result[7],
                    'is_valid': result[8],
                    'credential_type': result[9]
                }
            except Exception as e:
                error_info = Web3ErrorHandler.handle_contract_call_error(e, "credential details retrieval")
                logger.error(f"Error getting credential details: {error_info['technical_details']}")
                return {'error': error_info['user_message']}

        except Exception as e:
            error_info = Web3ErrorHandler.handle_transaction_error(e, "credential details retrieval")
            logger.error(f"Error getting credential details: {error_info['technical_details']}")
            return {'error': error_info['user_message']}

    def revoke_credential(self, credential_id: str, reason: str, issuer_private_key: str) -> Tuple[bool, str]:
        """
        Revoke a credential on the blockchain with enhanced error handling.

        Args:
            credential_id: Credential ID to revoke
            reason: Reason for revocation
            issuer_private_key: Private key for transaction signing

        Returns:
            Tuple of (success, transaction_hash_or_error)
        """
        try:
            contract = self.get_contract_instance('TrueCred')
            if not contract:
                return False, "Contract not available"

            if not issuer_private_key:
                return False, "Issuer private key required"

            # Prepare transaction data
            account = Account.from_key(issuer_private_key)
            tx_data = contract.functions.revokeCredential(
                bytes.fromhex(credential_id[2:]),
                reason
            ).build_transaction({
                'from': account.address,
                'chainId': self.web3.eth.chain_id
            })

            # Use transaction manager for sending with retry
            tx_manager = Web3TransactionManager(self.web3)
            result = tx_manager.send_transaction_with_retry(
                tx_data,
                issuer_private_key,
                "credential revocation"
            )

            if result['success']:
                return True, result['transaction_hash']
            else:
                return False, result['error']

        except Exception as e:
            error_info = Web3ErrorHandler.handle_transaction_error(e, "credential revocation")
            logger.error(f"Error revoking credential: {error_info['technical_details']}")
            return False, error_info['user_message']

    def get_student_credentials(self, student_id: str) -> List[str]:
        """
        Get all credential IDs for a student.

        Args:
            student_id: Student ID

        Returns:
            List of credential IDs
        """
        try:
            contract = self.get_contract_instance('TrueCred')
            if not contract:
                return []

            credential_ids = contract.functions.getStudentCredentials(student_id).call()
            return [f"0x{id.hex()}" for id in credential_ids]

        except Exception as e:
            logger.error(f"Error getting student credentials: {str(e)}")
            return []

    def authorize_issuer(
        self,
        issuer_address: str,
        issuer_name: str,
        institution: str,
        owner_private_key: str
    ) -> Tuple[bool, str]:
        """
        Authorize a new issuer on the blockchain with enhanced error handling.

        Args:
            issuer_address: Address of the issuer to authorize
            issuer_name: Name of the issuer
            institution: Institution name
            owner_private_key: Owner private key for transaction signing

        Returns:
            Tuple of (success, transaction_hash_or_error)
        """
        try:
            contract = self.get_contract_instance('TrueCred')
            if not contract:
                return False, "Contract not available"

            if not owner_private_key:
                return False, "Owner private key required"

            # Prepare transaction data
            account = Account.from_key(owner_private_key)
            tx_data = contract.functions.authorizeIssuer(
                self.web3.to_checksum_address(issuer_address),
                issuer_name,
                institution
            ).build_transaction({
                'from': account.address,
                'chainId': self.web3.eth.chain_id
            })

            # Use transaction manager for sending with retry
            tx_manager = Web3TransactionManager(self.web3)
            result = tx_manager.send_transaction_with_retry(
                tx_data,
                owner_private_key,
                "issuer authorization"
            )

            if result['success']:
                return True, result['transaction_hash']
            else:
                return False, result['error']

        except Exception as e:
            error_info = Web3ErrorHandler.handle_transaction_error(e, "issuer authorization")
            logger.error(f"Error authorizing issuer: {error_info['technical_details']}")
            return False, error_info['user_message']

    def _extract_credential_id_from_logs(self, logs, contract) -> str:
        """Extract credential ID from transaction logs."""
        try:
            for log in logs:
                if log['address'].lower() == contract.address.lower():
                    # Parse the CredentialStored event
                    event = contract.events.CredentialStored().process_log(log)
                    return f"0x{event.args.credentialId.hex()}"
            return ""
        except Exception as e:
            logger.error(f"Error extracting credential ID from logs: {str(e)}")
            return ""

    def get_network_info(self) -> Dict[str, Any]:
        """Get current network information."""
        if not self.web3 or not self.web3.is_connected():
            return {'connected': False}

        return {
            'connected': True,
            'chain_id': self.web3.eth.chain_id,
            'block_number': self.web3.eth.block_number,
            'gas_price': self.web3.eth.gas_price
        }

# Global Web3 service instance
web3_service = Web3Service()