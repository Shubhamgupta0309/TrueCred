// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TrueCred {
    struct Credential {
        string title;
        string issuer;
        string studentId;
        string studentName;
        string ipfsHash;
        string metadata; // JSON string with additional credential data
        uint256 timestamp;
        uint256 expirationDate; // 0 means no expiration
        bool isValid;
        uint8 credentialType; // 0: degree, 1: certificate, 2: experience, 3: skill
    }

    struct Issuer {
        string name;
        string institution;
        bool isActive;
        uint256 totalCredentials;
        uint256 reputation; // 0-100 score
    }

    mapping(bytes32 => Credential) public credentials;
    mapping(address => Issuer) public issuers;
    mapping(address => bool) public authorizedIssuers;
    mapping(bytes32 => bool) public revokedCredentials;
    mapping(string => bytes32[]) public studentCredentials; // studentId => credentialIds

    address public owner;
    uint256 public totalCredentials;
    uint256 public totalIssuers;

    // Events
    event CredentialStored(bytes32 indexed credentialId, string title, string issuer, string studentId, string ipfsHash);
    event CredentialRevoked(bytes32 indexed credentialId, string reason);
    event CredentialExpired(bytes32 indexed credentialId);
    event IssuerAuthorized(address indexed issuer, string name, string institution);
    event IssuerRevoked(address indexed issuer);
    event BatchCredentialsStored(bytes32[] credentialIds, uint256 count);
    event CredentialVerified(bytes32 indexed credentialId, address indexed verifier);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    modifier onlyAuthorizedIssuer() {
        require(authorizedIssuers[msg.sender] || msg.sender == owner, "Not authorized to issue credentials");
        _;
    }

    modifier validCredential(bytes32 credentialId) {
        require(credentials[credentialId].timestamp != 0, "Credential does not exist");
        require(credentials[credentialId].isValid, "Credential has been revoked");
        if (credentials[credentialId].expirationDate != 0) {
            require(block.timestamp <= credentials[credentialId].expirationDate, "Credential has expired");
        }
        _;
    }

    constructor() {
        owner = msg.sender;
        authorizedIssuers[msg.sender] = true;
        issuers[msg.sender] = Issuer({
            name: "TrueCred Admin",
            institution: "TrueCred",
            isActive: true,
            totalCredentials: 0,
            reputation: 100
        });
        totalIssuers = 1;
    }

    // Enhanced issuer management
    function authorizeIssuer(
        address issuer,
        string memory name,
        string memory institution
    ) public onlyOwner {
        require(!authorizedIssuers[issuer], "Issuer already authorized");

        authorizedIssuers[issuer] = true;
        issuers[issuer] = Issuer({
            name: name,
            institution: institution,
            isActive: true,
            totalCredentials: 0,
            reputation: 80 // Default reputation
        });
        totalIssuers++;

        emit IssuerAuthorized(issuer, name, institution);
    }

    function revokeIssuer(address issuer) public onlyOwner {
        require(authorizedIssuers[issuer], "Issuer not authorized");

        authorizedIssuers[issuer] = false;
        issuers[issuer].isActive = false;

        emit IssuerRevoked(issuer);
    }

    function updateIssuerReputation(address issuer, uint256 newReputation) public onlyOwner {
        require(authorizedIssuers[issuer], "Issuer not authorized");
        require(newReputation <= 100, "Reputation must be between 0-100");

        issuers[issuer].reputation = newReputation;
    }

    // Enhanced credential storage with metadata and expiration
    function storeCredential(
        string memory _title,
        string memory _studentId,
        string memory _studentName,
        string memory _ipfsHash,
        string memory _metadata,
        uint256 _expirationDate,
        uint8 _credentialType
    ) public onlyAuthorizedIssuer returns (bytes32) {
        require(_credentialType <= 3, "Invalid credential type");
        require(bytes(_studentId).length > 0, "Student ID cannot be empty");
        require(bytes(_ipfsHash).length > 0, "IPFS hash cannot be empty");

        bytes32 credentialId = keccak256(abi.encodePacked(
            _title,
            msg.sender,
            _studentId,
            _ipfsHash,
            block.timestamp
        ));

        require(credentials[credentialId].timestamp == 0, "Credential already exists");

        credentials[credentialId] = Credential({
            title: _title,
            issuer: issuers[msg.sender].name,
            studentId: _studentId,
            studentName: _studentName,
            ipfsHash: _ipfsHash,
            metadata: _metadata,
            timestamp: block.timestamp,
            expirationDate: _expirationDate,
            isValid: true,
            credentialType: _credentialType
        });

        // Track credentials per student
        studentCredentials[_studentId].push(credentialId);

        // Update issuer stats
        issuers[msg.sender].totalCredentials++;

        totalCredentials++;

        emit CredentialStored(credentialId, _title, issuers[msg.sender].name, _studentId, _ipfsHash);
        return credentialId;
    }

    // Batch credential storage for efficiency
    function storeCredentialsBatch(
        string[] memory _titles,
        string[] memory _studentIds,
        string[] memory _studentNames,
        string[] memory _ipfsHashes,
        string[] memory _metadata,
        uint256[] memory _expirationDates,
        uint8[] memory _credentialTypes
    ) public onlyAuthorizedIssuer returns (bytes32[] memory) {
        require(
            _titles.length == _studentIds.length &&
            _studentIds.length == _studentNames.length &&
            _studentNames.length == _ipfsHashes.length &&
            _ipfsHashes.length == _metadata.length &&
            _metadata.length == _expirationDates.length &&
            _expirationDates.length == _credentialTypes.length,
            "All arrays must have the same length"
        );

        uint256 count = _titles.length;
        bytes32[] memory credentialIds = new bytes32[](count);

        for (uint256 i = 0; i < count; i++) {
            credentialIds[i] = storeCredential(
                _titles[i],
                _studentIds[i],
                _studentNames[i],
                _ipfsHashes[i],
                _metadata[i],
                _expirationDates[i],
                _credentialTypes[i]
            );
        }

        emit BatchCredentialsStored(credentialIds, count);
        return credentialIds;
    }

    // Enhanced credential revocation with reason
    function revokeCredential(bytes32 credentialId, string memory reason) public onlyAuthorizedIssuer {
        require(credentials[credentialId].timestamp != 0, "Credential does not exist");
        require(credentials[credentialId].isValid, "Credential already revoked");

        credentials[credentialId].isValid = false;
        revokedCredentials[credentialId] = true;

        emit CredentialRevoked(credentialId, reason);
    }

    // Batch credential revocation
    function revokeCredentialsBatch(bytes32[] memory credentialIds, string memory reason) public onlyAuthorizedIssuer {
        for (uint256 i = 0; i < credentialIds.length; i++) {
            if (credentials[credentialIds[i]].timestamp != 0 && credentials[credentialIds[i]].isValid) {
                revokeCredential(credentialIds[i], reason);
            }
        }
    }

    // Check if credential is expired
    function isExpired(bytes32 credentialId) public view returns (bool) {
        if (credentials[credentialId].expirationDate == 0) {
            return false;
        }
        return block.timestamp > credentials[credentialId].expirationDate;
    }

    // Enhanced verification with expiration check
    function verifyCredential(bytes32 credentialId) public validCredential(credentialId) returns (
        string memory title,
        string memory issuer,
        string memory studentId,
        string memory studentName,
        string memory ipfsHash,
        string memory metadata,
        uint256 timestamp,
        uint256 expirationDate,
        bool isValid,
        uint8 credentialType
    ) {
        emit CredentialVerified(credentialId, msg.sender);

        Credential memory cred = credentials[credentialId];
        return (
            cred.title,
            cred.issuer,
            cred.studentId,
            cred.studentName,
            cred.ipfsHash,
            cred.metadata,
            cred.timestamp,
            cred.expirationDate,
            cred.isValid,
            cred.credentialType
        );
    }

    // Get credential details
    function getCredential(bytes32 credentialId) public view returns (Credential memory) {
        return credentials[credentialId];
    }

    // Check if credential is valid (includes expiration check)
    function isCredentialValid(bytes32 credentialId) public view returns (bool) {
        if (credentials[credentialId].timestamp == 0) {
            return false;
        }
        if (!credentials[credentialId].isValid) {
            return false;
        }
        if (credentials[credentialId].expirationDate != 0 && block.timestamp > credentials[credentialId].expirationDate) {
            return false;
        }
        return true;
    }

    // Get all credentials for a student
    function getStudentCredentials(string memory studentId) public view returns (bytes32[] memory) {
        return studentCredentials[studentId];
    }

    // Get valid credentials for a student
    function getValidStudentCredentials(string memory studentId) public view returns (bytes32[] memory) {
        bytes32[] memory allCredentials = studentCredentials[studentId];
        uint256 validCount = 0;

        // Count valid credentials
        for (uint256 i = 0; i < allCredentials.length; i++) {
            if (isCredentialValid(allCredentials[i])) {
                validCount++;
            }
        }

        // Create array of valid credentials
        bytes32[] memory validCredentials = new bytes32[](validCount);
        uint256 index = 0;

        for (uint256 i = 0; i < allCredentials.length; i++) {
            if (isCredentialValid(allCredentials[i])) {
                validCredentials[index] = allCredentials[i];
                index++;
            }
        }

        return validCredentials;
    }

    // Get issuer information
    function getIssuer(address issuerAddress) public view returns (Issuer memory) {
        return issuers[issuerAddress];
    }

    // Get contract statistics
    function getStats() public view returns (
        uint256 _totalCredentials,
        uint256 _totalIssuers,
        uint256 _activeIssuers
    ) {
        uint256 activeIssuers = 0;
        for (uint256 i = 0; i < totalIssuers; i++) {
            // Note: This is a simplified count - in production you'd track active issuers differently
            activeIssuers++;
        }

        return (totalCredentials, totalIssuers, activeIssuers);
    }

    // Emergency pause functionality
    bool public paused = false;

    modifier whenNotPaused() {
        require(!paused, "Contract is paused");
        _;
    }

    function pause() public onlyOwner {
        paused = true;
    }

    function unpause() public onlyOwner {
        paused = false;
    }

    // Update credential functions to respect pause
    function storeCredentialWithPause(
        string memory _title,
        string memory _studentId,
        string memory _studentName,
        string memory _ipfsHash,
        string memory _metadata,
        uint256 _expirationDate,
        uint8 _credentialType
    ) public onlyAuthorizedIssuer whenNotPaused returns (bytes32) {
        require(_credentialType <= 3, "Invalid credential type");
        require(bytes(_studentId).length > 0, "Student ID cannot be empty");
        require(bytes(_ipfsHash).length > 0, "IPFS hash cannot be empty");

        bytes32 credentialId = keccak256(abi.encodePacked(
            _title,
            msg.sender,
            _studentId,
            _ipfsHash,
            block.timestamp
        ));

        require(credentials[credentialId].timestamp == 0, "Credential already exists");

        credentials[credentialId] = Credential({
            title: _title,
            issuer: issuers[msg.sender].name,
            studentId: _studentId,
            studentName: _studentName,
            ipfsHash: _ipfsHash,
            metadata: _metadata,
            timestamp: block.timestamp,
            expirationDate: _expirationDate,
            isValid: true,
            credentialType: _credentialType
        });

        // Track credentials per student
        studentCredentials[_studentId].push(credentialId);

        // Update issuer stats
        issuers[msg.sender].totalCredentials++;

        totalCredentials++;

        emit CredentialStored(credentialId, _title, issuers[msg.sender].name, _studentId, _ipfsHash);
        return credentialId;
    }
}
}