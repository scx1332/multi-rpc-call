import logging
import argparse

from batch_rpc_provider import BatchRpcProvider, BatchRpcException

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def test_block_history(p: BatchRpcProvider):
    latest_block = p.get_latest_block()

    chain_id = p.get_chain_id()

    check_balance_addr = ""
    if chain_id == 1:
        check_balance_addr = "0x0000000000000000000000000000000000000000"
    elif chain_id == 4:
        check_balance_addr = "0x0000000000000000000000000000000000000000"
    elif chain_id == 5:
        check_balance_addr = "0x0000000000000000000000000000000000000000"
    elif chain_id == 137:
        check_balance_addr = "0x0000000000000000000000000000000000001010"
    elif chain_id == 80001:
        check_balance_addr = "0x0000000000000000000000000000000000001010"
    else:
        raise Exception(f"Unrecognized chain id {chain_id}")

    max_succeeded_block = latest_block
    min_failed_block = -1
    current_block = max_succeeded_block

    max_steps = 100
    while max_steps > 0:
        max_steps -= 1
        try:
            logger.info(f"Checking block {current_block}")
            balance = p.get_balance(check_balance_addr, f"0x{current_block:x}")
            logger.info(f"Balance at block {current_block} is {balance}")
            #p.get_erc20_balances(single_holder_array, token_address, f"0x{current_block:x}")
            success = True
        except BatchRpcException:
            success = False

        if success:
            max_succeeded_block = current_block
        else:
            min_failed_block = current_block

        if max_succeeded_block - min_failed_block == 1:
            logger.info(f"Successfully found node last state: {max_succeeded_block}. Archive depth blocks: {latest_block - max_succeeded_block}")
            return max_succeeded_block, latest_block - max_succeeded_block

        current_block = min_failed_block + (max_succeeded_block - min_failed_block) // 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test params')
    parser.add_argument('--target-url', dest="target_url", type=str, help='Node name', default="http://54.38.192.207:8545")

    args = parser.parse_args()
    p = BatchRpcProvider(args.target_url, 1)
    print(test_block_history(p))


