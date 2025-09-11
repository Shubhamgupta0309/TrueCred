/**
 * BlockchainService provides functions to interact with the TrueCred blockchain API.
 */
class BlockchainService {
  constructor() {
    // Use import.meta.env for Vite projects instead of process.env
  const raw = import.meta.env.VITE_API_URL || 'http://localhost:5000';
  this.apiUrl = raw.endsWith('/api') ? raw : `${raw}/api`;
  }

  /**
   * Get the current blockchain connection status
   * @returns {Promise<Object>} The blockchain status
   */
  async getStatus() {
  const response = await fetch(`${this.apiUrl}/blockchain/status`);
    if (!response.ok) {
      throw new Error(`Failed to fetch blockchain status: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Issue a new credential on the blockchain
   * @param {Object} credential - The credential to issue
   * @param {string} credential.subject - Ethereum address of the subject
   * @param {string} credential.credential_type - Type of credential
   * @param {string} credential.metadata_uri - IPFS URI of the credential metadata
   * @param {number} credential.expiration_date - Optional expiration timestamp
   * @returns {Promise<Object>} Result of the transaction
   */
  async issueCredential(credential) {
  const response = await fetch(`${this.apiUrl}/blockchain/credentials/issue`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify(credential)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.details || `Failed to issue credential: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Issue multiple credentials in a batch
   * @param {Object} batch - The batch of credentials to issue
   * @param {Array<string>} batch.subjects - Array of subject addresses
   * @param {Array<string>} batch.credential_types - Array of credential types
   * @param {Array<string>} batch.metadata_uris - Array of metadata URIs
   * @param {Array<number>} batch.expiration_dates - Array of expiration dates
   * @returns {Promise<Object>} Result of the transaction
   */
  async batchIssueCredentials(batch) {
  const response = await fetch(`${this.apiUrl}/blockchain/credentials/batch-issue`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify(batch)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.details || `Failed to batch issue credentials: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Revoke a credential on the blockchain
   * @param {string} credentialId - ID of the credential to revoke
   * @returns {Promise<Object>} Result of the transaction
   */
  async revokeCredential(credentialId) {
  const response = await fetch(`${this.apiUrl}/blockchain/credentials/revoke`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify({ credential_id: credentialId })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.details || `Failed to revoke credential: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Verify a credential's validity on the blockchain
   * @param {string} credentialId - ID of the credential to verify
   * @returns {Promise<Object>} Verification result
   */
  async verifyCredential(credentialId) {
  const response = await fetch(`${this.apiUrl}/blockchain/credentials/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ credential_id: credentialId })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.details || `Failed to verify credential: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get detailed information about a credential
   * @param {string} credentialId - ID of the credential
   * @returns {Promise<Object>} Credential details
   */
  async getCredentialDetails(credentialId) {
  const response = await fetch(`${this.apiUrl}/blockchain/credentials/details`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ credential_id: credentialId })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.details || `Failed to get credential details: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get all credentials owned by a subject
   * @param {string} subjectAddress - Ethereum address of the subject
   * @returns {Promise<Object>} List of credential IDs
   */
  async getSubjectCredentials(subjectAddress) {
  const response = await fetch(`${this.apiUrl}/blockchain/credentials/subject/${subjectAddress}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.details || `Failed to get subject credentials: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get all credentials issued by an issuer
   * @param {string} issuerAddress - Ethereum address of the issuer
   * @returns {Promise<Object>} List of credential IDs
   */
  async getIssuerCredentials(issuerAddress) {
  const response = await fetch(`${this.apiUrl}/blockchain/credentials/issuer/${issuerAddress}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.details || `Failed to get issuer credentials: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Check if an address is an authorized issuer
   * @param {string} issuerAddress - Ethereum address to check
   * @returns {Promise<Object>} Whether the address is authorized
   */
  async isAuthorizedIssuer(issuerAddress) {
  const response = await fetch(`${this.apiUrl}/blockchain/issuers/check/${issuerAddress}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.details || `Failed to check issuer: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Authorize an address to issue credentials
   * @param {string} issuerAddress - Ethereum address to authorize
   * @returns {Promise<Object>} Result of the transaction
   */
  async authorizeIssuer(issuerAddress) {
  const response = await fetch(`${this.apiUrl}/blockchain/issuers/authorize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify({ issuer: issuerAddress })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.details || `Failed to authorize issuer: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Revoke an issuer's authorization
   * @param {string} issuerAddress - Ethereum address to revoke
   * @returns {Promise<Object>} Result of the transaction
   */
  async revokeIssuer(issuerAddress) {
  const response = await fetch(`${this.apiUrl}/blockchain/issuers/revoke`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify({ issuer: issuerAddress })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.details || `Failed to revoke issuer: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get the status of a transaction
   * @param {string} txHash - Transaction hash to check
   * @returns {Promise<Object>} Transaction status
   */
  async getTransactionStatus(txHash) {
  const response = await fetch(`${this.apiUrl}/blockchain/transaction/${txHash}`, {
      headers: {
        'Authorization': `Bearer ${this.getToken()}`
      }
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.details || `Failed to get transaction status: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Sign a message with the account's private key
   * @param {string} message - Message to sign
   * @returns {Promise<Object>} Signature information
   */
  async signMessage(message) {
  const response = await fetch(`${this.apiUrl}/blockchain/sign`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify({ message })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.details || `Failed to sign message: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Verify a signature
   * @param {string} message - Original message
   * @param {string} signature - Signature to verify
   * @param {string} address - Ethereum address of the signer
   * @returns {Promise<Object>} Whether the signature is valid
   */
  async verifySignature(message, signature, address) {
  const response = await fetch(`${this.apiUrl}/blockchain/verify-signature`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, signature, address })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.details || `Failed to verify signature: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get the authentication token from local storage
   * @returns {string|null} The token or null if not found
   */
  getToken() {
    return localStorage.getItem('accessToken');
  }
}

// Export a singleton instance
const blockchainService = new BlockchainService();
export default blockchainService;
