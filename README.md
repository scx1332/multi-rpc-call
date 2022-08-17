# multi-rpc-call

curl -X POST --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' -H "Content-Type: application/json" localhost:8545
curl -X POST --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' -H "Content-Type: application/json" http://54.38.192.207:8545
curl -X POST --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' -H "Content-Type: application/json" http://51.38.53.113:8545/

# batch_rpc_provider

Simple web3 provider, using basic json RPC commands and RPC batching

BatchRpcProvider implementation is in the single file: batch_rpc_provider.py

Only dependency needed to run is requests library.


