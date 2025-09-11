#!/usr/bin/env python3
"""
Compile the TrueCred smart contract to produce ABI and bytecode.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

# Add the parent directory to sys.path to import from parent modules if needed
sys.path.append(str(Path(__file__).parent.parent))

def compile_contract():
    """Compile the TrueCred.sol contract using solc."""
    try:
        # Check if solc is installed
        subprocess.run(["solc", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Solidity compiler (solc) not found. Please install it.")
        print("Installation instructions: https://docs.soliditylang.org/en/v0.8.17/installing-solidity.html")
        return False

    # Get the directory of this script
    current_dir = Path(__file__).parent.absolute()
    contract_path = current_dir / "TrueCred.sol"
    output_dir = current_dir.parent / "build"

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Compile the contract
    print(f"Compiling contract: {contract_path}")
    compile_command = [
        "solc",
        "--optimize",
        "--combined-json", "abi,bin",
        str(contract_path)
    ]

    try:
        result = subprocess.run(
            compile_command,
            check=True,
            capture_output=True,
            text=True
        )
        compiled_json = json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error compiling contract: {e}")
        print(f"Compiler output: {e.stderr}")
        return False
    except json.JSONDecodeError as e:
        print(f"Error parsing compiler output: {e}")
        return False

    # Extract the contract data
    contract_name = "TrueCred"
    contract_key = f"{contract_path}:{contract_name}"
    
    if contract_key not in compiled_json["contracts"]:
        # Try alternative key format
        contract_key = next(
            (key for key in compiled_json["contracts"].keys() if key.endswith(f":{contract_name}")),
            None
        )
        
    if not contract_key:
        print(f"Error: Contract {contract_name} not found in compiler output")
        return False
        
    contract_data = compiled_json["contracts"][contract_key]
    
    # Create a clean contract output
    output = {
        "contractName": contract_name,
        "abi": contract_data["abi"],
        "bytecode": contract_data["bin"],
        "compiler": {
            "name": "solc",
            "version": result.stderr.split("\n")[0] if result.stderr else "Unknown"
        }
    }
    
    # Write the output to a JSON file
    output_path = output_dir / f"{contract_name}.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"Contract compiled successfully. Output written to {output_path}")
    return True

if __name__ == "__main__":
    success = compile_contract()
    sys.exit(0 if success else 1)
