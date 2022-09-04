import logging
import time
import argparse

from batch_rpc_provider import BatchRpcProvider, BatchRpcException

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser(description='Test params')
parser.add_argument('--target-url', dest="target_url", type=str, help='Node url', default="http://54.36.174.74:8745")
parser.add_argument('--batch-size', dest="batch_size", type=int, help='Batch size', default=1000)

args = parser.parse_args()

def test_get_balance():
    token_address = "0x7DD9c5Cba05E151C895FDe1CF355C9A1D5DA6429"
    call_data_params = []

    glm_holders = []
    logger.info("Load holders data...")
    with open("ethereum_golem_holders.txt") as r:
        for line in r:
            if line.strip():
                glm_holders.append(line.strip())

    logger.info(f"Loaded {len(glm_holders)} ethereum GLM holders...")

    # p = BatchRpcProvider(args.target_url, args.batch_size)
    p = BatchRpcProvider('http://54.36.174.74:8745', 1000)
    # p = BatchRpcProvider('http://10.30.8.195:8545', 1000)
    # p = BatchRpcProvider('https://geth.golem.network:55555', 1000)

    logger.info(f"Start multi call for {len(glm_holders)} holder addresses")
    start = time.time()
    resp = p.get_erc20_balances(glm_holders, token_address)
    end = time.time()

    glm_total_amount = 0
    for mumbai_holder_wallet, res in zip(glm_holders, resp):
        glm_amount = int(res, 0) / 1000000000 / 1000000000
        glm_total_amount += glm_amount
        logger.debug(f"Holder {mumbai_holder_wallet}: {glm_amount}")

    logger.info(f"Total GLM amount found: {glm_total_amount}")

    logger.info(f"Response took {end - start:0.3f}s")


if __name__ == "__main__":
    test_get_balance()


