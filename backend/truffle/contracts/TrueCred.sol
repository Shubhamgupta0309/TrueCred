// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TrueCred {
    struct Credential {
        string title;
        string issuer;
        string studentId;
        string ipfsHash;
        uint256 timestamp;
        bool isValid;
    }

    mapping(bytes32 => Credential) public credentials;
    mapping(address => bool) public authorizedIssuers;
    address public owner;

    event CredentialStored(bytes32 indexed credentialId, string title, string issuer, string studentId, string ipfsHash);
    event CredentialRevoked(bytes32 indexed credentialId);
    event IssuerAuthorized(address indexed issuer);
    event IssuerRevoked(address indexed issuer);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    modifier onlyAuthorizedIssuer() {
        require(authorizedIssuers[msg.sender] || msg.sender == owner, "Not authorized to issue credentials");
        _;
    }

    constructor() {
        owner = msg.sender;
        authorizedIssuers[msg.sender] = true;
    }

    function authorizeIssuer(address issuer) public onlyOwner {
        authorizedIssuers[issuer] = true;
        emit IssuerAuthorized(issuer);
    }

    function revokeIssuer(address issuer) public onlyOwner {
        authorizedIssuers[issuer] = false;
        emit IssuerRevoked(issuer);
    }

    function storeCredential(
        string memory _title,
        string memory _issuer,
        string memory _studentId,
        string memory _ipfsHash
    ) public onlyAuthorizedIssuer returns (bytes32) {
        bytes32 credentialId = keccak256(abi.encodePacked(_title, _issuer, _studentId, _ipfsHash, block.timestamp));

        credentials[credentialId] = Credential({
            title: _title,
            issuer: _issuer,
            studentId: _studentId,
            ipfsHash: _ipfsHash,
            timestamp: block.timestamp,
            isValid: true
        });

        emit CredentialStored(credentialId, _title, _issuer, _studentId, _ipfsHash);
        return credentialId;
    }

    function revokeCredential(bytes32 credentialId) public onlyAuthorizedIssuer {
        require(credentials[credentialId].isValid, "Credential not found or already revoked");
        credentials[credentialId].isValid = false;
        emit CredentialRevoked(credentialId);
    }

    function verifyCredential(bytes32 credentialId) public view returns (
        string memory title,
        string memory issuer,
        string memory studentId,
        string memory ipfsHash,
        uint256 timestamp,
        bool isValid
    ) {
        Credential memory cred = credentials[credentialId];
        return (
            cred.title,
            cred.issuer,
            cred.studentId,
            cred.ipfsHash,
            cred.timestamp,
            cred.isValid
        );
    }

    function getCredential(bytes32 credentialId) public view returns (Credential memory) {
        return credentials[credentialId];
    }

    function isCredentialValid(bytes32 credentialId) public view returns (bool) {
        return credentials[credentialId].isValid;
    }
}