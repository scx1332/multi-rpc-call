from batch_rpc_provider import BatchRpcProvider
from test_archive_history import test_block_history

p = BatchRpcProvider("http://54.38.192.207:8545", 1)
mumbai1 = test_block_history(p)

p = BatchRpcProvider("http://141.95.34.226:8545", 1)
mumbai2 = test_block_history(p)

p = BatchRpcProvider("http://54.36.174.74:8545", 1)
mumbai3 = test_block_history(p)

print(f"Mumbai1: {mumbai1}, Mumbai2: {mumbai2}, Mumbai3: {mumbai3}")
