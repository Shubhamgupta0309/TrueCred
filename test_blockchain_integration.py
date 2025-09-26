#!/usr/bin/env python3
import os
import sys
from datetime import datetime

# Add backend folder to path so imports inside backend can be resolved the same way routes do
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from flask import Flask

import pytest

from backend.config import get_config
from backend.utils.database import init_db
from backend.models.user import User
from backend.models.credential import Credential
from backend.services.credential_service import CredentialService
from backend.services.blockchain_service import BlockchainService


def setup_app_db():
    app = Flask(__name__)
    config = get_config('testing')
    app.config.from_object(config)
    init_db(app)
    return app


def ensure_test_user():
    user = User.objects(email="test_integration@example.com").first()
    if not user:
        user = User(
            username="test_integration_user",
            email="test_integration@example.com",
            password="hashedpassword",
            first_name="Test",
            last_name="Integration",
            role="student"
        )
        user.save()
    return user


def test_issue_and_store_credential_on_blockchain():
    """Create a credential, simulate verification and store on blockchain, then assert blockchain fields exist."""
    # Initialize DB
    setup_app_db()

    # Ensure user exists
    user = ensure_test_user()

    # Create credential via service
    credential_data = {
        'title': 'Integration Test Certificate',
        'issuer': 'Integration University',
        'description': 'Issued by test',
        'type': 'certificate',
        'issue_date': datetime.utcnow().isoformat(),
        'expiry_date': None,
        'document_url': None,
        'metadata': {'integration_test': True}
    }

    credential, err = CredentialService.create_credential(user_id=str(user.id), data=credential_data)
    assert err is None, f"Failed to create credential: {err}"
    assert credential is not None

    # Simulate marking verified (some endpoints do this prior to storing on chain)
    credential.verified = True
    credential.verified_at = datetime.utcnow()
    credential.save()

    # Call the blockchain service (this should return mock 'success' when no real node is connected)
    blockchain = BlockchainService()
    result = blockchain.store_credential_hash(
        title=credential.title,
        issuer=credential.issuer or "Unknown Issuer",
        student_id=str(credential.user.id),
        ipfs_hash=credential.document_url or credential.ipfs_hash or ""
    )

    assert result is not None, "Blockchain service returned None"
    assert result.get('status') in ('success', 'error') or result.get('mock') is True

    # If successful or mock, emulate route behavior and persist blockchain fields on credential
    if result.get('status') == 'success' or result.get('mock') or result.get('simulated'):
        credential.blockchain_tx_hash = result.get('transaction_hash')
        credential.blockchain_credential_id = result.get('credential_id')
        # store the raw result as blockchain_data for inspection
        credential.blockchain_data = result
        credential.verification_status = 'verified'
        credential.save()

    # Reload credential and assert blockchain fields are populated when expected
    saved = Credential.objects(id=credential.id).first()
    assert saved is not None

    # Mock mode returns mock transaction hash and credential id
    assert saved.blockchain_tx_hash, "blockchain_tx_hash not saved"
    assert saved.blockchain_credential_id, "blockchain_credential_id not saved"
    assert isinstance(saved.blockchain_data, dict) and saved.blockchain_data, "blockchain_data not saved or not a dict"
    assert saved.verification_status == 'verified'

    # Cleanup: optional - remove created credential (keep for debugging if you want)
    # Credential.objects(id=credential.id).delete()


if __name__ == '__main__':
    pytest.main([os.path.basename(__file__)])
