import logging
import time

from batch_rpc_provider import BatchRpcProvider, BatchRpcException

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def test_get_balance():
    token_address = "0x2036807B0B3aaf5b1858EE822D0e111fDdac7018"
    call_data_params = []

    mumbai_holders = []
    logger.info("Load holders data...")
    with open("mumbai_holders.txt") as r:
        for line in r:
            if line.strip():
                mumbai_holders.append(line.strip())

    logger.info(f"Loaded {len(mumbai_holders)} mumbai GLM holders...")

    p = BatchRpcProvider('https://mumbai-temp.golem.network/api/rpc/polygon/MAaCpE421MddDmzMLcAp', 5)
    logger.info(f"Start multi call for {len(mumbai_holders)} holder addresses")
    start = time.time()
    resp = p.get_erc20_balances(mumbai_holders, token_address)
    end = time.time()

    glm_total_amount = 0
    for mumbai_holder_wallet, res in zip(mumbai_holders, resp):
        glm_amount = int(res, 0) / 1000000000 / 1000000000
        glm_total_amount += glm_amount
        logger.debug(f"Holder {mumbai_holder_wallet}: {glm_amount}")

    logger.info(f"Total GLM amount found: {glm_total_amount}")

    logger.info(f"Response took {end - start:0.3f}s")


if __name__ == "__main__":
    for i in range(0,10000):
        test_get_balance()


