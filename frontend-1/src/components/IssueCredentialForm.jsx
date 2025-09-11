import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import blockchainService from '../services/BlockchainService';
import transactionMonitor from '../services/TransactionMonitor';
import { api } from '../services/api';

const IssueCredentialForm = ({ onCredentialIssued, initialRecipient = {} }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    recipientEmail: initialRecipient.email || '',
    recipientWallet: initialRecipient.wallet || '',
    credentialType: 'diploma',
    issueDate: new Date().toISOString().split('T')[0],
    expiryDate: '',
    document: null
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [txHash, setTxHash] = useState(null);
  const [credentialId, setCredentialId] = useState(null);
  const [metadataUri, setMetadataUri] = useState('');
  const [blockchainStatus, setBlockchainStatus] = useState(null);

  // Update form data when initialRecipient changes
  useEffect(() => {
    if (initialRecipient.email || initialRecipient.wallet) {
      setFormData(prevData => ({
        ...prevData,
        recipientEmail: initialRecipient.email || prevData.recipientEmail,
        recipientWallet: initialRecipient.wallet || prevData.recipientWallet
      }));
    }
  }, [initialRecipient]);

  // Check blockchain status on component mount
  useEffect(() => {
  const checkBlockchainStatus = async () => {
      try {
        const status = await blockchainService.getStatus();
    const connected = Boolean(status?.web3_connected) && Boolean(status?.contract_loaded || status?.contract_address);
    setBlockchainStatus(status ? { connected, ...status } : { connected: false, error: 'No status returned' });
      } catch (err) {
        console.error('Failed to get blockchain status:', err);
        setBlockchainStatus({ connected: false, error: err.message || 'Unknown error' });
      }
    };

    checkBlockchainStatus();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    setFormData(prev => ({ ...prev, document: e.target.files[0] }));
  };

  // Function to upload file to IPFS and get back a metadata URI
  const uploadToIPFS = async (fileData) => {
    const formData = new FormData();
    formData.append('file', fileData);
    
    try {
      const response = await api.post('/ipfs/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      if (!response.data.success) {
        throw new Error(response.data.message || 'Failed to upload document to IPFS');
      }
      
      return response.data.ipfs_uri;
    } catch (err) {
      console.error('IPFS upload error:', err);
      throw new Error('Failed to upload document to IPFS: ' + err.message);
    }
  };

  // Function to prepare metadata JSON
  const createMetadata = async () => {
    let metadataUri = '';
    
    // Prepare metadata JSON
    const metadata = {
      title: formData.title,
      description: formData.description,
      issuer: user?.wallet_address || user?.id,
      issuanceDate: new Date(formData.issueDate).toISOString(),
      expiryDate: formData.expiryDate ? new Date(formData.expiryDate).toISOString() : null,
      credentialType: formData.credentialType,
      issuerName: user?.organization_name || user?.name || 'Mock Organization',
      timestamp: Date.now()
    };
    
    // Upload document and create metadata
    // If there's a document, upload it to IPFS first
    if (formData.document) {
      try {
        const documentUri = await uploadToIPFS(formData.document);
        metadata.documentUri = documentUri;
      } catch (err) {
        console.error('Document upload error:', err);
        throw err;
      }
    }
    
    // Upload metadata to IPFS
    try {
      const metadataBlob = new Blob([JSON.stringify(metadata)], { type: 'application/json' });
      const metadataFile = new File([metadataBlob], 'metadata.json', { type: 'application/json' });
      metadataUri = await uploadToIPFS(metadataFile);
    } catch (err) {
      console.error('Metadata upload error:', err);
      throw err;
    }
    
    return metadataUri;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);
    setTxHash(null);
    setCredentialId(null);

    try {
      // First, check if we have a recipient wallet address
      if (!formData.recipientWallet) {
        throw new Error('Recipient wallet address is required');
      }
      
      // Generate IPFS metadata URI
      let metadataUri;
      try {
        metadataUri = await createMetadata();
        setMetadataUri(metadataUri);
      } catch (err) {
        console.error('Metadata creation error:', err);
        // If in development mode, continue with a mock URI
        if (import.meta.env.DEV) {
          console.warn('Development mode: Using mock metadata URI');
          metadataUri = 'ipfs://mockuri/metadata.json';
          setMetadataUri(metadataUri);
        } else {
          throw err;
        }
      }
      
      // Calculate expiration timestamp (0 means no expiration)
      const expirationTimestamp = formData.expiryDate 
        ? Math.floor(new Date(formData.expiryDate).getTime() / 1000) 
        : 0;
      
      // Issue credential on blockchain
      try {
        const issueResult = await blockchainService.issueCredential({
          subject: formData.recipientWallet,
          credential_type: formData.credentialType,
          metadata_uri: metadataUri,
          expiration_date: expirationTimestamp
        });
        
        setTxHash(issueResult.transaction_hash);
        setCredentialId(issueResult.credential_id);
        
        // Monitor the transaction for completion
        if (issueResult.transaction_hash) {
          transactionMonitor.monitorTransaction(
            issueResult.transaction_hash,
            (status) => {
              console.log('Transaction confirmed:', status);
              // You could update UI or show a confirmation message here
            },
            (error) => {
              console.error('Transaction failed:', error);
              setError(`Transaction failed: ${error.error || 'Unknown error'}`);
            }
          );
        }
      } catch (err) {
        console.error('Blockchain error:', err);
        throw new Error(err.message || 'Failed to issue credential on blockchain');
      }

      setSuccess(true);
      if (onCredentialIssued) {
        onCredentialIssued({
          id: credentialId,
          title: formData.title,
          description: formData.description,
          recipient: formData.recipientEmail,
          recipientWallet: formData.recipientWallet,
          credentialType: formData.credentialType,
          issueDate: formData.issueDate,
          expiryDate: formData.expiryDate,
          metadataUri
        });
      }

      // Reset form
      setFormData({
        title: '',
        description: '',
        recipientEmail: '',
        recipientWallet: '',
        credentialType: 'diploma',
        issueDate: new Date().toISOString().split('T')[0],
        expiryDate: '',
        document: null
      });

      // Reset file input
      const fileInput = document.getElementById('document-upload');
      if (fileInput) {
        fileInput.value = '';
      }

    } catch (err) {
      setError(err.message || 'An error occurred while issuing the credential');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white shadow-md rounded-lg p-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-purple-700">Issue New Credential</h2>
      
  {blockchainStatus && blockchainStatus.connected === false && (
        <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-6" role="alert">
          <p className="font-bold">Blockchain Connection Warning</p>
          <p>The blockchain service is currently unavailable. Credentials may not be stored on the blockchain at this time.</p>
          {blockchainStatus.error && <p className="text-sm mt-1">Error: {blockchainStatus.error}</p>}
        </div>
      )}
      
      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6" role="alert">
          <p>{error}</p>
        </div>
      )}
      
      {success && (
        <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-6" role="alert">
          <p className="font-bold">Credential Issued Successfully!</p>
          {credentialId && (
            <p className="text-sm mt-2">
              Credential ID: <span className="font-mono">{credentialId}</span>
            </p>
          )}
          {txHash && (
            <p className="text-sm mt-2">
              Transaction Hash: <span className="font-mono">{txHash}</span>
            </p>
          )}
          {metadataUri && (
            <p className="text-sm mt-2">
              Metadata URI: <span className="font-mono">{metadataUri}</span>
            </p>
          )}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="col-span-2">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="title">
              Credential Title *
            </label>
            <input
              type="text"
              id="title"
              name="title"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={formData.title}
              onChange={handleChange}
              required
              placeholder="e.g., Bachelor of Science in Computer Science"
            />
          </div>
          
          <div className="col-span-2">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="description">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={formData.description}
              onChange={handleChange}
              rows="3"
              placeholder="Provide details about this credential"
            ></textarea>
          </div>
          
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="recipientEmail">
              Recipient Email *
            </label>
            <input
              type="email"
              id="recipientEmail"
              name="recipientEmail"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={formData.recipientEmail}
              onChange={handleChange}
              required
              placeholder="student@example.com"
            />
          </div>
          
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="recipientWallet">
              Recipient Wallet Address *
            </label>
            <input
              type="text"
              id="recipientWallet"
              name="recipientWallet"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={formData.recipientWallet}
              onChange={handleChange}
              required
              placeholder="0x..."
            />
          </div>
          
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="credentialType">
              Credential Type *
            </label>
            <select
              id="credentialType"
              name="credentialType"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={formData.credentialType}
              onChange={handleChange}
              required
            >
              <option value="diploma">Diploma</option>
              <option value="degree">Degree</option>
              <option value="certificate">Certificate</option>
              <option value="badge">Badge</option>
              <option value="license">License</option>
              <option value="other">Other</option>
            </select>
          </div>
          
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="issueDate">
              Issue Date *
            </label>
            <input
              type="date"
              id="issueDate"
              name="issueDate"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={formData.issueDate}
              onChange={handleChange}
              required
            />
          </div>
          
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="expiryDate">
              Expiry Date (if applicable)
            </label>
            <input
              type="date"
              id="expiryDate"
              name="expiryDate"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={formData.expiryDate}
              onChange={handleChange}
              min={formData.issueDate}
            />
          </div>
          
          <div className="col-span-2">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="document-upload">
              Upload Document (PDF, JPG, PNG)
            </label>
            <input
              type="file"
              id="document-upload"
              name="document"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100"
              accept=".pdf,.jpg,.jpeg,.png"
            />
            <p className="text-xs text-gray-500 mt-1">Max file size: 10MB</p>
          </div>
        </div>
        
        <div className="mt-8">
          <button
            type="submit"
            className={`w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={loading}
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </>
            ) : (
              'Issue Credential'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default IssueCredentialForm;