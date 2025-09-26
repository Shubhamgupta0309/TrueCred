import json
from backend.services.blockchain_service import BlockchainService

if __name__ == '__main__':
    svc = BlockchainService()
    print(json.dumps(svc.get_connection_status(), default=str, indent=2))
