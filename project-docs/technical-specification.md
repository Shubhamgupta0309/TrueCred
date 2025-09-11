# TrueCred Technical Specification

This document provides detailed technical specifications for the remaining work on the TrueCred project.

## Smart Contract Development

### TrueCred.sol Contract

#### Core Functions

1. **Credential Management**

   ```solidity
   // Issue a new credential
   function issueCredential(address to, bytes32 credentialHash, string memory metadata) external returns (uint256);

   // Revoke an existing credential
   function revokeCredential(uint256 credentialId) external;

   // Verify a credential
   function verifyCredential(uint256 credentialId, bytes32 credentialHash) external view returns (bool);
   ```

2. **Experience Verification**

   ```solidity
   // Add experience record
   function addExperience(address user, bytes32 experienceHash, string memory metadata) external returns (uint256);

   // Verify experience
   function verifyExperience(uint256 experienceId) external;

   // Revoke experience verification
   function revokeExperienceVerification(uint256 experienceId) external;
   ```

3. **Access Control**

   ```solidity
   // Implement role-based access control
   // Roles: ADMIN, ISSUER, VERIFIER, USER

   // Add issuer (only admin)
   function addIssuer(address issuer) external;

   // Add verifier (only admin)
   function addVerifier(address verifier) external;
   ```

4. **Events**
   ```solidity
   // Events for tracking
   event CredentialIssued(uint256 indexed credentialId, address indexed to, address indexed issuer);
   event CredentialRevoked(uint256 indexed credentialId, address indexed revoker);
   event ExperienceAdded(uint256 indexed experienceId, address indexed user);
   event ExperienceVerified(uint256 indexed experienceId, address indexed verifier);
   ```

#### Contract Deployment & Testing

1. **compile_contract.py**

   - Update to include:
     - Solidity compilation
     - ABI generation
     - Bytecode output
     - Contract interface generation

2. **Deployment Scripts**

   - Create `deploy_local.py` for Ganache deployment
   - Create `deploy_testnet.py` for testnet deployment
   - Store contract addresses in configuration

3. **Testing Framework**
   - Create unit tests for all contract functions
   - Set up continuous integration for contract testing

## Backend Development

### API Endpoints

1. **Credential Management API**

   ```python
   # Issue credential
   @app.route('/api/credentials', methods=['POST'])

   # Verify credential
   @app.route('/api/credentials/<credential_id>/verify', methods=['POST'])

   # Revoke credential
   @app.route('/api/credentials/<credential_id>/revoke', methods=['POST'])

   # Get credential
   @app.route('/api/credentials/<credential_id>', methods=['GET'])

   # List credentials
   @app.route('/api/credentials', methods=['GET'])
   ```

2. **Experience Verification API**

   ```python
   # Add experience
   @app.route('/api/experiences', methods=['POST'])

   # Verify experience
   @app.route('/api/experiences/<experience_id>/verify', methods=['POST'])

   # Get experience
   @app.route('/api/experiences/<experience_id>', methods=['GET'])

   # List experiences
   @app.route('/api/experiences', methods=['GET'])
   ```

3. **Third-Party Verification API**

   ```python
   # Request third-party verification
   @app.route('/api/verification/request', methods=['POST'])

   # Respond to verification request
   @app.route('/api/verification/respond/<request_id>', methods=['POST'])
   ```

### Database Models

1. **Credential Model**

   ```python
   class Credential(Document):
       id = StringField(primary_key=True)
       blockchain_id = IntField(required=True)
       holder = ReferenceField(User, required=True)
       issuer = ReferenceField(User, required=True)
       credential_type = StringField(required=True)
       metadata = DictField()
       hash = StringField(required=True)
       status = StringField(required=True, choices=['ACTIVE', 'REVOKED'])
       ipfs_hash = StringField()
       created_at = DateTimeField(default=datetime.utcnow)
       updated_at = DateTimeField(default=datetime.utcnow)
   ```

2. **Experience Model**

   ```python
   class Experience(Document):
       id = StringField(primary_key=True)
       blockchain_id = IntField(required=True)
       user = ReferenceField(User, required=True)
       company = ReferenceField(User, required=True)
       title = StringField(required=True)
       description = StringField()
       start_date = DateTimeField(required=True)
       end_date = DateTimeField()
       verification_status = StringField(required=True, choices=['PENDING', 'VERIFIED', 'REJECTED'])
       hash = StringField(required=True)
       metadata = DictField()
       created_at = DateTimeField(default=datetime.utcnow)
       updated_at = DateTimeField(default=datetime.utcnow)
   ```

3. **Verification Record Model**
   ```python
   class VerificationRecord(Document):
       id = StringField(primary_key=True)
       verifier = ReferenceField(User, required=True)
       target_type = StringField(required=True, choices=['CREDENTIAL', 'EXPERIENCE'])
       target_id = StringField(required=True)
       verification_date = DateTimeField(default=datetime.utcnow)
       status = StringField(required=True, choices=['VERIFIED', 'REJECTED'])
       notes = StringField()
   ```

### Web3 & IPFS Integration

1. **Web3 Service**

   - Connect to Ethereum nodes
   - Handle contract interactions
   - Manage wallet credentials
   - Process transaction receipts

2. **IPFS Service**
   - Initialize IPFS connection
   - Store documents and metadata
   - Retrieve documents by hash
   - Verify document integrity

## Frontend Development

### User Interface Components

1. **Dashboard Components**

   - User Dashboard with credential display
   - College Dashboard for issuing credentials
   - Company Dashboard for verifying experiences
   - Admin Dashboard for system management

2. **Credential Components**

   - Credential Card with verification status
   - Credential Request Form
   - Credential Verification UI
   - Credential Badge for sharing

3. **Experience Components**
   - Experience Card with verification status
   - Experience Add/Edit Form
   - Experience Verification UI

### Blockchain Integration (Frontend)

1. **Wallet Connection**

   - MetaMask integration
   - Transaction signing
   - Address display and management

2. **Transaction Handling**

   - Transaction status monitoring
   - Gas estimation
   - Error handling and retries

3. **Verification Badge System**
   - Generate visual verification badges
   - QR codes for verification
   - Embeddable verification widgets

### State Management & API Connection

1. **State Management**

   - Context API for global state
   - Local state for component-specific data
   - Caching strategies for blockchain data

2. **API Service Layer**
   - Axios instance configuration
   - Request/response interceptors
   - Error handling and retries
   - Authentication token management

## Testing Strategy

### Unit Testing

- Smart contract unit tests with Truffle
- Backend API tests with Pytest
- Frontend component tests with Jest

### Integration Testing

- Contract-Backend integration tests
- Backend-Frontend integration tests
- Blockchain transaction flow tests

### End-to-End Testing

- Complete user journey tests
- Performance testing under load
- Security vulnerability testing

## Deployment Plan

### Development Environment

- Local Ganache blockchain
- MongoDB local instance
- Local IPFS node
- Development servers

### Testing Environment

- Ethereum testnet (Sepolia)
- MongoDB Atlas development cluster
- Infura IPFS
- Staging servers

### Production Environment

- Ethereum mainnet
- MongoDB Atlas production cluster
- Dedicated IPFS infrastructure
- Production servers with load balancing
