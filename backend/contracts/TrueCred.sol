// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title TrueCred
 * @dev Smart contract for storing and verifying credential and experience hashes
 */
contract TrueCred {
    address public owner;
    
    // Struct to represent a credential or experience hash record
    struct HashRecord {
        bytes32 dataHash;
        address issuer;
        uint256 timestamp;
        bool isRevoked;
    }
    
    // Mapping from credential/experience ID to its hash record
    mapping(bytes32 => HashRecord) private credentialHashes;
    mapping(bytes32 => HashRecord) private experienceHashes;
    
    // Events
    event CredentialHashStored(bytes32 indexed id, bytes32 dataHash, address indexed issuer);
    event ExperienceHashStored(bytes32 indexed id, bytes32 dataHash, address indexed verifier);
    event HashRevoked(bytes32 indexed id, address indexed revoker, uint256 timestamp);
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    modifier onlyIssuer(bytes32 id) {
        require(msg.sender == credentialHashes[id].issuer, "Only issuer can call this function");
        _;
    }
    
    modifier onlyVerifier(bytes32 id) {
        require(msg.sender == experienceHashes[id].issuer, "Only verifier can call this function");
        _;
    }
    
    /**
     * @dev Constructor that sets the owner of the contract
     */
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Store a credential hash on the blockchain
     * @param id Unique identifier for the credential
     * @param dataHash Hash of the credential data
     */
    function storeCredentialHash(bytes32 id, bytes32 dataHash) public {
        require(credentialHashes[id].dataHash == bytes32(0), "Credential hash already exists");
        
        credentialHashes[id] = HashRecord({
            dataHash: dataHash,
            issuer: msg.sender,
            timestamp: block.timestamp,
            isRevoked: false
        });
        
        emit CredentialHashStored(id, dataHash, msg.sender);
    }
    
    /**
     * @dev Store an experience hash on the blockchain
     * @param id Unique identifier for the experience
     * @param dataHash Hash of the experience data
     */
    function storeExperienceHash(bytes32 id, bytes32 dataHash) public {
        require(experienceHashes[id].dataHash == bytes32(0), "Experience hash already exists");
        
        experienceHashes[id] = HashRecord({
            dataHash: dataHash,
            issuer: msg.sender,
            timestamp: block.timestamp,
            isRevoked: false
        });
        
        emit ExperienceHashStored(id, dataHash, msg.sender);
    }
    
    /**
     * @dev Get a credential hash from the blockchain
     * @param id Unique identifier for the credential
     * @return dataHash The stored hash for the credential
     * @return issuer Address of the issuer
     * @return timestamp When the hash was stored
     * @return isRevoked Whether the hash has been revoked
     */
    function getCredentialHash(bytes32 id) public view returns (
        bytes32 dataHash,
        address issuer,
        uint256 timestamp,
        bool isRevoked
    ) {
        HashRecord memory record = credentialHashes[id];
        return (record.dataHash, record.issuer, record.timestamp, record.isRevoked);
    }
    
    /**
     * @dev Get an experience hash from the blockchain
     * @param id Unique identifier for the experience
     * @return dataHash The stored hash for the experience
     * @return issuer Address of the issuer (verifier)
     * @return timestamp When the hash was stored
     * @return isRevoked Whether the hash has been revoked
     */
    function getExperienceHash(bytes32 id) public view returns (
        bytes32 dataHash,
        address issuer,
        uint256 timestamp,
        bool isRevoked
    ) {
        HashRecord memory record = experienceHashes[id];
        return (record.dataHash, record.issuer, record.timestamp, record.isRevoked);
    }
    
    /**
     * @dev Verify a credential hash against the stored hash
     * @param id Unique identifier for the credential
     * @param dataHash Hash to verify
     * @return True if the hash matches and is not revoked, false otherwise
     */
    function verifyCredentialHash(bytes32 id, bytes32 dataHash) public view returns (bool) {
        HashRecord memory record = credentialHashes[id];
        return (record.dataHash == dataHash && !record.isRevoked);
    }
    
    /**
     * @dev Verify an experience hash against the stored hash
     * @param id Unique identifier for the experience
     * @param dataHash Hash to verify
     * @return True if the hash matches and is not revoked, false otherwise
     */
    function verifyExperienceHash(bytes32 id, bytes32 dataHash) public view returns (bool) {
        HashRecord memory record = experienceHashes[id];
        return (record.dataHash == dataHash && !record.isRevoked);
    }
    
    /**
     * @dev Revoke a credential hash (only the issuer can do this)
     * @param id Unique identifier for the credential
     */
    function revokeCredentialHash(bytes32 id) public onlyIssuer(id) {
        require(!credentialHashes[id].isRevoked, "Credential hash already revoked");
        
        credentialHashes[id].isRevoked = true;
        
        emit HashRevoked(id, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Revoke an experience hash (only the verifier can do this)
     * @param id Unique identifier for the experience
     */
    function revokeExperienceHash(bytes32 id) public onlyVerifier(id) {
        require(!experienceHashes[id].isRevoked, "Experience hash already revoked");
        
        experienceHashes[id].isRevoked = true;
        
        emit HashRevoked(id, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Transfer ownership of the contract
     * @param newOwner Address of the new owner
     */
    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "New owner cannot be the zero address");
        owner = newOwner;
    }
}
