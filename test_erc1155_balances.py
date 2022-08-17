import logging
import time

from batch_rpc_provider import BatchRpcProvider, BatchRpcException

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def test_erc1155_get_balance():
    p = BatchRpcProvider('http://54.38.192.207:8545', 10000)

    logger.info("Loading holders data...")
    holder_id_pairs = []
    for i in range(0, 10000):
        holder_id_pairs.append(("0x33C2af27BD58C77E47Cb82B068a2313B9878A9a2", i))
    for i in range(0, 10000):
        holder_id_pairs.append(("0x2f252433E8eCa94C77F2b8D573A3a32032530F5C", i))

    try:
        logger.info("Checking holders data...")
        resp = p.get_erc1155_balances(holder_id_pairs, "0x430FfE792083B45f8cd55857BC7055172a9c8767", block_no='latest')
        for holder_id_pair, res in zip(holder_id_pairs, resp):
            amount = int(res, 0)
            if amount != 0:
                logger.debug(f"Holder: {holder_id_pair[0]} Id: {holder_id_pair[1]} Amount: {amount}")
    except BatchRpcException as ex:
        logger.error(f"{ex}")
        pass

    # test error report
    try:
        resp = p.get_erc1155_balances(holder_id_pairs, "0x430FfE792083B45f8cd55857BC7055172a9c8767", block_no='0x5555')
    except BatchRpcException as ex:
        logger.info(f"Node should report error that trie node is missing")
        pass

    # test error report
    try:
        p = BatchRpcProvider('http://54.38.192.207:8545', 20000)
        resp = p.get_erc1155_balances(holder_id_pairs, "0x430FfE792083B45f8cd55857BC7055172a9c8767", block_no='0x5555')
    except BatchRpcException as ex:
        logger.info(f"Node limit should be exceeded")
        pass


if __name__ == "__main__":
    test_erc1155_get_balance()



