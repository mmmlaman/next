import requests
import pandas as pd
import threading
import time

SNOWTRACE_API_URL = "https://api.snowtrace.io/api"
API_KEYS_AVAX = ["",
                 "",
                 ""]

# Dictionaries to track request counts and times for each API key
request_counters = {key: 0 for key in API_KEYS_AVAX}
last_request_times = {key: time.time() for key in API_KEYS_AVAX}

def get_transactions_avax(address, api_key):
    # Use the global dictionaries
    global request_counters, last_request_times

    # Check if we need to rate limit for the given API key
    current_time = time.time()
    if current_time - last_request_times[api_key] < 1:  # Less than a second since last request
        request_counters[api_key] += 1
        if request_counters[api_key] >= 3:  # Adjust this based on Snowtrace's rate limit
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
    for _ in range(3):  # Try up to 3 times
        try:
            response = requests.get(SNOWTRACE_API_URL, params=params, timeout=10)  # Added a timeout for the request
            time.sleep(0.2)
            break
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}. Retrying...")
            time.sleep(2)  # Wait for 2 seconds before retrying
    else:
        print("Failed to get a response after 3 attempts. Skipping...")
        return []

    response = requests.get(SNOWTRACE_API_URL, params=params)
    if response.status_code != 200:
        print(f"Error fetching data for address {address} on Avax. Status code: {response.status_code}")
        return []

    data = response.json()

    if data["status"] == "1":
        return data["result"]
    else:
        print(f"Error fetching transactions for address {address} on Avax: {data['message']}")
        return []

def find_related_addresses_thread_avax(addresses, api_key, result_container):
    related_pairs = set()
    for address in addresses:
        transactions = get_transactions_avax(address, api_key)
        for tx in transactions:
            if tx["from"] in addresses and tx["to"] in addresses and tx["from"] != tx["to"]:
                pair = tuple(sorted([tx["from"], tx["to"]]))
                related_pairs.add(pair)
    result_container.extend(related_pairs)

def find_related_addresses_avax(addresses):
    n = len(addresses)
    split_addresses = [addresses[:n//3], addresses[n//3:2*n//3], addresses[2*n//3:]]

    results = []
    threads = []
    for i in range(3):
        thread = threading.Thread(target=find_related_addresses_thread_avax, args=(split_addresses[i], API_KEYS_AVAX[i], results))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return set(results)

addresses = pd.read_csv(r"D:\sybil\allocations.csv")['address'].tolist()
related_pairs_avax = find_related_addresses_avax(addresses)

# save
related_addresses_strings = ['<->'.join(pair) for pair in related_pairs_avax]
df_related_addresses = pd.DataFrame(related_addresses_strings, columns=["address"])
df_related_addresses.to_csv(r"D:\sybil\avax_txlist_related_address_pairs.csv", index=False)

print("Related address pairs on Avalanche have been saved to avax_txlist_related_address_pairs.csv.")
