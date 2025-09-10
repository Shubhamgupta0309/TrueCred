#!/usr/bin/env python3
"""
Deploy TrueCred smart contract to local blockchain.
"""
import json
import os
from pathlib import Path
from web3 import Web3

def deploy_contract():
    """Deploy the TrueCred contract to local blockchain."""
    # Connect to local blockchain
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
    
    if not w3.is_connected():
        print("Error: Could not connect to local blockchain. Make sure Ganache is running.")
        return False

    # Get the first account (will be the contract owner)
    accounts = w3.eth.accounts
    if not accounts:
        print("Error: No accounts found in the local blockchain.")
        return False
        
    owner = accounts[0]
    
    # Load the compiled contract
    current_dir = Path(__file__).parent.absolute()
    build_dir = current_dir.parent / "build"
    contract_path = build_dir / "TrueCred.json"
    
    if not contract_path.exists():
        print(f"Error: Contract file not found at {contract_path}")
        print("Please compile the contract first using compile_contract.py")
        return False
        
    with open(contract_path) as f:
        contract_data = json.load(f)
    
    # Deploy the contract
    print(f"Deploying contract from account: {owner}")
    
    Contract = w3.eth.contract(
        abi=contract_data["abi"],
        bytecode=contract_data["bytecode"]
    )
    
    try:
        # Estimate gas
        gas_estimate = Contract.constructor().estimate_gas()
        
        # Build the transaction
        transaction = Contract.constructor().build_transaction({
            'from': owner,
            'gas': gas_estimate,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(owner)
        })
        
        # Send the transaction
        tx_hash = w3.eth.send_transaction(transaction)
        print(f"Transaction sent: {tx_hash.hex()}")
        
        # Wait for the transaction to be mined
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        contract_address = tx_receipt.contractAddress
        
        print(f"\nContract deployed successfully!")
        print(f"Contract address: {contract_address}")
        
        # Save the contract address
        with open(build_dir / "contract_address.txt", "w") as f:
            f.write(contract_address)
            
        # Update .env file if it exists
        env_path = current_dir.parent / ".env"
        if env_path.exists():
            env_content = env_path.read_text()
            
            # Update or add CONTRACT_ADDRESS
            if "CONTRACT_ADDRESS=" in env_content:
                new_content = []
                for line in env_content.splitlines():
                    if line.startswith("CONTRACT_ADDRESS="):
                        new_content.append(f"CONTRACT_ADDRESS={contract_address}")
                    else:
                        new_content.append(line)
                env_path.write_text("\n".join(new_content))
            else:
                with open(env_path, "a") as f:
                    f.write(f"\nCONTRACT_ADDRESS={contract_address}\n")
            
        return True
        
    except Exception as e:
        print(f"Error deploying contract: {e}")
        return False

if __name__ == "__main__":
    success = deploy_contract()
    exit(0 if success else 1)
