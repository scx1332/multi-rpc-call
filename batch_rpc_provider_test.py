import logging
import time

from batch_rpc_provider import BatchRpcProvider, BatchRpcException

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def test_erc1155_get_balance():
    p = BatchRpcProvider('http://54.38.192.207:8545', 10000)

    holder_id_pairs = []
    for i in range(0, 10000):
        holder_id_pairs.append(("0x33C2af27BD58C77E47Cb82B068a2313B9878A9a2", i))
    for i in range(0, 10000):
        holder_id_pairs.append(("0x2f252433E8eCa94C77F2b8D573A3a32032530F5C", i))

    try:
        resp = p.get_erc1155_balances(holder_id_pairs, "0x430FfE792083B45f8cd55857BC7055172a9c8767", block_no='latest')
        for holder_id_pair, res in zip(holder_id_pairs, resp):
            amount = int(res, 0)
            if amount != 0:
                print(f"Holder: {holder_id_pair[0]} Id: {holder_id_pair[1]} Amount: {amount}")
    except BatchRpcException as ex:
        logger.error(f"{ex}")
        pass

    # test error report
    try:
        resp = p.get_erc1155_balances(holder_id_pairs, "0x430FfE792083B45f8cd55857BC7055172a9c8767", block_no='0x5555')
    except BatchRpcException as ex:
        logger.info(f"Node should report error that trie node is missing")
        pass


def test_get_balance():
    token_address = "0x2036807B0B3aaf5b1858EE822D0e111fDdac7018";
    call_data_params = []

    mumbai_holders = []
    print("Load holders data...")
    with open("mumbai_holders.txt") as r:
        for line in r:
            if line.strip():
                mumbai_holders.append(line.strip())

    print(f"Loaded {len(mumbai_holders)} mumbai GLM holders...")

    p = BatchRpcProvider('http://54.38.192.207:8545', 20)
    print(f"Start multi call for {len(mumbai_holders)} holder addresses")
    start = time.time()
    resp = p.get_erc20_balances(mumbai_holders, token_address)
    end = time.time()

    sum_of_glms = 0
    for mumbai_holder_wallet, res in zip(mumbai_holders, resp):
        for res in resp:
            glms = int(res, 0) / 1000000000 / 1000000000
            sum_of_glms += glms
            # print(f"Holder {mumbai_holder_wallet}: {glms}")
    print(f"Total number of GLMS: {sum_of_glms}")

    print(f"Response took {end - start:0.3f}s")


if __name__ == "__main__":
    test_erc1155_get_balance()
    test_get_balance()
