"""
Web3 error handling utilities for TrueCred.

This module provides comprehensive error handling for Web3 operations,
including transaction failures, gas estimation, and network issues.
"""
import logging
from typing import Dict, Any, Optional, Tuple
from web3.exceptions import ContractLogicError, BadFunctionCallOutput, ValidationError as Web3ValidationError
from eth_account import Account
from web3 import Web3

logger = logging.getLogger(__name__)

class Web3ErrorHandler:
    """Handles Web3-related errors and provides user-friendly messages."""

    @staticmethod
    def handle_transaction_error(error: Exception, operation: str = "transaction") -> Dict[str, Any]:
        """
        Handle transaction-related errors and return user-friendly error information.

        Args:
            error: The exception that occurred
            operation: Description of the operation being performed

        Returns:
            Dictionary with error details
        """
        error_info = {
            'success': False,
            'error_type': type(error).__name__,
            'user_message': 'An unexpected error occurred during the transaction.',
            'technical_details': str(error),
            'retryable': False,
            'suggested_action': 'Please try again later or contact support.'
        }

        if isinstance(error, ContractLogicError):
            error_info.update({
                'user_message': 'Transaction failed due to contract logic error.',
                'technical_details': f'Contract error: {str(error)}',
                'retryable': False,
                'suggested_action': 'Check the transaction parameters and try again.'
            })

        elif isinstance(error, Web3ValidationError):
            error_info.update({
                'user_message': 'Transaction validation failed.',
                'technical_details': f'Validation error: {str(error)}',
                'retryable': False,
                'suggested_action': 'Check the transaction data and ensure all parameters are correct.'
            })

        elif isinstance(error, BadFunctionCallOutput):
            error_info.update({
                'user_message': 'Failed to call smart contract function.',
                'technical_details': f'Function call error: {str(error)}',
                'retryable': True,
                'suggested_action': 'Try again in a few moments. The network might be congested.'
            })

        elif 'insufficient funds' in str(error).lower():
            error_info.update({
                'user_message': 'Insufficient funds for transaction.',
                'technical_details': 'Account does not have enough funds to cover gas fees.',
                'retryable': False,
                'suggested_action': 'Add funds to your wallet and try again.'
            })

        elif 'nonce too low' in str(error).lower():
            error_info.update({
                'user_message': 'Transaction nonce error.',
                'technical_details': 'Transaction nonce is too low.',
                'retryable': True,
                'suggested_action': 'Wait a moment and try again. The nonce will be updated automatically.'
            })

        elif 'replacement transaction underpriced' in str(error).lower():
            error_info.update({
                'user_message': 'Transaction gas price too low.',
                'technical_details': 'Gas price is too low to replace pending transaction.',
                'retryable': True,
                'suggested_action': 'Increase gas price or wait for pending transaction to complete.'
            })

        elif 'gas required exceeds allowance' in str(error).lower():
            error_info.update({
                'user_message': 'Transaction gas limit exceeded.',
                'technical_details': 'Gas required for transaction exceeds the block gas limit.',
                'retryable': False,
                'suggested_action': 'Break the transaction into smaller operations or contact support.'
            })

        logger.error(f"Web3 {operation} error: {error_info['technical_details']}")

        return error_info

    @staticmethod
    def handle_contract_call_error(error: Exception, operation: str = "contract call") -> Dict[str, Any]:
        """
        Handle contract call-related errors and return user-friendly error information.

        Args:
            error: The exception that occurred
            operation: Description of the operation being performed

        Returns:
            Dictionary with error details
        """
        error_info = {
            'success': False,
            'error_type': type(error).__name__,
            'user_message': 'An error occurred while calling the smart contract.',
            'technical_details': str(error),
            'retryable': True,
            'suggested_action': 'Please try again or check your connection.'
        }

        if isinstance(error, BadFunctionCallOutput):
            error_info.update({
                'user_message': 'Contract function call failed.',
                'technical_details': f'Bad function call output: {str(error)}',
                'retryable': True,
                'suggested_action': 'Check the function parameters and try again.'
            })

        elif isinstance(error, ContractLogicError):
            error_info.update({
                'user_message': 'Contract logic error occurred.',
                'technical_details': f'Contract logic error: {str(error)}',
                'retryable': False,
                'suggested_action': 'The operation may not be allowed or the contract state is invalid.'
            })

        elif 'execution reverted' in str(error).lower():
            error_info.update({
                'user_message': 'Transaction execution was reverted by the contract.',
                'technical_details': f'Execution reverted: {str(error)}',
                'retryable': False,
                'suggested_action': 'Check the contract conditions and try again.'
            })

        elif 'network' in str(error).lower() or 'connection' in str(error).lower():
            error_info.update({
                'user_message': 'Network connection error.',
                'technical_details': f'Network error: {str(error)}',
                'retryable': True,
                'suggested_action': 'Check your internet connection and try again.'
            })

        logger.error(f"Web3 {operation} error: {error_info['technical_details']}")

        return error_info

    @staticmethod
    def estimate_gas_with_fallback(
        web3: Web3,
        tx_data: Dict[str, Any],
        fallback_gas: int = 200000
    ) -> int:
        """
        Estimate gas for a transaction with fallback.

        Args:
            web3: Web3 instance
            tx_data: Transaction data
            fallback_gas: Fallback gas limit if estimation fails

        Returns:
            Estimated gas limit
        """
        try:
            estimated_gas = web3.eth.estimate_gas(tx_data)
            # Add 20% buffer for safety
            buffered_gas = int(estimated_gas * 1.2)
            logger.info(f"Estimated gas: {estimated_gas}, buffered: {buffered_gas}")
            return buffered_gas
        except Exception as e:
            logger.warning(f"Gas estimation failed: {str(e)}, using fallback: {fallback_gas}")
            return fallback_gas

    @staticmethod
    def get_optimal_gas_price(web3: Web3) -> int:
        """
        Get optimal gas price based on network conditions.

        Args:
            web3: Web3 instance

        Returns:
            Optimal gas price in wei
        """
        try:
            # Get current gas price
            gas_price = web3.eth.gas_price

            # For fast networks, use current price
            # For congested networks, increase by 10-20%
            # This is a simple implementation - in production, you might want to use more sophisticated logic

            # Check if we're on a testnet (lower gas prices)
            if web3.eth.chain_id in [5, 11155111]:  # Goerli, Sepolia
                return gas_price

            # For mainnet, add a small buffer
            buffered_price = int(gas_price * 1.1)
            logger.info(f"Current gas price: {gas_price}, optimal: {buffered_price}")
            return buffered_price

        except Exception as e:
            logger.error(f"Failed to get optimal gas price: {str(e)}")
            return 20000000000  # 20 gwei fallback

    @staticmethod
    def validate_transaction_data(tx_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate transaction data before sending.

        Args:
            tx_data: Transaction data to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['from', 'to', 'value', 'gas', 'gasPrice', 'nonce', 'chainId']

        for field in required_fields:
            if field not in tx_data:
                return False, f"Missing required field: {field}"

        # Validate addresses
        if not Web3.is_address(tx_data['from']):
            return False, "Invalid 'from' address"

        if tx_data.get('to') and not Web3.is_address(tx_data['to']):
            return False, "Invalid 'to' address"

        # Validate gas limits
        if tx_data['gas'] < 21000:  # Minimum gas for a simple transfer
            return False, "Gas limit too low"

        if tx_data['gas'] > 8000000:  # Reasonable upper limit
            return False, "Gas limit too high"

        return True, ""

    @staticmethod
    def handle_network_error(error: Exception) -> Dict[str, Any]:
        """
        Handle network-related errors.

        Args:
            error: The network exception

        Returns:
            Dictionary with error details
        """
        error_info = {
            'success': False,
            'error_type': 'NetworkError',
            'user_message': 'Network connection error.',
            'technical_details': str(error),
            'retryable': True,
            'suggested_action': 'Check your internet connection and try again.'
        }

        if 'connection refused' in str(error).lower():
            error_info.update({
                'user_message': 'Cannot connect to blockchain network.',
                'suggested_action': 'Check network configuration and try again.'
            })

        elif 'timeout' in str(error).lower():
            error_info.update({
                'user_message': 'Network request timed out.',
                'suggested_action': 'The network might be congested. Try again in a few moments.'
            })

        return error_info

    @staticmethod
    def create_retry_transaction(
        original_tx: Dict[str, Any],
        web3: Web3,
        account: Account
    ) -> Dict[str, Any]:
        """
        Create a retry transaction with updated nonce and gas price.

        Args:
            original_tx: Original transaction data
            web3: Web3 instance
            account: Account instance

        Returns:
            Updated transaction data
        """
        try:
            # Get updated nonce
            current_nonce = web3.eth.get_transaction_count(account.address)

            # Get updated gas price
            gas_price = Web3ErrorHandler.get_optimal_gas_price(web3)

            # Create new transaction with updated values
            retry_tx = original_tx.copy()
            retry_tx.update({
                'nonce': current_nonce,
                'gasPrice': gas_price
            })

            logger.info(f"Created retry transaction with nonce: {current_nonce}, gas price: {gas_price}")

            return retry_tx

        except Exception as e:
            logger.error(f"Failed to create retry transaction: {str(e)}")
            return original_tx

class Web3TransactionManager:
    """Manages Web3 transactions with error handling and retries."""

    def __init__(self, web3: Web3, max_retries: int = 3):
        self.web3 = web3
        self.max_retries = max_retries
        self.error_handler = Web3ErrorHandler()

    def send_transaction_with_retry(
        self,
        tx_data: Dict[str, Any],
        private_key: str,
        operation: str = "transaction"
    ) -> Dict[str, Any]:
        """
        Send a transaction with automatic retry on failure.

        Args:
            tx_data: Transaction data
            private_key: Private key for signing
            operation: Description of the operation

        Returns:
            Dictionary with transaction result
        """
        account = Account.from_key(private_key)
        last_error = None

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempting {operation} (attempt {attempt + 1}/{self.max_retries})")

                # Validate transaction data
                is_valid, validation_error = self.error_handler.validate_transaction_data(tx_data)
                if not is_valid:
                    return {
                        'success': False,
                        'error': validation_error,
                        'attempts': attempt + 1
                    }

                # Estimate gas if not provided
                if 'gas' not in tx_data:
                    tx_data['gas'] = self.error_handler.estimate_gas_with_fallback(self.web3, tx_data)

                # Set gas price if not provided
                if 'gasPrice' not in tx_data:
                    tx_data['gasPrice'] = self.error_handler.get_optimal_gas_price(self.web3)

                # Set nonce if not provided
                if 'nonce' not in tx_data:
                    tx_data['nonce'] = self.web3.eth.get_transaction_count(account.address)

                # Set chain ID if not provided
                if 'chainId' not in tx_data:
                    tx_data['chainId'] = self.web3.eth.chain_id

                # Sign transaction
                signed_tx = self.web3.eth.account.sign_transaction(tx_data, private_key)

                # Send transaction
                tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)

                # Wait for transaction receipt
                receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

                if receipt.status == 1:
                    logger.info(f"{operation} successful: {tx_hash.hex()}")
                    return {
                        'success': True,
                        'transaction_hash': tx_hash.hex(),
                        'receipt': receipt,
                        'attempts': attempt + 1
                    }
                else:
                    error_msg = f"Transaction failed with status: {receipt.status}"
                    logger.error(error_msg)
                    last_error = Exception(error_msg)

            except Exception as e:
                last_error = e
                error_info = self.error_handler.handle_transaction_error(e, operation)

                if not error_info['retryable'] or attempt == self.max_retries - 1:
                    logger.error(f"{operation} failed after {attempt + 1} attempts: {error_info['technical_details']}")
                    return {
                        'success': False,
                        'error': error_info['user_message'],
                        'technical_details': error_info['technical_details'],
                        'suggested_action': error_info['suggested_action'],
                        'attempts': attempt + 1
                    }

                # Create retry transaction for next attempt
                tx_data = self.error_handler.create_retry_transaction(tx_data, self.web3, account)

                logger.warning(f"{operation} attempt {attempt + 1} failed, retrying: {error_info['user_message']}")

        # All retries exhausted
        return {
            'success': False,
            'error': 'Transaction failed after all retry attempts',
            'technical_details': str(last_error) if last_error else 'Unknown error',
            'attempts': self.max_retries
        }