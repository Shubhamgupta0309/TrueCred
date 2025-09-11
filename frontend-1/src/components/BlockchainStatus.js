import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Chip, Box, Button, CircularProgress, Divider, Link } from '@mui/material';
import { Check, Close, Warning } from '@mui/icons-material';

/**
 * BlockchainStatus component displays the current status of the blockchain connection
 * and contract deployment.
 */
const BlockchainStatus = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const RAW_API = import.meta.env.VITE_API_URL || 'http://localhost:5000';
      const API_URL = RAW_API.endsWith('/api') ? RAW_API : `${RAW_API}/api`;
      const response = await fetch(`${API_URL}/blockchain/status`);
      if (!response.ok) {
        throw new Error(`Failed to fetch blockchain status: ${response.statusText}`);
      }
      const data = await response.json();
      setStatus(data);
      setError(null);
    } catch (err) {
      console.error("Error fetching blockchain status:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    // Poll for status updates every 30 seconds
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !status) {
    return (
      <Card elevation={3}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="center" p={2}>
            <CircularProgress size={24} sx={{ mr: 2 }} />
            <Typography variant="body1">Loading blockchain status...</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error && !status) {
    return (
      <Card elevation={3}>
        <CardContent>
          <Box display="flex" alignItems="center" p={1}>
            <Close color="error" sx={{ mr: 1 }} />
            <Typography variant="body1" color="error">
              Error loading blockchain status: {error}
            </Typography>
          </Box>
          <Box mt={2}>
            <Button variant="outlined" onClick={fetchStatus}>
              Retry
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
  }

  const getNetworkColor = (network) => {
    switch (network) {
      case 'mainnet':
        return 'success';
      case 'goerli':
      case 'sepolia':
        return 'info';
      default:
        return 'warning';
    }
  };

  return (
    <Card elevation={3}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Blockchain Status
        </Typography>

        <Box mb={2}>
          <Chip
            icon={status?.web3_connected ? <Check /> : <Close />}
            label={status?.web3_connected ? "Connected" : "Disconnected"}
            color={status?.web3_connected ? "success" : "error"}
            variant="outlined"
          />
          {status?.network && (
            <Chip
              label={`Network: ${status.network}`}
              color={getNetworkColor(status.network)}
              variant="outlined"
              sx={{ ml: 1 }}
            />
          )}
        </Box>

        {status?.web3_connected && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" gutterBottom>
              Contract Information
            </Typography>
            <Box>
              <Typography variant="body2">
                <strong>Contract Address:</strong>{' '}
                {status.contract_address ? (
                  <Link 
                    href={`https://${status.network === 'mainnet' ? '' : status.network + '.'}etherscan.io/address/${status.contract_address}`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                  >
                    {status.contract_address}
                  </Link>
                ) : (
                  <Chip size="small" label="Not Deployed" color="warning" />
                )}
              </Typography>
              
              {status.deployment_info && (
                <>
                  <Typography variant="body2">
                    <strong>Deployment Transaction:</strong>{' '}
                    <Link 
                      href={`https://${status.network === 'mainnet' ? '' : status.network + '.'}etherscan.io/tx/${status.deployment_info.deploymentTransactionHash}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                    >
                      {status.deployment_info.deploymentTransactionHash.substring(0, 10)}...
                    </Link>
                  </Typography>
                  <Typography variant="body2">
                    <strong>Block Number:</strong> {status.deployment_info.blockNumber}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Deployment Date:</strong>{' '}
                    {new Date(status.deployment_info.timestamp * 1000).toLocaleString()}
                  </Typography>
                </>
              )}
            </Box>

            {status.has_account && (
              <>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" gutterBottom>
                  Account Information
                </Typography>
                <Box>
                  <Typography variant="body2">
                    <strong>Account Address:</strong>{' '}
                    <Link 
                      href={`https://${status.network === 'mainnet' ? '' : status.network + '.'}etherscan.io/address/${status.account_address}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                    >
                      {status.account_address}
                    </Link>
                  </Typography>
                  <Typography variant="body2">
                    <strong>Balance:</strong> {status.account_balance} ETH
                  </Typography>
                </Box>
              </>
            )}

            {status.block_number && (
              <Box mt={2}>
                <Typography variant="body2">
                  <strong>Current Block:</strong> {status.block_number}
                </Typography>
              </Box>
            )}
          </>
        )}

        <Box mt={2}>
          <Button 
            variant="outlined"
            size="small"
            onClick={fetchStatus}
            startIcon={loading ? <CircularProgress size={16} /> : null}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh Status'}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default BlockchainStatus;
