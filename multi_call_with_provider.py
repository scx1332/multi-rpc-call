import requests
import json
import time

from web3 import Web3


class RPCCallDataWrap(Exception):
    def __init__(self, call_params):
        self.call_params = call_params


class ExtractMethodAndParamsProvider(Web3.HTTPProvider):
    def __init__(self):
        self.call_counter = 0
        pass

    def make_request(self, method, params):
        # validator wants to validate chain id so we have to return something
        if method == 'eth_chainId':
            dummy_response = {'jsonrpc': '2.0', 'id': 0, 'result': '0x1'}
            return dummy_response

        self.call_counter += 1
        call_params = {
            "method": method,
            "params": params,
        }
        # pass call params using
        raise RPCCallDataWrap(call_params)


def multi_call(call_data_params, max_in_req):
    call_data_array = []
    rpc_id = 1
    for call_data_param in call_data_params:
        call_data = {
            "jsonrpc": "2.0",
            "method": call_data_param["method"],
            "params": call_data_param["params"],
            "id": rpc_id
        }
        call_data_array.append(call_data)
        rpc_id += 1

    result_array = []
    if len(call_data_array) == 0:
        return result_array

    batch_count = (len(call_data_array) - 1) // max_in_req + 1
    for batch_no in range(0, batch_count):

        start_idx = batch_no * max_in_req
        end_idx = min(len(call_data_array), batch_no * max_in_req + max_in_req)

        # print(f"Requesting responses {start_idx} to {end_idx}")
        r = requests.post('http://54.38.192.207:8545', json=call_data_array[start_idx:end_idx])
        rpc_resp_array = json.loads(r.text)

        for call_data in call_data_array[start_idx:end_idx]:
            found_response = False
            for rpc_resp in rpc_resp_array:
                if rpc_resp["id"] == call_data["id"]:
                    found_response = True
                    break

            if not found_response:
                raise Exception(f"One of calls response not found {call_data['id']}")

            result_array.append(rpc_resp["result"])
    return result_array


def test_get_block_numer(start_block, end_block, batch_size):
    call_data_array = []

    for block_num in range(start_block, end_block):
        call_data = {
            "method": "eth_getBlockByNumber",
            "params": [hex(block_num), True],
        }
        call_data_array.append(call_data)

    bn = start_block
    for resp in multi_call(call_data_array, batch_size):
        if bn == (int(resp["number"], 0)):
            # print(f"OK {bn}")
            pass
        else:
            raise Exception(f"Test failed {bn}")
        bn += 1
    if bn != end_block:
        raise Exception(f"Not all responses found")


class Web3CallPreparer:
    def __init__(self):
        self.prov = ExtractMethodAndParamsProvider()
        self.w3 = Web3(self.prov)
        with open("IERC20.abi.json") as f:
            self.erc20abi = json.load(f)

    def get_balance(self, token_address, wallet):
        contract = self.w3.eth.contract(address=token_address, abi=self.erc20abi)
        try:
            contract.functions.balanceOf(wallet).call()
        except RPCCallDataWrap as wrappedData:
            return wrappedData.call_params

def test():
    web3_preparer = Web3CallPreparer()
    token_address = "0x2036807B0B3aaf5b1858EE822D0e111fDdac7018";
    wallet = "0x22DB5ceC3Ecd475Ab39Ee5729403D2F23c03Fb3d"
    call_data_params = []

    mumbai_holders = []
    with open("mumbai_holders.txt") as r:
        for line in r:
            if line.strip():
                mumbai_holders.append(line.strip())

    start = time.time()
    print(f"Prepare holders params for {len(mumbai_holders)} holder addresses")
    for mumbai_holder in mumbai_holders:
        call_params = web3_preparer.get_balance(token_address, wallet)
        call_data_params.append(call_params)
    end = time.time()
    print(f"Preparation took {end - start:0.3f}s")

    print(f"Start multi call for {len(mumbai_holders)} holder addresses")
    start = time.time()
    print(multi_call(call_data_params, 17))
    end = time.time()
    print(f"Response took {end - start:0.3f}s")


if __name__ == "__main__":
    test()
