import requests
import time
import json




def _erc20_get_balance_call(token_address, wallet, block):
    strip_wallet = wallet.replace("0x", "")
    abi_method = "70a08231000000000000000000000000"
    return {
        'method': 'eth_call',
        'params': [
            {
                'to': token_address,
                'data': f"0x{abi_method}{strip_wallet}"
            },
            block]
    }

def _erc1155_get_balance_call(token_address, wallet, id, block):
    strip_wallet = wallet.replace("0x", "")
    abi_method = "00fdd58e000000000000000000000000"
    return {
        'method': 'eth_call',
        'params': [
            {
                'to': token_address,
                'data': f"0x{abi_method}{strip_wallet}{id:064x}"
            },
            block]
    }


class BatchGetBalanceProvider:
    def __init__(self, endpoint, batch_size, verbose=False):
        self._endpoint = endpoint
        self._batch_size = batch_size
        self.number_of_batches_sent = 0
        self._verbose = verbose

    def _multi_call(self, endpoint, call_data_params, max_in_req):
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

            if self._verbose:
                print(f"Requesting responses {start_idx} to {end_idx}")

            r = requests.post(endpoint, json=call_data_array[start_idx:end_idx])
            self.number_of_batches_sent += 1
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

    def get_erc20_balances(self, holders, token_address):
        call_data_params = []
        for holder in holders:
            call_params = _erc20_get_balance_call(token_address, holder, 'latest')
            call_data_params.append(call_params)

        resp = self._multi_call(self._endpoint, call_data_params, self._batch_size)
        return resp

    def get_erc1155_balances(self, holder_id_pairs, token_address):
        call_data_params = []
        for holder_id_pair in holder_id_pairs:
            call_params = _erc1155_get_balance_call(token_address, holder_id_pair[0], holder_id_pair[1], 'latest')
            call_data_params.append(call_params)

        resp = self._multi_call(self._endpoint, call_data_params, self._batch_size)
        return resp


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

    p = BatchGetBalanceProvider('http://54.38.192.207:8545', 20)
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


def test_erc1155_get_balance():
    p = BatchGetBalanceProvider('http://54.38.192.207:8545', 100, verbose=True)

    holder_id_pairs = []
    for i in range(0, 3100):
        holder_id_pairs.append(("0x33C2af27BD58C77E47Cb82B068a2313B9878A9a2", i))
    for i in range(0, 3100):
        holder_id_pairs.append(("0x2f252433E8eCa94C77F2b8D573A3a32032530F5C", i))

    resp = p.get_erc1155_balances(holder_id_pairs, "0x430FfE792083B45f8cd55857BC7055172a9c8767")
    for holder_id_pair, res in zip(holder_id_pairs, resp):
        amount = int(res, 0)
        if amount != 0:
            print(f"Holder: {holder_id_pair[0]} Id: {holder_id_pair[1]} Amount: {amount}")


if __name__ == "__main__":
    test_erc1155_get_balance()
    # test_get_balance()
