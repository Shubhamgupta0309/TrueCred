# IPFS Integration for TrueCred

This document outlines the IPFS (InterPlanetary File System) integration for the TrueCred platform.

## Overview

TrueCred uses IPFS for decentralized document storage, providing:

1. **Content addressing** - Files are accessed by their content hash, not location
2. **Data integrity** - Content verification through cryptographic hashes
3. **Decentralized storage** - No single point of failure for document storage
4. **Persistent availability** - Documents remain available even if the original server goes offline

## Setup

### Prerequisites

1. Install IPFS Desktop or IPFS Daemon:

   - Desktop: https://docs.ipfs.io/install/ipfs-desktop/
   - CLI: https://docs.ipfs.io/install/command-line/

2. Initialize IPFS:

   ```
   ipfs init
   ```

3. Start the IPFS daemon:
   ```
   ipfs daemon
   ```

### Automated Setup

For convenience, we provide setup scripts:

- Windows: `setup_ipfs.bat`
- Linux/Mac: `setup_ipfs.sh`

These scripts:

1. Check if IPFS is installed
2. Initialize IPFS if needed
3. Configure CORS settings
4. Start the IPFS daemon

## Configuration

The IPFS service uses the following environment variables:

- `IPFS_API_URL`: URL of the IPFS API endpoint (default: `http://localhost:5001`)
- `IPFS_GATEWAY_URL`: URL of the IPFS HTTP gateway (default: `http://localhost:8080`)

These can be configured in the `.env` file:

```
IPFS_API_URL=http://localhost:5001
IPFS_GATEWAY_URL=https://ipfs.io
```

## Architecture

The IPFS integration consists of:

1. **IPFS Service** (`services/ipfs_service.py`):

   - Handles connection to IPFS nodes
   - Provides methods to store and retrieve documents
   - Manages pinning for persistent storage

2. **IPFS Utilities** (`utils/ipfs.py`):

   - Helper functions for IPFS operations
   - MIME type detection
   - Metadata creation

3. **API Routes** (`routes/ipfs.py`):

   - REST API endpoints for IPFS operations
   - Document upload/download
   - IPFS node status

4. **Model Extensions**:
   - `Credential` and `Experience` models have been extended to store IPFS hashes
   - Methods to store documents in IPFS

## Usage

### Storing Documents

Documents can be stored in IPFS in several ways:

1. **Through API endpoints**:

   ```
   POST /api/ipfs/upload
   ```

   With form data or JSON containing file data and optional metadata.

2. **Through model methods**:

   ```python
   # Store credential with document
   credential.store_in_ipfs(ipfs_service, document_data, metadata)

   # Add another document to credential
   credential.add_document_to_ipfs(ipfs_service, document_data, "transcript")
   ```

### Retrieving Documents

Documents can be retrieved by their IPFS hash:

1. **Through API endpoints**:

   ```
   GET /api/ipfs/retrieve/<ipfs_hash>
   ```

2. **Through gateway redirect**:

   ```
   GET /api/ipfs/gateway/<ipfs_hash>
   ```

   Redirects to an IPFS gateway URL.

3. **Directly through IPFS gateway**:
   ```
   https://ipfs.io/ipfs/<hash>
   ```

### Document Metadata

When storing documents, metadata is also stored in IPFS:

1. **Document Hash**: Hash of the actual document
2. **Metadata Hash**: Hash of the JSON metadata
3. **Combined Storage**: Both hashes are stored in the credential/experience

The metadata includes:

- User information
- Timestamp
- Filename
- Custom metadata

## Security Considerations

1. **Access Control**: Only document owners can access their documents through the API
2. **Privacy**: Sensitive documents should be encrypted before storage
3. **Permanence**: Once on IPFS, documents are difficult to remove completely

## Testing

Test the IPFS integration using:

```
python -m tests.test_ipfs_integration
```

This script tests:

1. IPFS service connectivity
2. File and JSON storage/retrieval
3. Model integration

## Troubleshooting

Common issues:

1. **IPFS daemon not running**:

   - Start with `ipfs daemon`
   - Check status with `ipfs id`

2. **Connection refused**:

   - Verify API URL in `.env`
   - Check CORS configuration: `ipfs config --json API.HTTPHeaders.Access-Control-Allow-Origin '["*"]'`

3. **Cannot retrieve files**:
   - Ensure the file is pinned: `ipfs pin add <hash>`
   - Try using a public gateway like `https://ipfs.io/ipfs/<hash>`
