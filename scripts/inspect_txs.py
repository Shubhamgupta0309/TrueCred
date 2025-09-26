from dotenv import load_dotenv
import os, json
from web3 import Web3

load_dotenv('backend/.env')
rpc = os.environ.get('ETHEREUM_PROVIDER_URL')
print('Using RPC:', rpc)

w3 = Web3(Web3.HTTPProvider(rpc))

txs = [
 '0xa0e1ffb4ac94fedf1b237d1a1ee9d6a7e6cd4cda21f024f57d2367ff2fbb0397',
 '0x0191977398ca7cc3bd3d6bbd8608fae958ca17b1f238a672dd5d72eb51805eba'
]

for tx in txs:
    try:
        receipt = w3.eth.get_transaction_receipt(tx)
        block = w3.eth.get_block(receipt.blockNumber)
        out = {
            'tx': tx,
            'status': receipt.status,
            'blockNumber': receipt.blockNumber,
            'blockTimestamp': block.timestamp,
            'to': receipt.to,
            'contractAddress': getattr(receipt, 'contractAddress', None),
            'logs_count': len(receipt.logs)
        }
        print(json.dumps(out, indent=2))
    except Exception as e:
        print('Error for', tx, e)
