import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import re

# Load the CSV file
data_all_groups = pd.read_csv("D:/sybil/gnosis_txlist_token_transfers_per_group.csv")  # Replace with your actual path

pattern = r'from:\s*"(?P<from_address>0x[a-fA-F0-9]+)".*to:\s*"(?P<to_address>0x[a-fA-F0-9]+)"'

output_directory = "gnosis"
os.makedirs(output_directory, exist_ok=True)

def shorten_address(address):
    return address[:6] + '...' + address[-6:]

def scale_positions(pos, scale_factor):
    """Scale the positions of nodes to increase the gap between them."""
    for key in pos:
        pos[key] = tuple([i * scale_factor for i in pos[key]])
    return pos

def plot_graph_for_column(column, index):
    addresses = data_all_groups[column][1].split('<->')
    addresses = [address.strip() for address in addresses]
    G = nx.DiGraph()
    for address in addresses:
        G.add_node(address)
    for row in data_all_groups[column][2:]:
        if isinstance(row, str) and 'from' in row and 'to' in row:
            match = re.search(pattern, row)
            if match:
                from_address = match.group("from_address")
                to_address = match.group("to_address")
                if from_address in addresses and to_address in addresses:
                    G.add_edge(from_address, to_address)
    labels = {node: shorten_address(node) for node in G.nodes()}

    # Create a figure and axis with more control
    fig, ax = plt.subplots(figsize=(14, 10))

    # Check the number of addresses and adjust the layout accordingly
    if len(addresses) >= 30 and len(addresses) < 80:
        # Divide the addresses based on the given ratios
        first_len = int(len(addresses) * 2/10)
        second_len = int(len(addresses) * 3/10)
        third_len = len(addresses) - first_len - second_len
        shell1 = addresses[:first_len]
        shell2 = addresses[first_len: first_len + second_len]
        shell3 = addresses[first_len + second_len:]
        pos = nx.shell_layout(G, [shell1, shell2, shell3])
    elif len(addresses) >= 80 and len(addresses) < 100:
        first_len = int(len(addresses) * 1 / 10)
        second_len = int(len(addresses) * 2 / 10)
        third_len = int(len(addresses) * 2 / 10)
        fourth_len = int(len(addresses) * 2 / 10)
        fifth_len = len(addresses) - first_len - second_len - third_len - fourth_len
        shell1 = addresses[:first_len]
        shell2 = addresses[first_len: first_len + second_len]
        shell3 = addresses[first_len + second_len: first_len + second_len + third_len]
        shell4 = addresses[first_len + second_len + third_len: first_len + second_len + third_len + fourth_len]
        shell5 = addresses[first_len + second_len + third_len + fourth_len:]
        pos = nx.shell_layout(G, [shell1, shell2, shell3, shell4, shell5])
    elif len(addresses) >= 130:
        ratios = [5 / 100, 7 / 100, 9 / 100, 11 / 100, 13 / 100, 16 / 100, 18 / 100, 21 / 100]
        partitions = [int(len(addresses) * ratio) for ratio in ratios]

        # Ensure that all addresses are considered by adjusting the last partition
        partitions[-1] = len(addresses) - sum(partitions[:-1])

        # Create shells based on the partitions
        starts = [0] + [sum(partitions[:i]) for i in range(1, len(partitions))]
        shells = [addresses[starts[i]:starts[i] + partitions[i]] for i in range(len(partitions))]

        pos = nx.shell_layout(G, shells)
        # Adjust figure size and node positions for better visualization
        fig, ax = plt.subplots(figsize=(30, 30))  # Increase the figsize for addresses greater than 100
        scale_factor = 2  # Adjust this value as needed
        pos = scale_positions(pos, scale_factor)  # Scale the positions for addresses greater than 100

    else:
        pos = nx.shell_layout(G)

    nx.draw(G, pos, labels=labels, with_labels=True, node_size=3000, node_color="skyblue", font_size=12, width=2,
            edge_color="gray", arrowsize=20, arrowstyle='-|>', ax=ax)

    # Set the title on the axis, which should provide better control
    ax.set_title(f"Address Relationship for gnosis_txlist_group{index} with Shell Layout", fontsize=16, pad=20)

    output_path = os.path.join(output_directory, f"gnosis_txlist_group{index}.png")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

# Iterate over all columns and plot graphs
for idx, column in enumerate(data_all_groups.columns, 1):
    plot_graph_for_column(column, idx)
