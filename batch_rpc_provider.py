import requests
import time
import json
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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


class BatchRpcException(Exception):
    pass


class BatchRpcProvider:
    def __init__(self, endpoint, batch_size):
        self._endpoint = endpoint
        self._batch_size = batch_size
        self.number_of_batches_sent = 0

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

            logger.info(f"Requesting responses {start_idx} to {end_idx}")

            r = requests.post(endpoint, json=call_data_array[start_idx:end_idx])
            if r.status_code == 413:
                raise Exception("Data too big")
            if r.status_code != 200:
                raise Exception(f"Other error {r}")

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

                if 'error' in rpc_resp:
                    logger.error(f"Error during request number {call_data['id']}:")
                    logger.error(f"\tCall data: {call_data}")
                    logger.error(f"\tRPC returned error: {rpc_resp['error']}")
                    raise BatchRpcException("RPC error, check log for details")

                result_array.append(rpc_resp["result"])
        return result_array

    def get_erc20_balances(self, holders, token_address):
        call_data_params = []
        for holder in holders:
            call_params = _erc20_get_balance_call(token_address, holder, 'latest')
            call_data_params.append(call_params)

        resp = self._multi_call(self._endpoint, call_data_params, self._batch_size)
        return resp

    def get_erc1155_balances(self, holder_id_pairs, token_address, block_no='latest'):
        call_data_params = []
        for holder_id_pair in holder_id_pairs:
            call_params = _erc1155_get_balance_call(token_address, holder_id_pair[0], holder_id_pair[1], block_no)
            call_data_params.append(call_params)

        resp = self._multi_call(self._endpoint, call_data_params, self._batch_size)
        return resp



