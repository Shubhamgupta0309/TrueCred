"""
Blockchain utility for Ethereum interaction in the TrueCred application.
"""
from web3 import Web3
import json
import os
from pathlib import Path

class BlockchainUtil:
    """
    Utility class for interacting with the Ethereum blockchain.
    """
    
    def __init__(self, web3_provider_uri, contract_address=None, contract_abi=None):
        """
        Initialize the blockchain utility.
        
        Args:
            web3_provider_uri: URI for the Web3 provider (e.g., Infura, local node)
            contract_address: Address of the deployed TrueCred contract (optional)
            contract_abi: ABI of the TrueCred contract (optional)
        """
        self.web3 = Web3(Web3.HTTPProvider(web3_provider_uri))
        self.contract_address = contract_address
        self.contract_abi = contract_abi
        self.contract = None
        
        if contract_address and contract_abi:
            self.set_contract(contract_address, contract_abi)
    
    def set_contract(self, contract_address, contract_abi):
        """
        Set the contract to interact with.
        
        Args:
            contract_address: Address of the deployed TrueCred contract
            contract_abi: ABI of the TrueCred contract
        """
        self.contract_address = contract_address
        self.contract_abi = contract_abi
        self.contract = self.web3.eth.contract(
            address=self.web3.toChecksumAddress(contract_address),
            abi=contract_abi
        )
    
    def load_contract_from_file(self, abi_path, address_path=None):
        """
        Load contract details from files.
        
        Args:
            abi_path: Path to the ABI JSON file
            address_path: Path to a file containing the contract address (optional)
        """
        # Load ABI
        with open(abi_path, 'r') as f:
            self.contract_abi = json.load(f)
        
        # Load address if provided
        if address_path:
            with open(address_path, 'r') as f:
                self.contract_address = f.read().strip()
            
        if self.contract_address:
            self.contract = self.web3.eth.contract(
                address=self.web3.toChecksumAddress(self.contract_address),
                abi=self.contract_abi
            )
    
    def is_connected(self):
        """
        Check if connected to the Ethereum network.
        
        Returns:
            True if connected, False otherwise
        """
        return self.web3.isConnected()
    
    def get_transaction_receipt(self, tx_hash):
        """
        Get a transaction receipt.
        
        Args:
            tx_hash: Transaction hash
        
        Returns:
            Transaction receipt
        """
        return self.web3.eth.getTransactionReceipt(tx_hash)
    
    def store_credential_hash(self, credential_hash, from_address, private_key):
        """
        Store a credential hash on the blockchain.
        
        Args:
            credential_hash: Hash of the credential to store
            from_address: Address to send the transaction from
            private_key: Private key for the from_address
        
        Returns:
            Transaction hash
        """
        if not self.contract:
            raise ValueError("Contract not set. Call set_contract() first.")
        
        # Get the function from the contract
        store_credential_function = self.contract.functions.storeCredential(credential_hash)
        
        # Build the transaction
        tx = store_credential_function.buildTransaction({
            'from': from_address,
            'nonce': self.web3.eth.getTransactionCount(from_address),
            'gas': 2000000,
            'gasPrice': self.web3.toWei('50', 'gwei')
        })
        
        # Sign the transaction
        signed_tx = self.web3.eth.account.signTransaction(tx, private_key)
        
        # Send the transaction
        tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        
        return tx_hash.hex()
    
    def verify_credential_hash(self, credential_hash):
        """
        Verify a credential hash on the blockchain.
        
        Args:
            credential_hash: Hash to verify
        
        Returns:
            Boolean indicating if the hash exists on the blockchain
        """
        if not self.contract:
            raise ValueError("Contract not set. Call set_contract() first.")
        
        # Call the verify function
        return self.contract.functions.verifyCredential(credential_hash).call()
