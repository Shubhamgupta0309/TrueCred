# Verification System Documentation

## Overview

The TrueCred verification system provides comprehensive verification of credentials and experiences using multiple verification methods:

1. **Manual Verification**: Credentials and experiences can be verified manually by authorized verifiers.
2. **Blockchain Verification**: Credentials and experiences can be verified by comparing their hash on the Ethereum blockchain.
3. **IPFS Verification**: Credentials and experiences can be verified by retrieving the original document from IPFS.

The verification system integrates these methods to provide a unified verification status for each credential and experience.

## Components

### Verification Service

The main service that coordinates verification across different methods. It provides:

- Individual verification of credentials and experiences
- Batch verification of multiple credentials or experiences
- User profile verification (all credentials and experiences for a user)
- Verification score calculation for user profiles

### Blockchain Service

Handles interaction with the Ethereum blockchain for verification:

- Storing credential and experience hashes on the blockchain
- Retrieving and verifying hashes against the blockchain
- Managing blockchain transactions

### IPFS Service

Handles interaction with IPFS for decentralized document storage and verification:

- Storing documents and their metadata on IPFS
- Retrieving documents and metadata from IPFS
- Validating document existence and integrity

## Verification Flow

1. **Request Verification**:

   - User requests verification for a credential or experience
   - System records the request and notifies verifiers

2. **Verification Process**:

   - Manual verification: An authorized verifier reviews and approves the credential or experience
   - Blockchain verification: System checks if the hash exists on the blockchain and matches
   - IPFS verification: System checks if the document exists on IPFS and can be retrieved

3. **Verification Result**:
   - System combines results from all verification methods
   - Credential or experience is marked as verified if at least one method succeeds
   - Verification data is stored with the credential or experience

## API Endpoints

### Verification Requests

- `POST /api/verification/experience/request/{experience_id}`: Request verification for an experience
- `POST /api/verification/credential/request/{credential_id}`: Request verification for a credential

### Manual Verification

- `POST /api/verification/experience/verify/{experience_id}`: Manually verify an experience
- `POST /api/verification/credential/verify/{credential_id}`: Manually verify a credential
- `POST /api/verification/experience/reject/{experience_id}`: Reject experience verification
- `POST /api/verification/credential/reject/{credential_id}`: Reject credential verification

### Blockchain/IPFS Verification

- `GET /api/verification/experience/verify-blockchain/{experience_id}`: Verify experience using blockchain/IPFS
- `GET /api/verification/credential/verify-blockchain/{credential_id}`: Verify credential using blockchain/IPFS

### Batch Verification

- `POST /api/verification/batch/experiences`: Verify multiple experiences
- `POST /api/verification/batch/credentials`: Verify multiple credentials

### Profile Verification

- `GET /api/verification/user-profile/{user_id}`: Verify all credentials and experiences for a user

## Verification Score

The verification score is a measure of the overall verification status of a user's profile. It is calculated as a weighted average:

- Credential verification: 60% weight
- Experience verification: 40% weight

For each category, the score is the percentage of verified items.

## Smart Contract

The TrueCred smart contract provides the following functions for verification:

- `verifyCredentialHash(bytes32 id, bytes32 dataHash)`: Verify a credential hash
- `verifyExperienceHash(bytes32 id, bytes32 dataHash)`: Verify an experience hash
- `getCredentialHash(bytes32 id)`: Get the stored hash for a credential
- `getExperienceHash(bytes32 id)`: Get the stored hash for an experience

## Security Considerations

- Manual verification requires proper authorization (verifier or admin role)
- Blockchain verification is publicly accessible without authentication
- Credential and experience data should be properly hashed before storage
- Proper error handling and logging are implemented throughout the system

## Example Usage

### Verify a Credential

```python
# Initialize verification service
verification_service = VerificationService()

# Verify credential
result = verification_service.verify_credential(
    credential_id="credential_123",
    verifier_id="verifier_456"  # Optional, for manual verification
)

# Check result
if result["verified"]:
    print(f"Credential verified using methods: {result['verification_methods']}")
else:
    print(f"Verification failed: {result['status']}")
```

### Verify a User Profile

```python
# Initialize verification service
verification_service = VerificationService()

# Verify user profile
result = verification_service.verify_user_profile(user_id="user_123")

# Check results
print(f"User: {result['username']}")
print(f"Verification score: {result['summary']['verification_score']}")
print(f"Verified credentials: {result['summary']['verified_credentials']} of {result['summary']['total_credentials']}")
print(f"Verified experiences: {result['summary']['verified_experiences']} of {result['summary']['total_experiences']}")
```
