import requests
import pandas as pd
from collections import defaultdict
import time

SNOWTRACE_API_URL = "https://api.snowtrace.io/api"
API_KEYS_AVAX = ["KEY1",
                 "KEY2",
                 "KEY3"]

api_call_count = 0  # counter to track number of API calls in the last second
last_call_timestamp = time.time()  # timestamp of the last API call

def get_transactions_avax(address, api_key):
    global api_call_count
    global last_call_timestamp

    current_time = time.time()
    if current_time - last_call_timestamp >= 1:  # more than one second has passed
        api_call_count = 0
        last_call_timestamp = current_time

    if api_call_count >= 4:  # if we made 4 or more calls in the last second
        time.sleep(0.2)  # pause for 0.2 seconds
        api_call_count = 0  # reset the counter after the sleep

    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": api_key
    }
    response = requests.get(SNOWTRACE_API_URL, params=params)
    data = response.json()
    if data["status"] == "1":
        return data["result"]
    else:
        print(f"Error fetching transactions for address {address} on AVAX: {data['message']}")
        return []

groups_df = pd.read_csv(r"D:\sybil\avax_txlist_large_connected_groups.csv")
groups = groups_df['Large Connected Groups'].tolist()

group_token_transfers = defaultdict(list)

# A set to keep track of seen transaction hashes
seen_hashes = set()

for index, group in enumerate(groups, start=1):
    addresses = set(group.split(" <-> "))
    print(addresses)
    for address in addresses:
        transactions = get_transactions_avax(address, API_KEYS_AVAX[0])
        for tx in transactions:
            # If the transaction hash has been seen before, we skip it
            if tx["hash"] in seen_hashes:
                continue
            # Add current transaction hash to the seen_hashes set
            seen_hashes.add(tx["hash"])
            if tx["from"] in addresses and tx["to"] in addresses and tx["from"] != tx["to"]:
                transfer_str = (f'hash: "{tx["hash"]}" from: "{tx["from"]}" to: "{tx["to"]}" '
                                f'tokenSymbol: "AVAX" value: "{int(tx["value"]) / (10 ** 18)}"')
                group_token_transfers[index].append(transfer_str)

max_len = max([len(v) for v in group_token_transfers.values()]) + 2  # +2 because of the "GROUP X" and address lines
df = pd.DataFrame(index=range(max_len))

for index, transfers in group_token_transfers.items():
    col_data = [f"GROUP {index}", groups[index-1]] + transfers + [''] * (max_len - len(transfers) - 2)
    df[f"GROUP {index}"] = col_data

# save
output_file_path = r"D:\sybil\avax_txlist_token_transfers_per_group.csv"
df.to_csv(output_file_path, index=False)

print("success")