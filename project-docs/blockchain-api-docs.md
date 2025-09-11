# TrueCred Blockchain API Documentation

## Base URL

All blockchain API endpoints are prefixed with `/api/blockchain`.

## Authentication

Most endpoints require authentication via a JWT token in the `Authorization` header:

```
Authorization: Bearer <token>
```

## Endpoints

### Blockchain Status

#### GET /api/blockchain/info

Returns information about the blockchain connection status.

**Authentication Required**: Yes

**Response**:

```json
{
  "success": true,
  "data": {
    "network": "goerli",
    "provider_url": "https://goerli.infura.io/v3/your-project-id",
    "connected": true,
    "chain_id": 5,
    "contract_loaded": true,
    "contract_address": "0x1234567890123456789012345678901234567890"
  }
}
```

### Credential Management

#### POST /api/blockchain/credentials/:credential_id/prepare

Prepares a credential for blockchain by generating its hash.

**Authentication Required**: Yes

**URL Parameters**:

- `credential_id`: ID of the credential to prepare

**Response**:

```json
{
  "success": true,
  "message": "Credential prepared for blockchain successfully",
  "data": {
    "credential_id": "123e4567-e89b-12d3-a456-426614174000",
    "data_hash": "0x1234567890123456789012345678901234567890123456789012345678901234",
    "timestamp": "2023-09-15T12:34:56Z",
    "blockchain_ready": true
  }
}
```

#### POST /api/blockchain/credentials/:credential_id/store

Stores a credential hash on the blockchain.

**Authentication Required**: Yes

**URL Parameters**:

- `credential_id`: ID of the credential to store

**Response**:

```json
{
  "success": true,
  "message": "Credential hash stored on blockchain",
  "data": {
    "credential_id": "123e4567-e89b-12d3-a456-426614174000",
    "transaction_hash": "0x1234567890123456789012345678901234567890123456789012345678901234",
    "block_number": 12345678,
    "timestamp": "2023-09-15T12:34:56Z",
    "status": "confirmed"
  }
}
```

#### POST /api/blockchain/credentials/:credential_id/verify

Verifies a credential hash against the blockchain.

**Authentication Required**: Yes

**URL Parameters**:

- `credential_id`: ID of the credential to verify

**Response**:

```json
{
  "success": true,
  "message": "Credential verified successfully",
  "data": {
    "credential_id": "123e4567-e89b-12d3-a456-426614174000",
    "verified": true,
    "issuer": "0x1234567890123456789012345678901234567890",
    "timestamp": "2023-09-15T12:34:56Z",
    "is_revoked": false
  }
}
```

#### POST /api/blockchain/credentials/:credential_id/revoke

Revokes a credential on the blockchain.

**Authentication Required**: Yes (must be the issuer)

**URL Parameters**:

- `credential_id`: ID of the credential to revoke

**Response**:

```json
{
  "success": true,
  "message": "Credential revoked successfully",
  "data": {
    "credential_id": "123e4567-e89b-12d3-a456-426614174000",
    "transaction_hash": "0x1234567890123456789012345678901234567890123456789012345678901234",
    "block_number": 12345678,
    "timestamp": "2023-09-15T12:34:56Z",
    "status": "confirmed"
  }
}
```

### Experience Management

#### POST /api/blockchain/experiences/:experience_id/prepare

Prepares an experience for blockchain by generating its hash.

**Authentication Required**: Yes

**URL Parameters**:

- `experience_id`: ID of the experience to prepare

**Response**:

```json
{
  "success": true,
  "message": "Experience prepared for blockchain successfully",
  "data": {
    "experience_id": "123e4567-e89b-12d3-a456-426614174000",
    "data_hash": "0x1234567890123456789012345678901234567890123456789012345678901234",
    "timestamp": "2023-09-15T12:34:56Z",
    "blockchain_ready": true
  }
}
```

#### POST /api/blockchain/experiences/:experience_id/store

Stores an experience hash on the blockchain.

**Authentication Required**: Yes

**URL Parameters**:

- `experience_id`: ID of the experience to store

**Response**:

```json
{
  "success": true,
  "message": "Experience hash stored on blockchain",
  "data": {
    "experience_id": "123e4567-e89b-12d3-a456-426614174000",
    "transaction_hash": "0x1234567890123456789012345678901234567890123456789012345678901234",
    "block_number": 12345678,
    "timestamp": "2023-09-15T12:34:56Z",
    "status": "confirmed"
  }
}
```

#### POST /api/blockchain/experiences/:experience_id/verify

Verifies an experience hash against the blockchain.

**Authentication Required**: Yes

**URL Parameters**:

- `experience_id`: ID of the experience to verify

**Response**:

```json
{
  "success": true,
  "message": "Experience verified successfully",
  "data": {
    "experience_id": "123e4567-e89b-12d3-a456-426614174000",
    "verified": true,
    "verifier": "0x1234567890123456789012345678901234567890",
    "timestamp": "2023-09-15T12:34:56Z",
    "is_revoked": false
  }
}
```

#### POST /api/blockchain/experiences/:experience_id/revoke

Revokes an experience on the blockchain.

**Authentication Required**: Yes (must be the verifier)

**URL Parameters**:

- `experience_id`: ID of the experience to revoke

**Response**:

```json
{
  "success": true,
  "message": "Experience revoked successfully",
  "data": {
    "experience_id": "123e4567-e89b-12d3-a456-426614174000",
    "transaction_hash": "0x1234567890123456789012345678901234567890123456789012345678901234",
    "block_number": 12345678,
    "timestamp": "2023-09-15T12:34:56Z",
    "status": "confirmed"
  }
}
```

### Transaction Management

#### GET /api/blockchain/transactions

Gets a list of recent blockchain transactions.

**Authentication Required**: Yes

**Query Parameters**:

- `limit` (optional): Maximum number of transactions to return (default: 10)
- `status` (optional): Filter by transaction status ('pending', 'confirmed', 'failed')
- `type` (optional): Filter by transaction type ('credential_issuance', 'experience_verification', etc.)

**Response**:

```json
{
  "success": true,
  "data": [
    {
      "transaction_hash": "0x1234567890123456789012345678901234567890123456789012345678901234",
      "block_number": 12345678,
      "timestamp": "2023-09-15T12:34:56Z",
      "status": "confirmed",
      "type": "credential_issuance",
      "item_id": "123e4567-e89b-12d3-a456-426614174000",
      "gas_used": 150000,
      "network": "goerli"
    },
    {
      "transaction_hash": "0x2345678901234567890123456789012345678901234567890123456789012345",
      "block_number": null,
      "timestamp": "2023-09-15T12:45:56Z",
      "status": "pending",
      "type": "experience_verification",
      "item_id": "234e5678-e89b-12d3-a456-426614174001",
      "gas_used": null,
      "network": "goerli"
    }
  ]
}
```

#### GET /api/blockchain/transactions/:tx_hash

Gets details for a specific transaction.

**Authentication Required**: Yes

**URL Parameters**:

- `tx_hash`: Transaction hash

**Response**:

```json
{
  "success": true,
  "data": {
    "transaction_hash": "0x1234567890123456789012345678901234567890123456789012345678901234",
    "block_number": 12345678,
    "timestamp": "2023-09-15T12:34:56Z",
    "status": "confirmed",
    "type": "credential_issuance",
    "item_id": "123e4567-e89b-12d3-a456-426614174000",
    "data_hash": "0x1234567890123456789012345678901234567890123456789012345678901234",
    "gas_used": 150000,
    "gas_price": 20000000000,
    "total_cost": "0.003",
    "network": "goerli",
    "issuer_address": "0x1234567890123456789012345678901234567890",
    "error": null
  }
}
```

### Batch Operations

#### POST /api/blockchain/credentials/batch

Performs batch operations for multiple credentials.

**Authentication Required**: Yes

**Request Body**:

```json
{
  "operation": "store",
  "credential_ids": [
    "123e4567-e89b-12d3-a456-426614174000",
    "234e5678-e89b-12d3-a456-426614174001",
    "345e6789-e89b-12d3-a456-426614174002"
  ]
}
```

**Response**:

```json
{
  "success": true,
  "message": "Batch operation initiated",
  "data": {
    "transaction_hash": "0x1234567890123456789012345678901234567890123456789012345678901234",
    "status": "pending",
    "credential_count": 3,
    "timestamp": "2023-09-15T12:34:56Z"
  }
}
```

## Error Handling

All endpoints return appropriate HTTP status codes and error messages in case of failure:

```json
{
  "success": false,
  "message": "Error message describing the issue",
  "error_code": "ERROR_CODE",
  "status_code": 400
}
```

Common error codes:

- `BLOCKCHAIN_DISCONNECTED`: Blockchain connection is not available
- `CONTRACT_NOT_LOADED`: Smart contract is not loaded
- `UNAUTHORIZED`: User is not authorized to perform this action
- `INVALID_CREDENTIAL`: Credential does not exist or is invalid
- `TRANSACTION_FAILED`: Transaction failed to execute
- `ALREADY_ON_BLOCKCHAIN`: Item is already stored on the blockchain
