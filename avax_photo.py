import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import re

# Load the CSV data
data_all_groups = pd.read_csv("D:/sybil/avax_txlist_token_transfers_per_group.csv")

pattern = r'from:\s*"(?P<from_address>0x[a-fA-F0-9]+)".*to:\s*"(?P<to_address>0x[a-fA-F0-9]+)"'
output_directory = "avax"
os.makedirs(output_directory, exist_ok=True)

def shorten_address(address):
    return address[:6] + '...' + address[-6:]

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

    pos = nx.shell_layout(G)
    nx.draw(G, pos, labels=labels, with_labels=True, node_size=3000, node_color="skyblue", font_size=12, width=2,
            edge_color="gray", arrowsize=20, arrowstyle='-|>', ax=ax)

    # Set the title on the axis, which should provide better control
    ax.set_title(f"Address Relationship for avax__txlist_group{index} with Shell Layout", fontsize=16, pad=20)

    output_path = os.path.join(output_directory, f"avax_txlist_group{index}.png")
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

# Iterate over all columns and plot graphs
for idx, column in enumerate(data_all_groups.columns, 1):
    plot_graph_for_column(column, idx)
