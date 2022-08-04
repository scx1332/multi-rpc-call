import requests
import json
import time


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


if __name__ == "__main__":
    start = time.time()
    test_get_block_numer(1000, 2000, 20)
    end = time.time()
    print(f"test_get_block_numer(1000, 2000, 20) {end - start:0.3f}s")

    start = time.time()
    test_get_block_numer(1000, 2000, 10)
    end = time.time()
    print(f"test_get_block_numer(1000, 2000, 10) {end - start:0.3f}s")

    start = time.time()
    test_get_block_numer(1000, 2000, 5)
    end = time.time()
    print(f"test_get_block_numer(1000, 2000, 5) {end - start:0.3f}s")

    start = time.time()
    test_get_block_numer(1000, 2000, 1)
    end = time.time()
    print(f"test_get_block_numer(1000, 2000, 1) {end - start:0.3f}s")
