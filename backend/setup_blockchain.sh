#!/bin/bash
# Blockchain setup script for TrueCred

echo "TrueCred Blockchain Setup"
echo "========================="

echo "Checking environment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Please create one based on .env.sample"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create build directory if it doesn't exist
mkdir -p contracts/build

# Compile the contract
echo "Compiling smart contract..."
python contracts/compile_contract.py

# Ask user if they want to deploy
echo
echo "Do you want to deploy the contract to Goerli testnet? (y/n)"
read deploy

if [ "$deploy" = "y" ] || [ "$deploy" = "Y" ]; then
    echo "Deploying smart contract to Goerli testnet..."
    python contracts/deploy_contract.py --network goerli
    
    echo
    echo "IMPORTANT: Make sure to update your .env file with the new CONTRACT_ADDRESS"
    echo
fi

# Test blockchain connection
echo "Testing blockchain connection..."
python contracts/test_blockchain.py

echo
echo "Blockchain setup completed!"
echo
