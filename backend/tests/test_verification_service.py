"""
Unit tests for verification service.

Tests the blockchain and IPFS integration for verifying credentials and experiences.
"""
import unittest
from unittest import mock
from datetime import datetime

from services.verification_service import VerificationService
from models.credential import Credential
from models.experience import Experience
from models.user import User


class VerificationServiceTests(unittest.TestCase):
    """Test cases for the verification service."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock objects
        self.mock_blockchain_service = mock.Mock()
        self.mock_ipfs_service = mock.Mock()
        
        # Create verification service with mocked dependencies
        self.verification_service = VerificationService()
        self.verification_service.blockchain_service = self.mock_blockchain_service
        self.verification_service.ipfs_service = self.mock_ipfs_service
        
    def test_string_to_bytes32(self):
        """Test conversion of string to bytes32."""
        # Test with a regular string
        test_id = "abc123"
        bytes32 = self.verification_service._string_to_bytes32(test_id)
        self.assertTrue(bytes32.startswith('0x'))
        self.assertEqual(len(bytes32), 66)  # 0x + 64 hex chars
        
        # Test with an already formatted bytes32
        existing_bytes32 = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        converted = self.verification_service._string_to_bytes32(existing_bytes32)
        self.assertEqual(converted, existing_bytes32)
    
    def test_calculate_verification_score(self):
        """Test calculation of verification score."""
        # Test with no credentials or experiences
        score = self.verification_service._calculate_verification_score(0, 0, 0, 0)
        self.assertEqual(score, 0.0)
        
        # Test with only credentials
        score = self.verification_service._calculate_verification_score(5, 10, 0, 0)
        self.assertEqual(score, 50.0)
        
        # Test with only experiences
        score = self.verification_service._calculate_verification_score(0, 0, 8, 10)
        self.assertEqual(score, 80.0)
        
        # Test with both
        score = self.verification_service._calculate_verification_score(5, 10, 8, 10)
        self.assertEqual(score, 62.0)  # 50*0.6 + 80*0.4
    
    @mock.patch('services.verification_service.Credential')
    def test_verify_credential_blockchain(self, mock_credential_model):
        """Test credential verification using blockchain."""
        # Set up mocks
        mock_credential = mock.Mock()
        mock_credential.id = "cred123"
        mock_credential.title = "Test Credential"
        mock_credential.issuer = "Test Issuer"
        mock_credential.blockchain_hash = "0xabcdef"
        mock_credential.ipfs_hash = None
        
        # Configure model mock to return our mock credential
        mock_credential_model.objects.get.return_value = mock_credential
        
        # Configure blockchain service mock to verify the credential
        self.mock_blockchain_service.verify_credential_hash.return_value = True
        
        # Perform verification
        result = self.verification_service.verify_credential("cred123")
        
        # Check results
        self.assertTrue(result['verified'])
        self.assertEqual(result['credential_id'], "cred123")
        self.assertTrue(result['blockchain_verification']['verified'])
        self.assertFalse(result['ipfs_verification']['verified'])
        self.assertEqual(result['verification_methods'], ['blockchain'])
        
        # Verify model was updated
        mock_credential.save.assert_called_once()
        self.assertTrue(mock_credential.verified)
    
    @mock.patch('services.verification_service.Experience')
    def test_verify_experience_ipfs(self, mock_experience_model):
        """Test experience verification using IPFS."""
        # Set up mocks
        mock_experience = mock.Mock()
        mock_experience.id = "exp123"
        mock_experience.title = "Test Experience"
        mock_experience.organization = "Test Organization"
        mock_experience.blockchain_hash = None
        mock_experience.ipfs_hash = "QmTest"
        mock_experience.ipfs_metadata_hash = "QmTestMeta"
        
        # Configure model mock to return our mock experience
        mock_experience_model.objects.get.return_value = mock_experience
        
        # Configure IPFS service mock to verify the experience
        self.mock_ipfs_service.get_file.return_value = b"test data"
        self.mock_ipfs_service.get_json.return_value = {"test": "metadata"}
        self.mock_ipfs_service.get_gateway_url.return_value = "http://ipfs.example.com/QmTest"
        
        # Perform verification
        result = self.verification_service.verify_experience("exp123")
        
        # Check results
        self.assertTrue(result['verified'])
        self.assertEqual(result['experience_id'], "exp123")
        self.assertFalse(result['blockchain_verification']['verified'])
        self.assertTrue(result['ipfs_verification']['verified'])
        self.assertEqual(result['verification_methods'], ['ipfs'])
        
        # Verify model was updated
        mock_experience.save.assert_called_once()
        self.assertTrue(mock_experience.is_verified)
    
    @mock.patch('services.verification_service.User')
    @mock.patch('services.verification_service.Credential')
    @mock.patch('services.verification_service.Experience')
    def test_verify_user_profile(self, mock_experience_model, mock_credential_model, mock_user_model):
        """Test verification of a user's complete profile."""
        # Set up user mock
        mock_user = mock.Mock()
        mock_user.id = "user123"
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        
        # Set up credential mocks
        mock_credential1 = mock.Mock()
        mock_credential1.id = "cred1"
        mock_credential2 = mock.Mock()
        mock_credential2.id = "cred2"
        
        # Set up experience mocks
        mock_experience1 = mock.Mock()
        mock_experience1.id = "exp1"
        mock_experience2 = mock.Mock()
        mock_experience2.id = "exp2"
        
        # Configure model mocks
        mock_user_model.objects.get.return_value = mock_user
        mock_credential_model.objects.filter.return_value = [mock_credential1, mock_credential2]
        mock_experience_model.objects.filter.return_value = [mock_experience1, mock_experience2]
        
        # Mock batch verification methods
        with mock.patch.object(VerificationService, 'batch_verify_credentials') as mock_batch_creds:
            with mock.patch.object(VerificationService, 'batch_verify_experiences') as mock_batch_exps:
                # Configure batch verification mocks
                mock_batch_creds.return_value = {
                    'results': {"cred1": {"verified": True}, "cred2": {"verified": False}},
                    'summary': {'total': 2, 'verified': 1, 'failed': 1, 'timestamp': datetime.utcnow().isoformat()}
                }
                mock_batch_exps.return_value = {
                    'results': {"exp1": {"verified": True}, "exp2": {"verified": True}},
                    'summary': {'total': 2, 'verified': 2, 'failed': 0, 'timestamp': datetime.utcnow().isoformat()}
                }
                
                # Perform verification
                result = self.verification_service.verify_user_profile("user123")
                
                # Check results
                self.assertEqual(result['user_id'], "user123")
                self.assertEqual(result['username'], "testuser")
                self.assertEqual(result['summary']['verification_score'], 74.0)  # (50*0.6 + 100*0.4)
                self.assertEqual(result['summary']['verified_credentials'], 1)
                self.assertEqual(result['summary']['verified_experiences'], 2)


if __name__ == '__main__':
    unittest.main()
