#!/usr/bin/env python3
"""
Blockchain Service for TrueCred
Provides functionality for interacting with the TrueCred smart contract on Ethereum.
"""
import json
import os
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BlockchainService:
    """Service for interacting with the TrueCred smart contract."""
    
    def __init__(self):
        """Initialize the blockchain service."""
        # Get configuration from environment
        self.infura_project_id = os.getenv("INFURA_PROJECT_ID")
        self.ethereum_network = os.getenv("ETHEREUM_NETWORK", "goerli")
        self.contract_address = os.getenv("CONTRACT_ADDRESS")
        self.private_key = os.getenv("BLOCKCHAIN_PRIVATE_KEY")
        
        # Initialize Web3 connection
        self.web3 = self._initialize_web3()
        
        # Load contract ABI
        self.contract = self._load_contract()
        
        # Set up account from private key if available
        self.account = None
        if self.private_key:
            self.account = Account.from_key(self.private_key)
    
    def _initialize_web3(self) -> Web3:
        """Initialize Web3 connection to Ethereum network."""
        if self.infura_project_id and self.infura_project_id != "your_infura_project_id":
            # Use Infura for Ethereum network access
            provider_url = f"https://{self.ethereum_network}.infura.io/v3/{self.infura_project_id}"
            web3 = Web3(Web3.HTTPProvider(provider_url))
        else:
            # Use local node for testing (e.g., Ganache)
            web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
        
        # Add middleware for PoA networks (e.g., Goerli)
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        return web3
    
    def _load_contract(self) -> Optional[Any]:
        """Load the TrueCred contract."""
        if not self.web3.is_connected():
            return None
            
        if not self.contract_address or self.contract_address == "0x0000000000000000000000000000000000000000":
            return None
            
        # Load ABI from contract build file
        contract_path = Path(__file__).parent / "build" / "TrueCred.json"
        if not contract_path.exists():
            return None
            
        with open(contract_path, "r") as f:
            contract_data = json.load(f)
            
        contract_abi = contract_data["abi"]
        
        # Return contract instance
        return self.web3.eth.contract(
            address=self.web3.to_checksum_address(self.contract_address), 
            abi=contract_abi
        )
    
    def is_connected(self) -> bool:
        """Check if connected to Ethereum network."""
        return self.web3.is_connected() and self.contract is not None
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get detailed connection status."""
        is_connected = self.web3.is_connected()
        contract_loaded = self.contract is not None
        has_account = self.account is not None
        
        result = {
            "web3_connected": is_connected,
            "contract_loaded": contract_loaded,
            "has_account": has_account,
            "network": self.ethereum_network,
            "contract_address": self.contract_address if contract_loaded else None,
        }
        
        if is_connected:
            result["block_number"] = self.web3.eth.block_number
            
            if has_account:
                account_address = self.account.address
                result["account_address"] = account_address
                result["account_balance"] = self.web3.from_wei(
                    self.web3.eth.get_balance(account_address), 
                    "ether"
                )
        
        return result
    
    def generate_credential_id(self, credential_data: Dict[str, Any]) -> bytes:
        """Generate a unique identifier for a credential."""
        # Create a deterministic ID based on credential data
        data_string = f"{credential_data['issuer']}:{credential_data['recipient']}:{credential_data['title']}:{credential_data['issue_date']}"
        
        # Hash the data
        hash_bytes = hashlib.sha256(data_string.encode()).digest()
        
        return hash_bytes
    
    def issue_credential(
        self,
        subject: str,
        credential_type: str,
        metadata_uri: str,
        expiration_date: int = 0
    ) -> Optional[Dict[str, Any]]:
        """Issue a new credential on the blockchain."""
        if not self.is_connected() or not self.account:
            return None
            
        try:
            # Convert addresses to checksum format
            subject_address = self.web3.to_checksum_address(subject)
            issuer_address = self.account.address
            
            # Generate credential ID
            credential_data = {
                "issuer": issuer_address,
                "recipient": subject_address,
                "title": credential_type,
                "issue_date": self.web3.eth.get_block('latest').timestamp
            }
            credential_id = self.generate_credential_id(credential_data)
            
            # Estimate gas for the transaction
            gas_estimate = self.contract.functions.issueCredential(
                credential_id,
                subject_address,
                credential_type,
                metadata_uri,
                expiration_date
            ).estimate_gas({
                "from": issuer_address
            })
            
            # Get current gas price
            gas_price = self.web3.eth.gas_price
            
            # Build transaction
            nonce = self.web3.eth.get_transaction_count(issuer_address)
            transaction = self.contract.functions.issueCredential(
                credential_id,
                subject_address,
                credential_type,
                metadata_uri,
                expiration_date
            ).build_transaction({
                "from": issuer_address,
                "gas": gas_estimate,
                "gasPrice": gas_price,
                "nonce": nonce
            })
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(
                transaction, 
                private_key=self.private_key
            )
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "transaction_hash": self.web3.to_hex(tx_hash),
                "block_number": tx_receipt.blockNumber,
                "gas_used": tx_receipt.gasUsed,
                "credential_id": self.web3.to_hex(credential_id),
                "status": "success" if tx_receipt.status == 1 else "failed"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def batch_issue_credentials(
        self,
        subjects: List[str],
        credential_types: List[str],
        metadata_uris: List[str],
        expiration_dates: List[int]
    ) -> Optional[Dict[str, Any]]:
        """Issue multiple credentials in a batch."""
        if not self.is_connected() or not self.account:
            return None
            
        # Validate input arrays have the same length
        if not (len(subjects) == len(credential_types) == len(metadata_uris) == len(expiration_dates)):
            return {
                "status": "error",
                "error": "Input arrays must have the same length"
            }
            
        try:
            # Convert addresses to checksum format
            subject_addresses = [self.web3.to_checksum_address(subject) for subject in subjects]
            issuer_address = self.account.address
            
            # Generate credential IDs
            credential_ids = []
            for i, subject in enumerate(subject_addresses):
                credential_data = {
                    "issuer": issuer_address,
                    "recipient": subject,
                    "title": credential_types[i],
                    "issue_date": self.web3.eth.get_block('latest').timestamp
                }
                credential_id = self.generate_credential_id(credential_data)
                credential_ids.append(credential_id)
            
            # Estimate gas for the transaction
            gas_estimate = self.contract.functions.batchIssueCredentials(
                credential_ids,
                subject_addresses,
                credential_types,
                metadata_uris,
                expiration_dates
            ).estimate_gas({
                "from": issuer_address
            })
            
            # Get current gas price
            gas_price = self.web3.eth.gas_price
            
            # Build transaction
            nonce = self.web3.eth.get_transaction_count(issuer_address)
            transaction = self.contract.functions.batchIssueCredentials(
                credential_ids,
                subject_addresses,
                credential_types,
                metadata_uris,
                expiration_dates
            ).build_transaction({
                "from": issuer_address,
                "gas": gas_estimate,
                "gasPrice": gas_price,
                "nonce": nonce
            })
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(
                transaction, 
                private_key=self.private_key
            )
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "transaction_hash": self.web3.to_hex(tx_hash),
                "block_number": tx_receipt.blockNumber,
                "gas_used": tx_receipt.gasUsed,
                "credential_ids": [self.web3.to_hex(cid) for cid in credential_ids],
                "status": "success" if tx_receipt.status == 1 else "failed"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def revoke_credential(self, credential_id: bytes) -> Optional[Dict[str, Any]]:
        """Revoke a credential on the blockchain."""
        if not self.is_connected() or not self.account:
            return None
            
        try:
            issuer_address = self.account.address
            
            # Estimate gas for the transaction
            gas_estimate = self.contract.functions.revokeCredential(
                credential_id
            ).estimate_gas({
                "from": issuer_address
            })
            
            # Get current gas price
            gas_price = self.web3.eth.gas_price
            
            # Build transaction
            nonce = self.web3.eth.get_transaction_count(issuer_address)
            transaction = self.contract.functions.revokeCredential(
                credential_id
            ).build_transaction({
                "from": issuer_address,
                "gas": gas_estimate,
                "gasPrice": gas_price,
                "nonce": nonce
            })
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(
                transaction, 
                private_key=self.private_key
            )
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "transaction_hash": self.web3.to_hex(tx_hash),
                "block_number": tx_receipt.blockNumber,
                "gas_used": tx_receipt.gasUsed,
                "credential_id": self.web3.to_hex(credential_id),
                "status": "success" if tx_receipt.status == 1 else "failed"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def verify_credential(self, credential_id: bytes) -> Optional[Dict[str, Any]]:
        """Verify a credential's validity on the blockchain."""
        if not self.is_connected():
            return None
            
        try:
            # Call the verifyCredential function
            valid, status, issuer = self.contract.functions.verifyCredential(
                credential_id
            ).call()
            
            return {
                "credential_id": self.web3.to_hex(credential_id),
                "valid": valid,
                "status": status,
                "issuer": issuer
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_credential_details(self, credential_id: bytes) -> Optional[Dict[str, Any]]:
        """Get detailed information about a credential."""
        if not self.is_connected():
            return None
            
        try:
            # Call the getCredentialDetails function
            credential = self.contract.functions.getCredentialDetails(
                credential_id
            ).call()
            
            # Convert the returned tuple to a dictionary
            result = {
                "id": self.web3.to_hex(credential[0]),
                "issuer": credential[1],
                "subject": credential[2],
                "credential_type": credential[3],
                "metadata_uri": credential[4],
                "issuance_date": credential[5],
                "expiration_date": credential[6],
                "status": credential[7]
            }
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_subject_credentials(self, subject: str) -> Optional[List[bytes]]:
        """Get all credential IDs owned by a subject."""
        if not self.is_connected():
            return None
            
        try:
            subject_address = self.web3.to_checksum_address(subject)
            
            # Call the getSubjectCredentials function
            credential_ids = self.contract.functions.getSubjectCredentials(
                subject_address
            ).call()
            
            return [self.web3.to_hex(cid) for cid in credential_ids]
            
        except Exception as e:
            return None
    
    def get_issuer_credentials(self, issuer: str) -> Optional[List[bytes]]:
        """Get all credential IDs issued by an issuer."""
        if not self.is_connected():
            return None
            
        try:
            issuer_address = self.web3.to_checksum_address(issuer)
            
            # Call the getIssuerCredentials function
            credential_ids = self.contract.functions.getIssuerCredentials(
                issuer_address
            ).call()
            
            return [self.web3.to_hex(cid) for cid in credential_ids]
            
        except Exception as e:
            return None
    
    def is_authorized_issuer(self, issuer: str) -> bool:
        """Check if an address is an authorized issuer."""
        if not self.is_connected():
            return False
            
        try:
            issuer_address = self.web3.to_checksum_address(issuer)
            
            # Call the isAuthorizedIssuer function
            return self.contract.functions.isAuthorizedIssuer(
                issuer_address
            ).call()
            
        except Exception as e:
            return False
    
    def authorize_issuer(self, issuer: str) -> Optional[Dict[str, Any]]:
        """Authorize an address to issue credentials."""
        if not self.is_connected() or not self.account:
            return None
            
        try:
            issuer_address = self.web3.to_checksum_address(issuer)
            owner_address = self.account.address
            
            # Estimate gas for the transaction
            gas_estimate = self.contract.functions.authorizeIssuer(
                issuer_address
            ).estimate_gas({
                "from": owner_address
            })
            
            # Get current gas price
            gas_price = self.web3.eth.gas_price
            
            # Build transaction
            nonce = self.web3.eth.get_transaction_count(owner_address)
            transaction = self.contract.functions.authorizeIssuer(
                issuer_address
            ).build_transaction({
                "from": owner_address,
                "gas": gas_estimate,
                "gasPrice": gas_price,
                "nonce": nonce
            })
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(
                transaction, 
                private_key=self.private_key
            )
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "transaction_hash": self.web3.to_hex(tx_hash),
                "block_number": tx_receipt.blockNumber,
                "gas_used": tx_receipt.gasUsed,
                "issuer": issuer_address,
                "status": "success" if tx_receipt.status == 1 else "failed"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def revoke_issuer(self, issuer: str) -> Optional[Dict[str, Any]]:
        """Revoke an issuer's authorization."""
        if not self.is_connected() or not self.account:
            return None
            
        try:
            issuer_address = self.web3.to_checksum_address(issuer)
            owner_address = self.account.address
            
            # Estimate gas for the transaction
            gas_estimate = self.contract.functions.revokeIssuer(
                issuer_address
            ).estimate_gas({
                "from": owner_address
            })
            
            # Get current gas price
            gas_price = self.web3.eth.gas_price
            
            # Build transaction
            nonce = self.web3.eth.get_transaction_count(owner_address)
            transaction = self.contract.functions.revokeIssuer(
                issuer_address
            ).build_transaction({
                "from": owner_address,
                "gas": gas_estimate,
                "gasPrice": gas_price,
                "nonce": nonce
            })
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(
                transaction, 
                private_key=self.private_key
            )
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "transaction_hash": self.web3.to_hex(tx_hash),
                "block_number": tx_receipt.blockNumber,
                "gas_used": tx_receipt.gasUsed,
                "issuer": issuer_address,
                "status": "success" if tx_receipt.status == 1 else "failed"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def sign_message(self, message: str) -> Optional[Dict[str, Any]]:
        """Sign a message with the account's private key."""
        if not self.account:
            return None
            
        try:
            # Create the message hash
            message_hash = encode_defunct(text=message)
            
            # Sign the message
            signed_message = self.web3.eth.account.sign_message(
                message_hash,
                private_key=self.private_key
            )
            
            return {
                "message": message,
                "signature": self.web3.to_hex(signed_message.signature),
                "signer": self.account.address
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def verify_signature(self, message: str, signature: str, address: str) -> bool:
        """Verify a signature."""
        try:
            signer_address = self.web3.to_checksum_address(address)
            signature_bytes = HexBytes(signature)
            
            # Create the message hash
            message_hash = encode_defunct(text=message)
            
            # Recover the signer's address
            recovered_address = self.web3.eth.account.recover_message(
                message_hash,
                signature=signature_bytes
            )
            
            return recovered_address == signer_address
            
        except Exception as e:
            return False

# Create a singleton instance
blockchain_service = BlockchainService()
