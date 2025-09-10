// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

/**
 * @title TrueCred
 * @dev Smart contract for managing verifiable credentials on the blockchain
 * @custom:dev-run-script ./deploy_contract.js
 */
contract TrueCred {
    // ====================== Type Definitions ======================
    
    enum CredentialStatus { Valid, Revoked, Expired }
    
    struct Credential {
        bytes32 id;                  // Unique credential identifier
        address issuer;              // Address that issued the credential
        address subject;             // Address of the credential subject
        string credentialType;       // Type of the credential (e.g., "Diploma", "Certificate")
        string metadataURI;          // IPFS URI pointing to full credential data
        uint256 issuanceDate;        // When the credential was issued
        uint256 expirationDate;      // When the credential expires (0 if no expiration)
        CredentialStatus status;     // Current status of the credential
    }
    
    // ====================== State Variables ======================
    
    // Credential ID to Credential mapping
    mapping(bytes32 => Credential) public credentials;
    
    // Issuer address to bool (whether they are authorized)
    mapping(address => bool) public authorizedIssuers;
    
    // Subject address to credential IDs they own
    mapping(address => bytes32[]) public subjectCredentials;
    
    // Issuer address to credential IDs they issued
    mapping(address => bytes32[]) public issuerCredentials;
    
    address public owner;
    
    // ====================== Events ======================
    
    event IssuerAuthorized(address indexed issuer);
    event IssuerRevoked(address indexed issuer);
    event CredentialIssued(bytes32 indexed credentialId, address indexed issuer, address indexed subject);
    event CredentialRevoked(bytes32 indexed credentialId, address indexed revokedBy);
    event CredentialVerified(bytes32 indexed credentialId, bool valid);
    event BatchCredentialsIssued(bytes32[] credentialIds, address issuer);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    
    // ====================== Modifiers ======================
    
    modifier onlyOwner() {
        require(msg.sender == owner, "TrueCred: caller is not the owner");
        _;
    }
    
    modifier onlyAuthorizedIssuer() {
        require(authorizedIssuers[msg.sender], "TrueCred: caller is not an authorized issuer");
        _;
    }
    
    modifier credentialExists(bytes32 credentialId) {
        require(credentials[credentialId].issuer != address(0), "TrueCred: credential does not exist");
        _;
    }
    
    // ====================== Constructor ======================
    
    constructor() {
        owner = msg.sender;
        authorizedIssuers[msg.sender] = true; // Owner is an authorized issuer by default
        emit IssuerAuthorized(msg.sender);
        emit OwnershipTransferred(address(0), msg.sender);
    }
    
    // ====================== External Functions ======================
    
    /**
     * @dev Authorize an address to issue credentials
     * @param issuer Address to authorize
     */
    function authorizeIssuer(address issuer) external onlyOwner {
        require(issuer != address(0), "TrueCred: invalid issuer address");
        require(!authorizedIssuers[issuer], "TrueCred: issuer already authorized");
        
        authorizedIssuers[issuer] = true;
        emit IssuerAuthorized(issuer);
    }
    
    /**
     * @dev Revoke an issuer's authorization
     * @param issuer Address to revoke
     */
    function revokeIssuer(address issuer) external onlyOwner {
        require(authorizedIssuers[issuer], "TrueCred: issuer not authorized");
        require(issuer != owner, "TrueCred: cannot revoke owner as issuer");
        
        authorizedIssuers[issuer] = false;
        emit IssuerRevoked(issuer);
    }
    
    /**
     * @dev Issue a new credential
     * @param credentialId Unique identifier for the credential
     * @param subject Address of the credential subject
     * @param credentialType Type of credential being issued
     * @param metadataURI IPFS URI to the credential metadata
     * @param expirationDate Optional expiration date (0 for no expiration)
     * @return success Whether the credential was successfully issued
     */
    function issueCredential(
        bytes32 credentialId,
        address subject,
        string calldata credentialType,
        string calldata metadataURI,
        uint256 expirationDate
    ) external onlyAuthorizedIssuer returns (bool success) {
        require(credentials[credentialId].issuer == address(0), "TrueCred: credential ID already exists");
        require(subject != address(0), "TrueCred: invalid subject address");
        require(bytes(credentialType).length > 0, "TrueCred: credential type cannot be empty");
        require(bytes(metadataURI).length > 0, "TrueCred: metadata URI cannot be empty");
        
        Credential memory newCredential = Credential({
            id: credentialId,
            issuer: msg.sender,
            subject: subject,
            credentialType: credentialType,
            metadataURI: metadataURI,
            issuanceDate: block.timestamp,
            expirationDate: expirationDate,
            status: CredentialStatus.Valid
        });
        
        credentials[credentialId] = newCredential;
        subjectCredentials[subject].push(credentialId);
        issuerCredentials[msg.sender].push(credentialId);
        
        emit CredentialIssued(credentialId, msg.sender, subject);
        
        return true;
    }
    
    /**
     * @dev Issue multiple credentials in a batch
     * @param credentialIds Array of credential IDs
     * @param subjects Array of subject addresses
     * @param credentialTypes Array of credential types
     * @param metadataURIs Array of IPFS URIs
     * @param expirationDates Array of expiration dates
     * @return success Whether all credentials were successfully issued
     */
    function batchIssueCredentials(
        bytes32[] calldata credentialIds,
        address[] calldata subjects,
        string[] calldata credentialTypes,
        string[] calldata metadataURIs,
        uint256[] calldata expirationDates
    ) external onlyAuthorizedIssuer returns (bool success) {
        uint256 length = credentialIds.length;
        require(
            subjects.length == length && 
            credentialTypes.length == length && 
            metadataURIs.length == length && 
            expirationDates.length == length,
            "TrueCred: input arrays must have the same length"
        );
        
        for (uint256 i = 0; i < length; i++) {
            bytes32 credentialId = credentialIds[i];
            require(credentials[credentialId].issuer == address(0), "TrueCred: credential ID already exists");
            
            Credential memory newCredential = Credential({
                id: credentialId,
                issuer: msg.sender,
                subject: subjects[i],
                credentialType: credentialTypes[i],
                metadataURI: metadataURIs[i],
                issuanceDate: block.timestamp,
                expirationDate: expirationDates[i],
                status: CredentialStatus.Valid
            });
            
            credentials[credentialId] = newCredential;
            subjectCredentials[subjects[i]].push(credentialId);
            issuerCredentials[msg.sender].push(credentialId);
            
            emit CredentialIssued(credentialId, msg.sender, subjects[i]);
        }
        
        emit BatchCredentialsIssued(credentialIds, msg.sender);
        
        return true;
    }
    
    /**
     * @dev Revoke a credential
     * @param credentialId ID of the credential to revoke
     * @return success Whether the credential was successfully revoked
     */
    function revokeCredential(bytes32 credentialId) 
        external 
        credentialExists(credentialId) 
        returns (bool success) 
    {
        Credential storage credential = credentials[credentialId];
        
        // Only the issuer or the contract owner can revoke
        require(
            credential.issuer == msg.sender || msg.sender == owner,
            "TrueCred: caller is not authorized to revoke this credential"
        );
        
        require(credential.status == CredentialStatus.Valid, "TrueCred: credential is not valid");
        
        credential.status = CredentialStatus.Revoked;
        
        emit CredentialRevoked(credentialId, msg.sender);
        
        return true;
    }
    
    /**
     * @dev Verify a credential's validity
     * @param credentialId ID of the credential to verify
     * @return valid Whether the credential is valid
     * @return status The credential's current status
     * @return issuer The issuer of the credential
     */
    function verifyCredential(bytes32 credentialId) 
        external 
        credentialExists(credentialId)
        returns (bool valid, CredentialStatus status, address issuer) 
    {
        Credential memory credential = credentials[credentialId];
        
        // Check if credential is expired
        if (credential.expirationDate != 0 && block.timestamp > credential.expirationDate) {
            // Update status if needed
            if (credentials[credentialId].status == CredentialStatus.Valid) {
                credentials[credentialId].status = CredentialStatus.Expired;
            }
            valid = false;
            status = CredentialStatus.Expired;
        } else {
            valid = (credential.status == CredentialStatus.Valid);
            status = credential.status;
        }
        
        issuer = credential.issuer;
        
        emit CredentialVerified(credentialId, valid);
        
        return (valid, status, issuer);
    }
    
    /**
     * @dev Get detailed information about a credential
     * @param credentialId ID of the credential to get details for
     * @return The complete credential struct
     */
    function getCredentialDetails(bytes32 credentialId) 
        external 
        view 
        credentialExists(credentialId)
        returns (Credential memory) 
    {
        return credentials[credentialId];
    }
    
    /**
     * @dev Get all credential IDs owned by a subject
     * @param subject Address of the subject
     * @return Array of credential IDs
     */
    function getSubjectCredentials(address subject) external view returns (bytes32[] memory) {
        return subjectCredentials[subject];
    }
    
    /**
     * @dev Get all credential IDs issued by an issuer
     * @param issuer Address of the issuer
     * @return Array of credential IDs
     */
    function getIssuerCredentials(address issuer) external view returns (bytes32[] memory) {
        return issuerCredentials[issuer];
    }
    
    /**
     * @dev Transfer ownership of the contract
     * @param newOwner Address of the new owner
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "TrueCred: new owner is the zero address");
        address oldOwner = owner;
        owner = newOwner;
        
        // Make the new owner an authorized issuer automatically
        if (!authorizedIssuers[newOwner]) {
            authorizedIssuers[newOwner] = true;
            emit IssuerAuthorized(newOwner);
        }
        
        emit OwnershipTransferred(oldOwner, newOwner);
    }
    
    /**
     * @dev Check if an address is an authorized issuer
     * @param issuer Address to check
     * @return Whether the address is authorized
     */
    function isAuthorizedIssuer(address issuer) external view returns (bool) {
        return authorizedIssuers[issuer];
    }
}
