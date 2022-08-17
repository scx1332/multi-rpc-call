import logging
import time

from batch_rpc_provider import BatchRpcProvider, BatchRpcException

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def test_block_history():
    p = BatchRpcProvider('http://54.38.192.207:8545', 20)
    latest_block = p.get_latest_block()

    token_address = "0x2036807B0B3aaf5b1858EE822D0e111fDdac7018"

    single_holder_array = ['0xc596aee002ebe98345ce3f967631aaf79cfbdf41']

    max_succeeded_block = latest_block
    min_failed_block = 1
    current_block = max_succeeded_block

    max_steps = 100
    while max_steps > 0:
        max_steps -= 1
        success = True
        try:
            resp = p.get_erc20_balances(single_holder_array, token_address, f"0x{current_block:x}")
            success = True
        except BatchRpcException as ex:
            success = False

        if success:
            max_succeeded_block = current_block
        else:
            min_failed_block = current_block

        if max_succeeded_block - min_failed_block == 1:
            logger.info(f"Successfully found node last state: {max_succeeded_block}. Archive depth blocks: {latest_block - max_succeeded_block}")
            break

        current_block = min_failed_block + (max_succeeded_block - min_failed_block) // 2


if __name__ == "__main__":
    test_block_history()


