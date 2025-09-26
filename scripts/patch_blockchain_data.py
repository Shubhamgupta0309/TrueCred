"""Patch script: populate credential.blockchain_data for existing records.

Usage: run from repository root with the same environment used by the backend.
This will try to fetch block timestamp from the configured ETH provider if possible.
"""
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId

# Ensure backend/.env is loaded
load_dotenv()
env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Make sure the repo root is on sys.path so 'backend' package imports work when
# this script is executed directly from the repository root.
import sys
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Ensure MongoEngine has a default connection when running this script standalone.
from mongoengine import connect

# Connect to MongoDB using MONGO_URI from environment (loaded above).
mongodb_uri = os.environ.get('MONGO_URI')
if not mongodb_uri:
    # Try to look for backend/.env as a fallback (already loaded above) and re-read
    env_path2 = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
    if os.path.exists(env_path2):
        # already loaded earlier, but double-check env var
        mongodb_uri = os.environ.get('MONGO_URI')

if not mongodb_uri:
    raise RuntimeError('MONGO_URI environment variable is required to run this script.\n'
                       'Set MONGO_URI in your environment or add it to backend/.env')

# Establish a default mongoengine connection (alias='default')
connect(host=mongodb_uri, alias='default')

# Now import application models / services that rely on mongoengine
from backend.services.blockchain_service import BlockchainService
from backend.models.credential import Credential


def patch_credential(credential_id_str: str):
    cred = Credential.objects(id=ObjectId(credential_id_str)).first()
    if not cred:
        print('Credential not found:', credential_id_str)
        return False

    print('Found credential:', str(cred.id))

    # If blockchain_data already has tx info, skip
    existing = getattr(cred, 'blockchain_data', None) or {}
    has_tx = bool(existing.get('tx_hash') or existing.get('transaction_hash'))
    if has_tx:
        print('Credential already has blockchain_data.tx_hash; nothing to do')
        return True

    # Build new blockchain_data from top-level fields
    new_data = dict(existing)
    if getattr(cred, 'blockchain_tx_hash', None):
        new_data['transaction_hash'] = cred.blockchain_tx_hash
        new_data['tx_hash'] = cred.blockchain_tx_hash
    if getattr(cred, 'blockchain_credential_id', None):
        new_data['credential_id'] = cred.blockchain_credential_id

    # Try to enrich with timestamp and block_number via blockchain service
    bs = BlockchainService()
    if bs.web3 and bs.web3.is_connected() and new_data.get('tx_hash'):
        try:
            tx_hash = new_data.get('tx_hash')
            # web3 expects hex string
            receipt = bs.web3.eth.get_transaction_receipt(tx_hash)
            if receipt:
                new_data['block_number'] = receipt.blockNumber
                # get block timestamp
                try:
                    block = bs.web3.eth.get_block(receipt.blockNumber)
                    new_data['timestamp'] = int(block.timestamp)
                except Exception:
                    new_data['timestamp'] = None
        except Exception as e:
            print('Warning: failed to fetch receipt/timestamp:', e)

    # Assign and save
    cred.blockchain_data = new_data
    cred.save()
    print('Updated credential.blockchain_data:', new_data)
    return True


if __name__ == '__main__':
    # Replace with credential id you want to patch
    target_id = os.environ.get('PATCH_CREDENTIAL_ID', '68d56e2c5d2c0722681ae324')
    ok = patch_credential(target_id)
    if ok:
        print('Patch completed')
    else:
        print('Patch failed')
