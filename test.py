from batch_rpc_provider import BatchRpcProvider

p = BatchRpcProvider('https://bor.golem.network', 5)

print(p.get_chain_id())
print(p.get_latest_block())

print(p.get_block_by_number(133, True))

for i in range(15000000, 15000000 + 1):

    block_info = p.get_block_by_number(i, True)
    if not block_info["transactions"]:
        continue

    for transaction in block_info["transactions"]:
        print(transaction['hash'])
        