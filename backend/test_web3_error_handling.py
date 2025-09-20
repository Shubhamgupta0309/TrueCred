"""
Test file for Web3 service with enhanced error handling.
"""
import unittest
from unittest.mock import Mock, patch
from services.web3_service import Web3Service
from utils.web3_error_handler import Web3ErrorHandler, Web3TransactionManager


class TestWeb3Service(unittest.TestCase):
    """Test cases for Web3 service with error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.web3_service = Web3Service()

    @patch('services.web3_service.Web3')
    def test_store_credential_error_handling(self, mock_web3):
        """Test that store_credential_on_blockchain handles errors properly."""
        # Mock Web3 connection
        mock_web3_instance = Mock()
        mock_web3_instance.is_connected.return_value = True
        mock_web3_instance.eth.chain_id = 1
        mock_web3.return_value = mock_web3_instance

        # Mock contract instance to raise an exception
        with patch.object(self.web3_service, 'get_contract_instance') as mock_get_contract:
            mock_contract = Mock()
            mock_contract.functions.storeCredential.side_effect = Exception("Network error")
            mock_get_contract.return_value = mock_contract

            # Test error handling with a valid-looking private key (64 hex chars = 32 bytes)
            result = self.web3_service.store_credential_on_blockchain(
                title="Test Credential",
                student_id="12345",
                student_name="John Doe",
                ipfs_hash="QmTestHash",
                issuer_private_key="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
            )

            # Should return False and error message
            self.assertFalse(result[0])
            self.assertIn("error", result[2].lower())

    @patch('services.web3_service.Web3')
    def test_verify_credential_error_handling(self, mock_web3):
        """Test that verify_credential handles errors properly."""
        # Mock Web3 connection
        mock_web3_instance = Mock()
        mock_web3_instance.is_connected.return_value = True
        mock_web3.return_value = mock_web3_instance

        # Mock contract instance to raise an exception
        with patch.object(self.web3_service, 'get_contract_instance') as mock_get_contract:
            mock_contract = Mock()
            mock_contract.functions.verifyCredential.side_effect = Exception("Contract call failed")
            mock_get_contract.return_value = mock_contract

            # Test error handling
            result = self.web3_service.verify_credential("0x1234567890abcdef")

            # Should return error in result
            self.assertFalse(result['valid'])
            self.assertIn("error", result['error'].lower())

    def test_error_handler_integration(self):
        """Test that error handler classes are properly imported and accessible."""
        # Test that we can create error handler instances
        error_handler = Web3ErrorHandler()
        tx_manager = Web3TransactionManager(Mock())

        # Test that they have expected methods
        self.assertTrue(hasattr(error_handler, 'handle_transaction_error'))
        self.assertTrue(hasattr(error_handler, 'handle_contract_call_error'))
        self.assertTrue(hasattr(tx_manager, 'send_transaction_with_retry'))


if __name__ == '__main__':
    unittest.main()