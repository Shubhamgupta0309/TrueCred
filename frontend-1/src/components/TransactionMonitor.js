import React, { useState, useEffect } from 'react';
import { Card, Badge, ListGroup, Button, Spinner, Modal } from 'react-bootstrap';
import { 
  FaCheckCircle, FaTimesCircle, FaSpinner, 
  FaInfoCircle, FaExternalLinkAlt, FaHistory 
} from 'react-icons/fa';
import BlockchainService from '../services/BlockchainService';

/**
 * TransactionMonitor component tracks and displays blockchain transaction status
 * for credential issuance, verification, and revocation operations.
 */
const TransactionMonitor = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTx, setSelectedTx] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    loadTransactions();
  }, []);

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const txList = await BlockchainService.getRecentTransactions();
      setTransactions(txList);
    } catch (error) {
      console.error('Failed to load transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const refreshTransactions = async () => {
    try {
      setRefreshing(true);
      const txList = await BlockchainService.getRecentTransactions();
      setTransactions(txList);
    } catch (error) {
      console.error('Failed to refresh transactions:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const viewTransactionDetails = (tx) => {
    setSelectedTx(tx);
    setShowModal(true);
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'confirmed':
        return <Badge bg="success"><FaCheckCircle className="me-1" /> Confirmed</Badge>;
      case 'pending':
        return <Badge bg="warning"><FaSpinner className="me-1 fa-spin" /> Pending</Badge>;
      case 'failed':
        return <Badge bg="danger"><FaTimesCircle className="me-1" /> Failed</Badge>;
      default:
        return <Badge bg="secondary"><FaInfoCircle className="me-1" /> Unknown</Badge>;
    }
  };

  const getTransactionTypeLabel = (type) => {
    switch (type) {
      case 'credential_issuance':
        return 'Credential Issuance';
      case 'experience_verification':
        return 'Experience Verification';
      case 'credential_revocation':
        return 'Credential Revocation';
      case 'experience_revocation':
        return 'Experience Revocation';
      default:
        return type ? type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Transaction';
    }
  };

  const getNetworkExplorerUrl = (txHash, network) => {
    if (!txHash) return null;
    
    const explorers = {
      'mainnet': `https://etherscan.io/tx/${txHash}`,
      'goerli': `https://goerli.etherscan.io/tx/${txHash}`,
      'sepolia': `https://sepolia.etherscan.io/tx/${txHash}`,
      'local': null
    };
    
    return explorers[network] || null;
  };

  const formatDate = (timestamp) => {
    if (!timestamp) return 'N/A';
    
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const shortenAddress = (address) => {
    if (!address) return 'N/A';
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
  };

  return (
    <>
      <Card className="shadow-sm mb-4">
        <Card.Header className="d-flex justify-content-between align-items-center">
          <div>
            <h5 className="mb-0">Transaction Monitor</h5>
          </div>
          <Button 
            variant="outline-primary" 
            size="sm" 
            onClick={refreshTransactions}
            disabled={refreshing}
          >
            {refreshing ? (
              <>
                <Spinner as="span" animation="border" size="sm" className="me-2" />
                Refreshing...
              </>
            ) : (
              <>
                <FaHistory className="me-1" /> Refresh
              </>
            )}
          </Button>
        </Card.Header>
        <Card.Body>
          {loading ? (
            <div className="text-center py-4">
              <Spinner animation="border" variant="primary" />
              <p className="mt-2">Loading transactions...</p>
            </div>
          ) : transactions.length === 0 ? (
            <div className="text-center py-4">
              <FaInfoCircle size={24} className="mb-3 text-muted" />
              <p className="mb-0">No transactions found</p>
              <p className="text-muted small">Transactions will appear here after you issue or verify credentials</p>
            </div>
          ) : (
            <ListGroup variant="flush">
              {transactions.map((tx, index) => (
                <ListGroup.Item 
                  key={index}
                  action
                  onClick={() => viewTransactionDetails(tx)}
                  className="d-flex justify-content-between align-items-center"
                >
                  <div>
                    <div className="d-flex align-items-center mb-1">
                      <span className="me-2 fw-bold">{getTransactionTypeLabel(tx.type)}</span>
                      {getStatusBadge(tx.status)}
                    </div>
                    <div className="small text-muted">
                      {tx.item_id && <div>ID: {shortenAddress(tx.item_id)}</div>}
                      <div>Timestamp: {formatDate(tx.timestamp)}</div>
                    </div>
                  </div>
                  <div>
                    <Button variant="link" size="sm" className="text-decoration-none">
                      <FaInfoCircle /> Details
                    </Button>
                  </div>
                </ListGroup.Item>
              ))}
            </ListGroup>
          )}
        </Card.Body>
      </Card>

      {/* Transaction Details Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Transaction Details</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedTx && (
            <div>
              <h6 className="mb-3">{getTransactionTypeLabel(selectedTx.type)}</h6>
              
              <div className="mb-3">
                <div className="fw-bold mb-1">Status</div>
                <div>{getStatusBadge(selectedTx.status)}</div>
              </div>
              
              <div className="row mb-3">
                <div className="col-md-6">
                  <div className="fw-bold mb-1">Transaction Hash</div>
                  <div className="text-break">
                    {selectedTx.transaction_hash || 'Not available'}
                    {selectedTx.transaction_hash && selectedTx.network && getNetworkExplorerUrl(selectedTx.transaction_hash, selectedTx.network) && (
                      <a 
                        href={getNetworkExplorerUrl(selectedTx.transaction_hash, selectedTx.network)} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="ms-2"
                      >
                        <FaExternalLinkAlt size={14} />
                      </a>
                    )}
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="fw-bold mb-1">Network</div>
                  <div>{selectedTx.network ? selectedTx.network.charAt(0).toUpperCase() + selectedTx.network.slice(1) : 'Unknown'}</div>
                </div>
              </div>
              
              <div className="row mb-3">
                <div className="col-md-6">
                  <div className="fw-bold mb-1">Block Number</div>
                  <div>{selectedTx.block_number || 'Pending'}</div>
                </div>
                <div className="col-md-6">
                  <div className="fw-bold mb-1">Timestamp</div>
                  <div>{formatDate(selectedTx.timestamp)}</div>
                </div>
              </div>
              
              <div className="row mb-3">
                <div className="col-md-6">
                  <div className="fw-bold mb-1">Gas Used</div>
                  <div>{selectedTx.gas_used || 'Not available'}</div>
                </div>
                <div className="col-md-6">
                  <div className="fw-bold mb-1">Item ID</div>
                  <div className="text-break">{selectedTx.item_id || 'Not available'}</div>
                </div>
              </div>
              
              {selectedTx.data_hash && (
                <div className="mb-3">
                  <div className="fw-bold mb-1">Data Hash</div>
                  <div className="text-break">{selectedTx.data_hash}</div>
                </div>
              )}
              
              {selectedTx.issuer_address && (
                <div className="mb-3">
                  <div className="fw-bold mb-1">Issuer Address</div>
                  <div className="text-break">{selectedTx.issuer_address}</div>
                </div>
              )}
              
              {selectedTx.error && (
                <div className="alert alert-danger mt-3">
                  <div className="fw-bold">Error</div>
                  <div>{selectedTx.error}</div>
                </div>
              )}
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          {selectedTx && selectedTx.transaction_hash && selectedTx.network && getNetworkExplorerUrl(selectedTx.transaction_hash, selectedTx.network) && (
            <Button 
              variant="outline-primary" 
              href={getNetworkExplorerUrl(selectedTx.transaction_hash, selectedTx.network)} 
              target="_blank"
              rel="noopener noreferrer"
            >
              <FaExternalLinkAlt className="me-2" />
              View on Etherscan
            </Button>
          )}
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default TransactionMonitor;
