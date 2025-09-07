"""
Script to deploy the TrueCred smart contract to an Ethereum testnet.

This script compiles the TrueCred smart contract and deploys it to the
specified Ethereum network (default: Goerli testnet).

Usage:
    python deploy_contract.py [--network goerli|sepolia|mainnet]

Environment variables required:
    ETHEREUM_PRIVATE_KEY: Private key for the deployer account
    INFURA_API_KEY: API key for Infura
"""
import os
import sys
import json
import argparse
import logging
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from solcx import compile_source, install_solc
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_contract_path():
    """Get the path to the smart contract file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, 'TrueCred.sol')

def compile_contract():
    """Compile the TrueCred smart contract."""
    # Install solc compiler if not already installed
    try:
        install_solc(version='0.8.0')
    except Exception as e:
        logger.warning(f"Failed to install solc: {e}. Using existing installation.")
    
    # Read contract source
    contract_path = get_contract_path()
    with open(contract_path, 'r') as f:
        contract_source = f.read()
    
    # Compile contract
    compiled_sol = compile_source(
        contract_source,
        output_values=['abi', 'bin'],
        solc_version='0.8.0'
    )
    
    # Extract contract data
    contract_id, contract_interface = compiled_sol.popitem()
    bytecode = contract_interface['bin']
    abi = contract_interface['abi']
    
    logger.info(f"Contract compiled successfully: {contract_id}")
    
    return bytecode, abi

def deploy_contract(network='goerli'):
    """
    Deploy the TrueCred smart contract to the specified network.
    
    Args:
        network (str): Network to deploy to ('goerli', 'sepolia', 'mainnet')
        
    Returns:
        str: Deployed contract address
    """
    # Get environment variables
    private_key = os.getenv('ETHEREUM_PRIVATE_KEY')
    infura_api_key = os.getenv('INFURA_API_KEY')
    
    if not private_key:
        logger.error("ETHEREUM_PRIVATE_KEY environment variable not set")
        sys.exit(1)
    
    if not infura_api_key:
        logger.error("INFURA_API_KEY environment variable not set")
        sys.exit(1)
    
    # Set up provider URL
    provider_url = f"https://{network}.infura.io/v3/{infura_api_key}"
    
    # Chain ID mapping
    chain_ids = {
        'mainnet': 1,
        'goerli': 5,
        'sepolia': 11155111,
    }
    chain_id = chain_ids.get(network, 5)  # Default to Goerli
    
    try:
        # Connect to Ethereum
        web3 = Web3(Web3.HTTPProvider(provider_url))
        
        # Add middleware for testnet compatibility
        if network in ['goerli', 'sepolia']:
            web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Set up account
        account = Account.from_key(private_key)
        logger.info(f"Deploying from account: {account.address}")
        
        # Check account balance
        balance = web3.eth.get_balance(account.address)
        balance_eth = web3.from_wei(balance, 'ether')
        logger.info(f"Account balance: {balance_eth} ETH")
        
        if balance_eth < 0.01:
            logger.warning(f"Account balance is low: {balance_eth} ETH")
        
        # Compile contract
        bytecode, abi = compile_contract()
        
        # Create contract object
        TrueCred = web3.eth.contract(abi=abi, bytecode=bytecode)
        
        # Build transaction
        transaction = TrueCred.constructor().build_transaction({
            'chainId': chain_id,
            'gas': 3000000,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(account.address),
            'from': account.address
        })
        
        # Sign and send transaction
        signed_tx = web3.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        logger.info(f"Transaction sent: {tx_hash.hex()}")
        logger.info("Waiting for transaction to be mined...")
        
        # Wait for transaction receipt
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        contract_address = tx_receipt.contractAddress
        
        logger.info(f"Contract deployed successfully!")
        logger.info(f"Contract address: {contract_address}")
        logger.info(f"Transaction hash: {tx_receipt.transactionHash.hex()}")
        logger.info(f"Block number: {tx_receipt.blockNumber}")
        logger.info(f"Gas used: {tx_receipt.gasUsed}")
        
        # Save contract data
        build_dir = os.path.join(os.path.dirname(get_contract_path()), 'build')
        os.makedirs(build_dir, exist_ok=True)
        
        contract_data = {
            'address': contract_address,
            'abi': abi,
            'bytecode': bytecode,
            'transaction_hash': tx_receipt.transactionHash.hex(),
            'block_number': tx_receipt.blockNumber,
            'gas_used': tx_receipt.gasUsed,
            'network': network,
            'chain_id': chain_id,
            'deployed_at': datetime.utcnow().isoformat(),
            'deployed_by': account.address
        }
        
        contract_file = os.path.join(build_dir, f'TrueCred_{network}.json')
        with open(contract_file, 'w') as f:
            json.dump(contract_data, f, indent=2)
        
        logger.info(f"Contract data saved to {contract_file}")
        
        # Also save as the default contract file
        default_contract_file = os.path.join(build_dir, 'TrueCred.json')
        with open(default_contract_file, 'w') as f:
            json.dump(contract_data, f, indent=2)
        
        logger.info(f"Contract data saved to {default_contract_file}")
        
        return contract_address
        
    except Exception as e:
        logger.error(f"Error deploying contract: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deploy TrueCred smart contract')
    parser.add_argument('--network', type=str, default='goerli',
                      help='Ethereum network to deploy to (goerli, sepolia, mainnet)')
    
    args = parser.parse_args()
    
    if args.network not in ['goerli', 'sepolia', 'mainnet']:
        logger.error(f"Invalid network: {args.network}")
        sys.exit(1)
    
    logger.info(f"Deploying TrueCred contract to {args.network} network...")
    deploy_contract(args.network)
