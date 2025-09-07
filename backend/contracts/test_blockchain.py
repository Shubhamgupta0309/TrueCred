"""
Script to test the blockchain connection and contract interaction.

This script tests the connection to the Ethereum network and the interaction
with the deployed TrueCred smart contract.

Usage:
    python test_blockchain.py [--network goerli|sepolia|mainnet]

Environment variables required:
    ETHEREUM_PROVIDER_URL: URL of the Ethereum node
    CONTRACT_ADDRESS: Address of the deployed TrueCred contract
    ETHEREUM_PRIVATE_KEY: Private key for the test account (optional for read-only tests)
"""
import os
import sys
import json
import argparse
import logging
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_contract_abi():
    """Load the TrueCred contract ABI from the build directory."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        build_dir = os.path.join(script_dir, 'build')
        contract_file = os.path.join(build_dir, 'TrueCred.json')
        
        with open(contract_file, 'r') as f:
            contract_data = json.load(f)
        
        return contract_data['abi']
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        logger.error(f"Error loading contract ABI: {str(e)}")
        sys.exit(1)

def test_blockchain_connection(network='goerli'):
    """
    Test the connection to the Ethereum blockchain.
    
    Args:
        network (str): Network to connect to ('goerli', 'sepolia', 'mainnet')
    """
    # Get environment variables
    provider_url = os.getenv('ETHEREUM_PROVIDER_URL')
    contract_address = os.getenv('CONTRACT_ADDRESS')
    private_key = os.getenv('ETHEREUM_PRIVATE_KEY')
    
    if not provider_url:
        logger.error("ETHEREUM_PROVIDER_URL environment variable not set")
        sys.exit(1)
    
    if not contract_address:
        logger.error("CONTRACT_ADDRESS environment variable not set")
        sys.exit(1)
    
    try:
        # Connect to Ethereum
        web3 = Web3(Web3.HTTPProvider(provider_url))
        
        # Add middleware for testnet compatibility
        if network in ['goerli', 'sepolia']:
            web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Check connection
        if not web3.is_connected():
            logger.error(f"Failed to connect to Ethereum network at {provider_url}")
            sys.exit(1)
        
        logger.info(f"Connected to Ethereum network: {network}")
        logger.info(f"Current block number: {web3.eth.block_number}")
        
        # Check contract address
        if not web3.is_address(contract_address):
            logger.error(f"Invalid contract address: {contract_address}")
            sys.exit(1)
        
        # Check contract code
        code = web3.eth.get_code(contract_address)
        if code == b'':
            logger.error(f"No contract found at address: {contract_address}")
            sys.exit(1)
        
        logger.info(f"Contract found at address: {contract_address}")
        
        # Load contract ABI
        contract_abi = load_contract_abi()
        
        # Create contract instance
        contract = web3.eth.contract(address=contract_address, abi=contract_abi)
        
        # Test contract read function
        owner = contract.functions.owner().call()
        logger.info(f"Contract owner: {owner}")
        
        # Set up account if private key is available
        if private_key:
            account = Account.from_key(private_key)
            logger.info(f"Test account: {account.address}")
            
            # Check account balance
            balance = web3.eth.get_balance(account.address)
            balance_eth = web3.from_wei(balance, 'ether')
            logger.info(f"Account balance: {balance_eth} ETH")
            
            # Test contract write function
            test_id = f"test_{datetime.utcnow().timestamp()}"
            test_hash = Web3.solidity_keccak(['string'], [test_id]).hex()
            
            logger.info(f"Testing contract write function with ID: {test_id}")
            logger.info(f"Test hash: {test_hash}")
            
            # Build transaction
            tx = contract.functions.storeCredentialHash(
                test_id,
                test_hash
            ).build_transaction({
                'chainId': web3.eth.chain_id,
                'gas': 2000000,
                'gasPrice': web3.eth.gas_price,
                'nonce': web3.eth.get_transaction_count(account.address),
                'from': account.address
            })
            
            # Sign and send transaction
            signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            logger.info(f"Transaction sent: {tx_hash.hex()}")
            logger.info("Waiting for transaction to be mined...")
            
            # Wait for transaction receipt
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            logger.info(f"Transaction mined!")
            logger.info(f"Transaction hash: {tx_receipt.transactionHash.hex()}")
            logger.info(f"Block number: {tx_receipt.blockNumber}")
            logger.info(f"Gas used: {tx_receipt.gasUsed}")
            
            # Verify the stored hash
            stored_hash = contract.functions.getCredentialHash(test_id).call()
            logger.info(f"Stored hash: {stored_hash}")
            
            if stored_hash == test_hash:
                logger.info("Hash verification successful!")
            else:
                logger.error("Hash verification failed!")
        
        logger.info("Blockchain connection test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error testing blockchain connection: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test TrueCred blockchain connection')
    parser.add_argument('--network', type=str, default='goerli',
                      help='Ethereum network to connect to (goerli, sepolia, mainnet)')
    
    args = parser.parse_args()
    
    if args.network not in ['goerli', 'sepolia', 'mainnet']:
        logger.error(f"Invalid network: {args.network}")
        sys.exit(1)
    
    logger.info(f"Testing blockchain connection to {args.network} network...")
    test_blockchain_connection(args.network)
