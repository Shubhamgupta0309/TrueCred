from dotenv import load_dotenv
import os, json
from web3 import Web3

load_dotenv('backend/.env')
rpc = os.environ.get('ETHEREUM_PROVIDER_URL')
print('Using RPC:', rpc)

w3 = Web3(Web3.HTTPProvider(rpc))

tx = '0xfb3cb445633d9145fd6b38a7958866a843999db391aad5e42f2915b366bc7887'

try:
    receipt = w3.eth.get_transaction_receipt(tx)
    block = w3.eth.get_block(receipt.blockNumber)
    def hb(x):
        try:
            return x.hex()
        except Exception:
            return x

    out = {
        'tx': tx,
        'status': int(receipt.status),
        'blockNumber': int(receipt.blockNumber),
        'blockTimestamp': int(block.timestamp),
        'to': receipt.to,
        'from': receipt['from'] if 'from' in receipt else None,
        'contractAddress': getattr(receipt, 'contractAddress', None),
        'logs_count': len(receipt.logs),
        'logs': [
            {
                'address': l.address,
                'topics': [hb(t) for t in l.topics],
                'data': hb(l.data)
            } for l in receipt.logs
        ]
    }
    print(json.dumps(out, indent=2))
except Exception as e:
    print('Error fetching tx:', e)
