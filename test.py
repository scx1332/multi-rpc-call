from batch_rpc_provider import BatchRpcProvider, BatchRpcException
import logging



logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

p = BatchRpcProvider('https://mumbai-temp.golem.network/api/rpc/polygon/MAaCpE421MddDmzMLcAp', 1000)
# p = BatchRpcProvider('http://51.178.88.224/polygon', 1000)

def check_in_block(block_num):
    block_info = p.get_block_by_number(block_num, False)
    if not block_info["transactions"]:
        raise Exception("No transaction found")

    block_num = int(block_info["number"], 0)

    max_transactions_to_check = 10
    transactions_checked = 0
    for transaction in block_info["transactions"]:
        test_transaction_hash = transaction['hash']
        test_transaction_index = int(transaction['transactionIndex'], 16)

        transaction_info_by_hash = p.get_transaction_by_hash(test_transaction_hash)
        if transaction_info_by_hash is None:
            raise Exception(f"Transaction with hash {test_transaction_hash} not found")

        transaction_info_by_number = p.get_transaction_by_block_number_and_index(block_num, test_transaction_index)
        if transaction_info_by_number is None:
            raise Exception(f"Transaction with block number {block_num} and index {test_transaction_index} not found")

        transactions_checked += 1
        print(f"Successfully checked transaction {transactions_checked}")
        if transactions_checked >= max_transactions_to_check:
            break

full_blocks = []

def search_first():
    for i in range(0, 1000):
        block_start = 10000000 + i * 1000
        res = p.get_blocks_by_range(block_start, 1000, False)
        for idx, block in enumerate(res):
            if block["transactions"]:
                print(f"Non empty block: {block_start + idx}")
                with open("blocks.txt", "a") as w:
                    w.write(f"{block_start + idx}\n")

def search():

    latest_block = p.get_latest_block()

    chain_id = p.get_chain_id()

    max_succeeded_block = latest_block
    min_failed_block = -1
    current_block = max_succeeded_block

    max_steps = 100
    while max_steps > 0:
        max_steps -= 1
        try:
            logger.info(f"Checking block {current_block}")
            check_in_block(current_block)
            # logger.info(f"Balance at block {current_block} is {balance}")
            success = True
        except Exception as ex:
            pass
            success = False

        if success:
            max_succeeded_block = current_block
        else:
            min_failed_block = current_block

        if max_succeeded_block - min_failed_block == 1:
            logger.info(f"Successfully found node last state: {max_succeeded_block}. Archive depth blocks: {latest_block - max_succeeded_block}")
            return max_succeeded_block, latest_block - max_succeeded_block

        current_block = min_failed_block + (max_succeeded_block - min_failed_block) // 2

search_first()

        