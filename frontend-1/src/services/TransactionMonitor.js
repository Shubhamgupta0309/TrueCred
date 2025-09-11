/**
 * Transaction Monitor Service
 * 
 * This service is responsible for monitoring blockchain transactions
 * and updating the UI when they complete.
 */
import blockchainService from './BlockchainService';

class TransactionMonitor {
  constructor() {
    this.transactions = new Map();
    this.pollingInterval = null;
    this.pollingTime = 5000; // 5 seconds
  }

  /**
   * Start monitoring a transaction
   * @param {string} txHash - Transaction hash
   * @param {Function} onComplete - Callback function when transaction completes
   * @param {Function} onError - Callback function if transaction fails
   * @returns {string} Transaction ID
   */
  monitorTransaction(txHash, onComplete, onError) {
    const id = this._generateId();
    
    this.transactions.set(id, {
      txHash,
      status: 'pending',
      onComplete,
      onError,
      startTime: Date.now()
    });
    
    // Start polling if not already started
    this._startPolling();
    
    return id;
  }

  /**
   * Stop monitoring a specific transaction
   * @param {string} id - Transaction ID
   */
  stopMonitoring(id) {
    if (this.transactions.has(id)) {
      this.transactions.delete(id);
      
      // Stop polling if no transactions left
      if (this.transactions.size === 0) {
        this._stopPolling();
      }
    }
  }

  /**
   * Check if a transaction is being monitored
   * @param {string} txHash - Transaction hash
   * @returns {boolean} Whether the transaction is monitored
   */
  isTransactionMonitored(txHash) {
    for (const tx of this.transactions.values()) {
      if (tx.txHash === txHash) {
        return true;
      }
    }
    return false;
  }

  /**
   * Get the status of a transaction
   * @param {string} txHash - Transaction hash
   * @returns {string|null} Transaction status or null if not found
   */
  getTransactionStatus(txHash) {
    for (const tx of this.transactions.values()) {
      if (tx.txHash === txHash) {
        return tx.status;
      }
    }
    return null;
  }

  /**
   * Generate a unique ID for tracking transactions
   * @private
   * @returns {string} Unique ID
   */
  _generateId() {
    return `tx_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Start polling for transaction updates
   * @private
   */
  _startPolling() {
    if (!this.pollingInterval) {
      this.pollingInterval = setInterval(() => {
        this._checkTransactions();
      }, this.pollingTime);
    }
  }

  /**
   * Stop polling for transaction updates
   * @private
   */
  _stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }

  /**
   * Check the status of all transactions
   * @private
   */
  async _checkTransactions() {
    const now = Date.now();
    const txToRemove = [];
    
    for (const [id, tx] of this.transactions.entries()) {
      try {
        // Check transaction status
        const status = await blockchainService.getTransactionStatus(tx.txHash);
        
        if (status.confirmed) {
          // Transaction confirmed
          tx.status = 'confirmed';
          if (tx.onComplete) {
            tx.onComplete(status);
          }
          txToRemove.push(id);
        } else if (status.failed) {
          // Transaction failed
          tx.status = 'failed';
          if (tx.onError) {
            tx.onError(status);
          }
          txToRemove.push(id);
        } else if (now - tx.startTime > 10 * 60 * 1000) {
          // Timeout after 10 minutes
          tx.status = 'timeout';
          if (tx.onError) {
            tx.onError({ error: 'Transaction timed out' });
          }
          txToRemove.push(id);
        }
      } catch (err) {
        console.error('Error checking transaction status:', err);
        // Don't remove the transaction on error, will try again
      }
    }
    
    // Remove completed transactions
    for (const id of txToRemove) {
      this.transactions.delete(id);
    }
    
    // Stop polling if no transactions left
    if (this.transactions.size === 0) {
      this._stopPolling();
    }
  }
}

// Export a singleton instance
const transactionMonitor = new TransactionMonitor();
export default transactionMonitor;
