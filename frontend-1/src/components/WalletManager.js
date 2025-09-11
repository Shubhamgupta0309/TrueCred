import React, { useState, useEffect } from 'react';
import { Card, Button, Alert, Spinner, Form } from 'react-bootstrap';
import { FaWallet, FaEthereum, FaExclamationTriangle, FaCheck, FaSignOutAlt } from 'react-icons/fa';
import BlockchainService from '../services/BlockchainService';

/**
 * WalletManager component provides wallet connection and management functionality
 * for blockchain interactions.
 */
const WalletManager = () => {
  const [walletState, setWalletState] = useState({
    connected: false,
    connecting: false,
    address: null,
    network: null,
    networkSupported: false,
    balance: null,
    error: null
  });

  useEffect(() => {
    // Check if wallet is already connected
    checkWalletConnection();

    // Listen for account changes
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', handleAccountsChanged);
      window.ethereum.on('chainChanged', handleChainChanged);
    }

    return () => {
      // Clean up event listeners
      if (window.ethereum) {
        window.ethereum.removeListener('accountsChanged', handleAccountsChanged);
        window.ethereum.removeListener('chainChanged', handleChainChanged);
      }
    };
  }, []);

  const checkWalletConnection = async () => {
    try {
      if (!window.ethereum) return;
      
      const accounts = await window.ethereum.request({ method: 'eth_accounts' });
      if (accounts.length > 0) {
        const networkName = await BlockchainService.getNetworkName();
        const networkSupported = await BlockchainService.isNetworkSupported();
        const balance = await getAccountBalance(accounts[0]);
        
        setWalletState({
          connected: true,
          connecting: false,
          address: accounts[0],
          network: networkName,
          networkSupported,
          balance,
          error: null
        });
      }
    } catch (error) {
      console.error('Error checking wallet connection:', error);
    }
  };

  const connectWallet = async () => {
    try {
      setWalletState(prev => ({ ...prev, connecting: true, error: null }));
      
      if (!window.ethereum) {
        throw new Error('MetaMask is not installed. Please install it to connect your wallet.');
      }
      
      const address = await BlockchainService.connectWallet();
      const networkName = await BlockchainService.getNetworkName();
      const networkSupported = await BlockchainService.isNetworkSupported();
      const balance = await getAccountBalance(address);
      
      setWalletState({
        connected: true,
        connecting: false,
        address,
        network: networkName,
        networkSupported,
        balance,
        error: null
      });
    } catch (error) {
      setWalletState(prev => ({
        ...prev,
        connecting: false,
        error: error.message || 'Failed to connect wallet'
      }));
    }
  };

  const disconnectWallet = () => {
    setWalletState({
      connected: false,
      connecting: false,
      address: null,
      network: null,
      networkSupported: false,
      balance: null,
      error: null
    });
  };

  const handleAccountsChanged = async (accounts) => {
    if (accounts.length === 0) {
      // User disconnected wallet
      disconnectWallet();
    } else {
      // Account changed
      const networkName = await BlockchainService.getNetworkName();
      const networkSupported = await BlockchainService.isNetworkSupported();
      const balance = await getAccountBalance(accounts[0]);
      
      setWalletState(prev => ({
        ...prev,
        address: accounts[0],
        network: networkName,
        networkSupported,
        balance
      }));
    }
  };

  const handleChainChanged = async () => {
    // Reload the page when network changes
    window.location.reload();
  };

  const getAccountBalance = async (address) => {
    try {
      if (!window.ethereum) return null;
      
      const balance = await window.ethereum.request({
        method: 'eth_getBalance',
        params: [address, 'latest']
      });
      
      // Convert from wei to ether
      return parseFloat(parseInt(balance, 16) / 1e18).toFixed(4);
    } catch (error) {
      console.error('Error getting account balance:', error);
      return null;
    }
  };

  const shortenAddress = (address) => {
    if (!address) return '';
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
  };

  return (
    <Card className="shadow-sm mb-4">
      <Card.Header>
        <h5 className="mb-0">
          <FaWallet className="me-2" />
          Wallet Connection
        </h5>
      </Card.Header>
      <Card.Body>
        {walletState.error && (
          <Alert variant="danger" className="mb-3">
            <FaExclamationTriangle className="me-2" />
            {walletState.error}
          </Alert>
        )}
        
        {walletState.connected ? (
          <div>
            <div className="mb-3">
              <Form.Group>
                <Form.Label>Connected Address</Form.Label>
                <div className="d-flex">
                  <Form.Control
                    type="text"
                    value={walletState.address}
                    readOnly
                    className="bg-light"
                  />
                  <Button 
                    variant="outline-secondary" 
                    className="ms-2"
                    onClick={() => navigator.clipboard.writeText(walletState.address)}
                    title="Copy to clipboard"
                  >
                    Copy
                  </Button>
                </div>
              </Form.Group>
            </div>
            
            <div className="row mb-3">
              <div className="col-md-6">
                <Form.Group>
                  <Form.Label>Network</Form.Label>
                  <div className="d-flex align-items-center">
                    <FaEthereum className="me-2 text-primary" />
                    <span>{walletState.network}</span>
                    {walletState.networkSupported ? (
                      <FaCheck className="ms-2 text-success" title="Supported network" />
                    ) : (
                      <FaExclamationTriangle 
                        className="ms-2 text-warning" 
                        title="Unsupported network - please switch to Mainnet, Goerli, or Sepolia" 
                      />
                    )}
                  </div>
                </Form.Group>
              </div>
              <div className="col-md-6">
                <Form.Group>
                  <Form.Label>Balance</Form.Label>
                  <div>
                    {walletState.balance ? (
                      <span>{walletState.balance} ETH</span>
                    ) : (
                      <span className="text-muted">Loading...</span>
                    )}
                  </div>
                </Form.Group>
              </div>
            </div>
            
            {!walletState.networkSupported && (
              <Alert variant="warning" className="mb-3">
                <FaExclamationTriangle className="me-2" />
                You are connected to an unsupported network. Please switch to Mainnet, Goerli, or Sepolia.
              </Alert>
            )}
            
            <Button 
              variant="outline-danger" 
              onClick={disconnectWallet}
              className="mt-2"
            >
              <FaSignOutAlt className="me-2" />
              Disconnect Wallet
            </Button>
          </div>
        ) : (
          <div className="text-center py-4">
            {!window.ethereum ? (
              <div>
                <FaExclamationTriangle size={24} className="text-warning mb-3" />
                <p>MetaMask is not installed.</p>
                <Button 
                  variant="primary" 
                  href="https://metamask.io/download.html" 
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Install MetaMask
                </Button>
              </div>
            ) : (
              <div>
                <FaWallet size={24} className="text-primary mb-3" />
                <p>Connect your wallet to use blockchain features</p>
                <Button 
                  variant="primary"
                  onClick={connectWallet}
                  disabled={walletState.connecting}
                >
                  {walletState.connecting ? (
                    <>
                      <Spinner as="span" animation="border" size="sm" className="me-2" />
                      Connecting...
                    </>
                  ) : (
                    <>
                      <FaEthereum className="me-2" />
                      Connect MetaMask
                    </>
                  )}
                </Button>
              </div>
            )}
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

export default WalletManager;
