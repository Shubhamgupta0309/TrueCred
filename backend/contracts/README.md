# TrueCred Smart Contracts

This directory contains the smart contracts used by TrueCred for credential and experience verification on the blockchain.

## Overview

TrueCred uses blockchain technology to provide immutable and verifiable records of credentials and professional experiences. The smart contracts in this directory enable:

1. Storage of credential and experience hash records on the Ethereum blockchain
2. Verification of credentials and experiences using these hash records
3. Revocation of credentials when necessary
4. Tracking of verification status and timestamps

## Smart Contracts

### TrueCred.sol

The main smart contract for the TrueCred platform. It provides functions to:

- Store credential hashes on the blockchain
- Store experience hashes on the blockchain
- Verify the existence and validity of credential hashes
- Verify the existence and validity of experience hashes
- Revoke credentials
- Check the revocation status of credentials

## Compilation and Deployment

### Prerequisites

- Solidity compiler (solc) version 0.8.0 or higher
- Python 3.7 or higher
- Web3.py library
- py-solc-x library

### Compilation

The contract can be compiled using the `compile_contract.py` script:

```bash
python compile_contract.py
```

This will generate the contract ABI and bytecode in the `build` directory.

### Deployment

To deploy the contract to a test network or the main Ethereum network, you'll need:

1. An Ethereum account with sufficient ETH for gas fees
2. Access to a node (Infura, Alchemy, or your own Ethereum node)
3. Environment variables set up for your private key and node URL

## Integration with TrueCred Backend

The TrueCred backend integrates with these smart contracts through the BlockchainService, which provides methods to:

1. Store credential and experience hashes on the blockchain
2. Verify stored credential and experience hashes
3. Check the status of blockchain transactions

## Testing

Smart contract tests are available in the `tests` directory and can be run using:

```bash
pytest tests/test_contract.py
```

## Security Considerations

The smart contracts handle cryptographic hashes and verification of important credentials. Key security considerations include:

1. Only authorized addresses should be able to store or revoke credentials
2. Gas optimizations to reduce transaction costs
3. Protection against replay attacks
4. Proper handling of sensitive data (only hashes are stored on-chain, never the actual credentials)

## License

These smart contracts are licensed under MIT.
