# Blockchain Integration for TrueCred

This document provides information about the blockchain integration for TrueCred, including setup instructions, usage, and troubleshooting.

## Overview

TrueCred uses Ethereum blockchain technology to provide immutable and verifiable records of credentials and professional experiences. The blockchain integration includes:

1. Smart contract for storing and verifying credential and experience hashes
2. Web3 implementation for interacting with the Ethereum blockchain
3. Digital signature service for creating and verifying signatures
4. Blockchain service for managing transactions and verification

## Requirements

- Python 3.7+
- Ethereum account with private key
- Infura API key (for connecting to Ethereum networks)
- Solidity compiler (installed via py-solc-x)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file based on `.env.sample` with the following blockchain-related variables:

```
ETHEREUM_PROVIDER_URL=https://goerli.infura.io/v3/your-infura-api-key
ETHEREUM_PRIVATE_KEY=your-ethereum-private-key
ETHEREUM_CHAIN_ID=5  # Goerli testnet
CONTRACT_ADDRESS=your-deployed-contract-address
INFURA_API_KEY=your-infura-api-key
```

### 3. Compile and Deploy Smart Contract

#### Windows

```bash
setup_blockchain.bat
```

#### Unix/Linux/Mac

```bash
chmod +x setup_blockchain.sh
./setup_blockchain.sh
```

Or manually:

```bash
# Compile the contract
python contracts/compile_contract.py

# Deploy the contract (optional)
python contracts/deploy_contract.py --network goerli

# Test the connection
python contracts/test_blockchain.py
```

### 4. Update CONTRACT_ADDRESS

After deploying the contract, update the `CONTRACT_ADDRESS` in your `.env` file with the address of the deployed contract.

## Usage

### 1. Storing Credential Hash

To store a credential hash on the blockchain:

```python
from services.blockchain_service import BlockchainService

blockchain_service = BlockchainService()
transaction = blockchain_service.store_credential_hash(
    credential_id="credential-123",
    data_hash="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
)

print(f"Transaction hash: {transaction['transaction_hash']}")
```

### 2. Verifying Credential Hash

To verify a credential hash on the blockchain:

```python
from services.blockchain_service import BlockchainService

blockchain_service = BlockchainService()
is_verified = blockchain_service.verify_credential_hash(
    credential_id="credential-123",
    data_hash="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
)

print(f"Verification result: {is_verified}")
```

### 3. API Endpoints

The blockchain integration provides the following API endpoints:

- `POST /api/blockchain/credentials/:id/prepare` - Prepare a credential for blockchain storage
- `POST /api/blockchain/experiences/:id/prepare` - Prepare an experience for blockchain storage
- `POST /api/blockchain/credentials/:id/store` - Store a credential hash on the blockchain
- `POST /api/blockchain/experiences/:id/store` - Store an experience hash on the blockchain
- `GET /api/blockchain/credentials/:id/verify` - Verify a credential against the blockchain
- `GET /api/blockchain/experiences/:id/verify` - Verify an experience against the blockchain
- `GET /api/blockchain/transaction/:hash` - Get the status of a blockchain transaction

## Smart Contract

The TrueCred smart contract provides the following functionality:

1. Storing credential hashes
2. Storing experience hashes
3. Retrieving stored hashes
4. Revoking credentials
5. Checking revocation status

## Troubleshooting

### Common Issues

1. **Unable to connect to Ethereum network**

   - Check your Infura API key
   - Verify the provider URL in your `.env` file
   - Ensure your network connection is working

2. **Transaction fails**

   - Check your account balance (need ETH for gas)
   - Verify your private key is correct
   - Check gas price and limit settings

3. **Contract not found**
   - Ensure the CONTRACT_ADDRESS is correct
   - Verify the contract was deployed successfully
   - Check you're connecting to the right network

### Debugging

Enable DEBUG level logging to see more information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Networks

TrueCred supports the following Ethereum networks:

- **Goerli** (testnet) - Chain ID: 5
- **Sepolia** (testnet) - Chain ID: 11155111
- **Mainnet** - Chain ID: 1

For development and testing, we recommend using Goerli or Sepolia testnet.

## Gas Optimization

The smart contract has been optimized for gas efficiency:

- Minimal storage usage
- Gas-efficient data structures
- Optimized function implementations

## Security Considerations

1. Never share your private key
2. Use environment variables for sensitive information
3. Implement proper access controls for blockchain operations
4. Only allow authorized users to store and revoke credentials
5. Validate all inputs before sending transactions

## References

- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Solidity Documentation](https://docs.soliditylang.org/)
- [Ethereum Development Documentation](https://ethereum.org/developers/)
