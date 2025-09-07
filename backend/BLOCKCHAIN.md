# TrueCred Blockchain Integration

## Overview

TrueCred leverages blockchain technology to provide immutable and verifiable records of credentials and professional experiences. This integration helps ensure the integrity and trustworthiness of the platform by creating a tamper-proof verification system.

## Components

The blockchain integration consists of the following components:

1. **Smart Contracts**: Located in the `contracts` directory, these Solidity contracts run on the Ethereum blockchain to store and verify credential and experience hashes.

2. **Digital Signature Service**: Manages cryptographic operations for signing and verifying credentials and experiences before they are stored on the blockchain.

3. **Blockchain Service**: Provides an interface between the TrueCred application and the blockchain, handling transactions and verification.

4. **Blockchain Routes**: API endpoints for preparing and storing credentials and experiences on the blockchain, as well as verifying their authenticity.

## Workflow

The blockchain verification workflow follows these steps:

1. **Preparation**: A verified credential or experience is prepared for blockchain storage by generating a hash of its essential data.

2. **Storage**: The hash is stored on the Ethereum blockchain through the TrueCred smart contract.

3. **Verification**: Anyone can verify the authenticity of a credential or experience by comparing its current hash with the one stored on the blockchain.

## Setup and Configuration

To use the blockchain integration:

1. Install the required dependencies:

   ```
   pip install web3 eth-account py-solc-x cryptography
   ```

2. Set up environment variables:

   ```
   ETHEREUM_PROVIDER_URL=https://goerli.infura.io/v3/your-infura-key
   ETHEREUM_PRIVATE_KEY=your-private-key
   ETHEREUM_CHAIN_ID=5  # Goerli testnet
   CONTRACT_ADDRESS=deployed-contract-address
   ```

3. Compile and deploy the smart contract (if not already deployed):
   ```
   python contracts/compile_contract.py
   ```

## API Endpoints

The blockchain API endpoints include:

- **POST /api/blockchain/credentials/:id/prepare**: Prepares a credential for blockchain storage
- **POST /api/blockchain/experiences/:id/prepare**: Prepares an experience for blockchain storage
- **POST /api/blockchain/credentials/:id/store**: Stores a credential hash on the blockchain
- **POST /api/blockchain/experiences/:id/store**: Stores an experience hash on the blockchain
- **GET /api/blockchain/credentials/:id/verify**: Verifies a credential against the blockchain
- **GET /api/blockchain/experiences/:id/verify**: Verifies an experience against the blockchain
- **GET /api/blockchain/transaction/:hash**: Gets the status of a blockchain transaction

## Security Considerations

- Only hashes of data are stored on the blockchain, never the actual credentials or experiences
- Smart contract access controls ensure only authorized users can store or revoke credentials
- Digital signatures ensure the integrity and authenticity of the data
