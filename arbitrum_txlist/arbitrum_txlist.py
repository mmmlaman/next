import requests
import pandas as pd
import threading
import time
import json
ARBITRUMSCAN_API_URL = "https://api.arbiscan.io/api"
API_KEYS_ARBITRUM = ["", "", ""]

# Dictionaries to track request counts and times for each API key
request_counters = {key: 0 for key in API_KEYS_ARBITRUM}
last_request_times = {key: time.time() for key in API_KEYS_ARBITRUM}

def get_transactions_arbitrum(address, api_key):
    """Fetch all transactions for a given address on Arbitrum."""
    # Use the global dictionaries
    global request_counters, last_request_times

    # Check if we need to rate limit for the given API key
    current_time = time.time()
    if current_time - last_request_times[api_key] < 1:  # Less than a second since last request
        request_counters[api_key] += 1
        if request_counters[api_key] >= 3:
            time.sleep(0.2)
            request_counters[api_key] = 0
    else:
        request_counters[api_key] = 1
        last_request_times[api_key] = current_time

    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": api_key
    }
    response = requests.get(ARBITRUMSCAN_API_URL, params=params)

    # Check HTTP status code
    if response.status_code != 200:
        print(f"HTTP Error {response.status_code} for address {address} on Arbitrum. Response: {response.text}")
        return []

    # Try to decode the JSON response
    try:
        data = response.json()
    except json.decoder.JSONDecodeError:
        print(f"Failed to decode JSON response for address {address} on Arbitrum. Response: {response.text}")
        return []

    if data["status"] == "1":
        return data["result"]
    else:
        print(f"Error fetching transactions for address {address} on Arbitrum: {data['message']}")
        return []

def find_related_addresses_thread_arbitrum(addresses, api_key, result_container):
    """Find related address pairs in a threaded environment for arbitrum."""
    related_pairs = set()
    for address in addresses:
        transactions = get_transactions_arbitrum(address, api_key)
        for tx in transactions:
            if tx["from"] in addresses and tx["to"] in addresses and tx["from"] != tx["to"]:
                pair = tuple(sorted([tx["from"], tx["to"]]))
                related_pairs.add(pair)
    result_container.extend(related_pairs)

def find_related_addresses_arbitrum(addresses):
    """Find related address pairs for a given list of addresses on arbitrum."""
    n = len(addresses)
    split_addresses = [addresses[:n//3], addresses[n//3:2*n//3], addresses[2*n//3:]]

    results = []
    threads = []
    for i in range(3):
        thread = threading.Thread(target=find_related_addresses_thread_arbitrum, args=(split_addresses[i], API_KEYS_ARBITRUM[i], results))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return set(results)

addresses = pd.read_csv(r"D:\sybil\allocations.csv")['address'].tolist()
related_pairs_arbitrum = find_related_addresses_arbitrum(addresses)

# Organize data and save to CSV file
related_addresses_strings = ['<->'.join(pair) for pair in related_pairs_arbitrum]
df_related_addresses = pd.DataFrame(related_addresses_strings, columns=["address"])
df_related_addresses.to_csv(r"D:\sybil\arbitrum_txlist_related_address_pairs.csv", index=False)

print("Related address pairs on Optimism have been saved to arbitrum_txlist_related_address_pairs.csv.")
