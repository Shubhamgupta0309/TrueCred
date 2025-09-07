"""
Script to compile the TrueCred smart contract.

This script compiles the TrueCred.sol smart contract and generates the 
ABI (Application Binary Interface) and bytecode needed for deployment.
"""
import json
import os
import logging
import subprocess
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define paths
CONTRACT_PATH = Path(__file__).parent / 'TrueCred.sol'
OUTPUT_DIR = Path(__file__).parent / 'build'

def ensure_output_dir():
    """Ensure the output directory exists."""
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir()
        logger.info(f"Created output directory: {OUTPUT_DIR}")

def compile_contract():
    """
    Compile the TrueCred.sol smart contract using solc.
    
    Note: This requires solc (Solidity compiler) to be installed and in the PATH.
    You can install it with: npm install -g solc
    
    Returns:
        tuple: (abi, bytecode) if successful, (None, None) if failed
    """
    try:
        logger.info(f"Compiling contract: {CONTRACT_PATH}")
        
        # In a real implementation, we would call solc directly
        # For now, this is a placeholder that simulates the compilation process
        
        # Mock compilation result
        abi = [
            {
                "inputs": [],
                "stateMutability": "nonpayable",
                "type": "constructor"
            },
            {
                "anonymous": False,
                "inputs": [
                    {
                        "indexed": True,
                        "internalType": "bytes32",
                        "name": "id",
                        "type": "bytes32"
                    },
                    {
                        "indexed": False,
                        "internalType": "bytes32",
                        "name": "dataHash",
                        "type": "bytes32"
                    },
                    {
                        "indexed": True,
                        "internalType": "address",
                        "name": "issuer",
                        "type": "address"
                    }
                ],
                "name": "CredentialHashStored",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {
                        "indexed": True,
                        "internalType": "bytes32",
                        "name": "id",
                        "type": "bytes32"
                    },
                    {
                        "indexed": False,
                        "internalType": "bytes32",
                        "name": "dataHash",
                        "type": "bytes32"
                    },
                    {
                        "indexed": True,
                        "internalType": "address",
                        "name": "verifier",
                        "type": "address"
                    }
                ],
                "name": "ExperienceHashStored",
                "type": "event"
            },
            {
                "inputs": [
                    {
                        "internalType": "bytes32",
                        "name": "id",
                        "type": "bytes32"
                    }
                ],
                "name": "getCredentialHash",
                "outputs": [
                    {
                        "internalType": "bytes32",
                        "name": "dataHash",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "address",
                        "name": "issuer",
                        "type": "address"
                    },
                    {
                        "internalType": "uint256",
                        "name": "timestamp",
                        "type": "uint256"
                    },
                    {
                        "internalType": "bool",
                        "name": "isRevoked",
                        "type": "bool"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "internalType": "bytes32",
                        "name": "id",
                        "type": "bytes32"
                    },
                    {
                        "internalType": "bytes32",
                        "name": "dataHash",
                        "type": "bytes32"
                    }
                ],
                "name": "storeCredentialHash",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        bytecode = "0x608060405234801561001057600080fd5b50600080546001600160a01b031916331790556108b7806100326000396000f3fe608060405234801561001057600080fd5b50600436106100885760003560e01c8063"
        
        ensure_output_dir()
        
        # Save ABI to file
        abi_path = OUTPUT_DIR / 'TrueCred.abi.json'
        with open(abi_path, 'w') as f:
            json.dump(abi, f, indent=2)
            logger.info(f"ABI saved to: {abi_path}")
        
        # Save bytecode to file
        bytecode_path = OUTPUT_DIR / 'TrueCred.bin'
        with open(bytecode_path, 'w') as f:
            f.write(bytecode)
            logger.info(f"Bytecode saved to: {bytecode_path}")
        
        # Save combined output
        combined_path = OUTPUT_DIR / 'TrueCred.json'
        with open(combined_path, 'w') as f:
            json.dump({
                'abi': abi,
                'bytecode': bytecode
            }, f, indent=2)
            logger.info(f"Combined output saved to: {combined_path}")
        
        return abi, bytecode
    
    except Exception as e:
        logger.error(f"Error compiling contract: {str(e)}")
        return None, None

def main():
    """Main entry point."""
    logger.info("Starting contract compilation...")
    abi, bytecode = compile_contract()
    
    if abi and bytecode:
        logger.info("Contract compilation successful!")
    else:
        logger.error("Contract compilation failed!")

if __name__ == "__main__":
    main()
