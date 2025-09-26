"""
Lightweight blockchain status route to match frontend expectation at /api/blockchain/status.
"""
from flask import Blueprint, jsonify
from services.blockchain_service import BlockchainService

status_bp = Blueprint('blockchain_status', __name__, url_prefix='/api/blockchain')

_svc = None

def _get_svc():
    global _svc
    if _svc is None:
        _svc = BlockchainService()
    return _svc

@status_bp.route('/status', methods=['GET'])
def blockchain_status():
    svc = _get_svc()
    web3_connected = False
    chain_id = None
    try:
        if svc.web3:
            web3_connected = bool(svc.web3.is_connected())
            try:
                chain_id = svc.web3.eth.chain_id if web3_connected else None
            except Exception:
                chain_id = None
    except Exception:
        web3_connected = False

    contract_loaded = bool(getattr(svc, 'contract', None))
    contract_address = getattr(svc, 'contract_address', None)
    network = getattr(svc, 'network', None)

    return jsonify({
        'web3_connected': web3_connected,
        'chain_id': chain_id,
        'contract_loaded': contract_loaded,
        'contract_address': contract_address,
        'network': network,
    }), 200
