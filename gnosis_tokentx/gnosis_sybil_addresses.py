import pandas as pd

data = pd.read_csv(r"D:\sybil\gnosis_tokentx_related_address_pairs.csv")

data[['sender', 'receiver']] = data['address'].str.split('<->', expand=True)

address_mapping = {}

for _, row in data.iterrows():
    sender, receiver = row['sender'].strip(), row['receiver'].strip()

    if sender not in address_mapping:
        address_mapping[sender] = set()
    address_mapping[sender].add(receiver)

    if receiver not in address_mapping:
        address_mapping[receiver] = set()
    address_mapping[receiver].add(sender)

def dfs(address, visited, current_group):
    visited.add(address)
    current_group.add(address)
    for neighbor in address_mapping[address]:
        if neighbor not in visited:
            dfs(neighbor, visited, current_group)
    return current_group

visited = set()
groups = []

for address in address_mapping:
    if address not in visited:
        current_group = dfs(address, visited, set())
        if len(current_group) >= 10:
            groups.append(current_group)

output = []
for group in groups:
    if len(group) > 1:
        output.append(' <-> '.join(group))
    else:
        output.append(next(iter(group)))

output_df = pd.DataFrame(output, columns=["Large Connected Groups"])
output_df.to_csv(r"D:\sybil\gnosis_tokentx_large_connected_groups.csv", index=False)

print("success")