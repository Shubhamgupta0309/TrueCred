#!/usr/bin/env python3
"""
Deploy the TrueCred smart contract to an Ethereum network.
"""
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import geth_poa_middleware

# Add the parent directory to sys.path to import from parent modules if needed
sys.path.append(str(Path(__file__).parent.parent))

def deploy_contract():
    """Deploy the TrueCred contract to the Ethereum network specified in .env."""
    # Load environment variables
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    
    # Get the Web3 provider URL based on the network
    infura_project_id = os.getenv("INFURA_PROJECT_ID")
    ethereum_network = os.getenv("ETHEREUM_NETWORK", "goerli")
    
    if not infura_project_id or infura_project_id == "your_infura_project_id":
        print("Error: INFURA_PROJECT_ID not set in .env file")
        return False
    
    # Create the web3 instance
    provider_url = f"https://{ethereum_network}.infura.io/v3/{infura_project_id}"
    web3 = Web3(Web3.HTTPProvider(provider_url))
    
    # Apply middleware for PoA networks (needed for testnets like Goerli)
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    if not web3.is_connected():
        print(f"Error: Could not connect to Ethereum network at {provider_url}")
        return False
    
    print(f"Connected to Ethereum network: {ethereum_network}")
    
    # Get the private key for deployment
    private_key = os.getenv("DEPLOYER_PRIVATE_KEY")
    if not private_key:
        print("Error: DEPLOYER_PRIVATE_KEY not set in .env file")
        print("Please add your deployer wallet private key to the .env file")
        return False
    
    # Set up the deployer account
    account = web3.eth.account.from_key(private_key)
    deployer_address = account.address
    print(f"Deployer address: {deployer_address}")
    
    # Load the compiled contract
    contract_dir = Path(__file__).parent.parent / "build"
    contract_path = contract_dir / "TrueCred.json"
    
    if not contract_path.exists():
        print(f"Error: Compiled contract not found at {contract_path}")
        print("Please run compile_contract.py first")
        return False
    
    with open(contract_path, "r") as f:
        contract_data = json.load(f)
    
    # Prepare the contract
    contract_bytecode = contract_data["bytecode"]
    contract_abi = contract_data["abi"]
    TrueCred = web3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
    
    # Check balance
    balance = web3.eth.get_balance(deployer_address)
    balance_eth = web3.from_wei(balance, "ether")
    print(f"Deployer balance: {balance_eth} ETH")
    
    if balance == 0:
        print("Error: Deployer account has no ETH for gas")
        print(f"Please send some ETH to {deployer_address} to cover gas costs")
        return False
    
    # Estimate gas for deployment
    try:
        gas_estimate = TrueCred.constructor().estimate_gas({"from": deployer_address})
        gas_price = web3.eth.gas_price
        gas_cost_wei = gas_estimate * gas_price
        gas_cost_eth = web3.from_wei(gas_cost_wei, "ether")
        
        print(f"Estimated deployment gas: {gas_estimate}")
        print(f"Current gas price: {web3.from_wei(gas_price, 'gwei')} gwei")
        print(f"Estimated deployment cost: {gas_cost_eth} ETH")
        
        if gas_cost_wei > balance:
            print("Error: Insufficient funds for deployment")
            print(f"Required: {gas_cost_eth} ETH, Available: {balance_eth} ETH")
            return False
    except Exception as e:
        print(f"Error estimating gas: {e}")
        return False
    
    # Build the transaction
    nonce = web3.eth.get_transaction_count(deployer_address)
    transaction = TrueCred.constructor().build_transaction({
        "from": deployer_address,
        "gas": gas_estimate,
        "gasPrice": gas_price,
        "nonce": nonce
    })
    
    # Sign the transaction
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
    
    # Deploy the contract
    print("Deploying contract...")
    try:
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f"Transaction sent: {web3.to_hex(tx_hash)}")
        
        # Wait for the transaction to be mined
        print("Waiting for transaction to be mined...")
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        contract_address = tx_receipt.contractAddress
        print(f"Contract deployed successfully!")
        print(f"Contract address: {contract_address}")
        print(f"Transaction hash: {web3.to_hex(tx_hash)}")
        print(f"Gas used: {tx_receipt.gasUsed}")
        
        # Update the .env file with the contract address
        env_content = []
        with open(env_path, "r") as f:
            env_content = f.readlines()
        
        with open(env_path, "w") as f:
            for line in env_content:
                if line.startswith("CONTRACT_ADDRESS="):
                    f.write(f"CONTRACT_ADDRESS={contract_address}\n")
                else:
                    f.write(line)
        
        print(f"Updated CONTRACT_ADDRESS in .env file")
        
        # Save deployment info
        deployment_info = {
            "network": ethereum_network,
            "contractAddress": contract_address,
            "deploymentTransactionHash": web3.to_hex(tx_hash),
            "deployerAddress": deployer_address,
            "blockNumber": tx_receipt.blockNumber,
            "timestamp": web3.eth.get_block(tx_receipt.blockNumber).timestamp
        }
        
        deployment_path = contract_dir / "deployment.json"
        with open(deployment_path, "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        print(f"Deployment information saved to {deployment_path}")
        return True
    
    except Exception as e:
        print(f"Error deploying contract: {e}")
        return False

if __name__ == "__main__":
    success = deploy_contract()
    sys.exit(0 if success else 1)
