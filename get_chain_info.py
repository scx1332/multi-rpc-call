import requests
import json
import sys

call_data = {
    "jsonrpc": "2.0",
    "method": "eth_chainId",
    "params": [],
    "id": 0
}

r = requests.post(sys.argv[1], json=call_data)
res = json.loads(r.text)

latest_block = int(res["result"], 0)
if latest_block == 80001:
    print("Detected Mumbai RPC")
else:
    print(f"Chain ID: {latest_block}")