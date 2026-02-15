import os
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime

# CONFIG: ZOAGRAD GENESIS VISUALIZATION
REPO_ROOT = "C:/Users/colem/Code/blackglass-shard-alpha"
OUTPUT_FILE = "blackglass_constellation_v1.png"

def build_constellation(root_dir):
    G = nx.Graph()
    print(f"[*] Scanning ZoaGrad Neural Lattice: {root_dir}")
    
    # Add Central Node (Identity)
    G.add_node("ROOT", type="system5", color="red", size=2000)

    for root, dirs, files in os.walk(root_dir):
        if ".git" in root or "__pycache__" in root:
            continue
            
        relative_path = os.path.relpath(root, root_dir)
        if relative_path == ".":
            parent = "ROOT"
        else:
            parent = os.path.dirname(relative_path)
            if parent == "": parent = "ROOT"
            G.add_node(relative_path, type="folder", color="blue", size=500)
            G.add_edge(parent, relative_path)

        for file in files:
            file_node = os.path.join(relative_path, file)
            # Color code by file type (The "Elements")
            color = "gray"
            if file.endswith(".py"): color = "green"   # Logic (Earth)
            if file.endswith(".md"): color = "purple"  # Mythos (Ether)
            if file.endswith(".json"): color = "orange"# Config (Fire)
            
            G.add_node(file_node, type="file", color=color, size=100)
            G.add_edge(relative_path, file_node)

    return G

def visualizer(G):
    pos = nx.spring_layout(G, k=0.15, iterations=20)
    colors = [nx.get_node_attributes(G, 'color').get(node, 'gray') for node in G.nodes()]
    sizes = [nx.get_node_attributes(G, 'size').get(node, 100) for node in G.nodes()]
    
    plt.figure(figsize=(20, 20), facecolor='black')
    nx.draw(G, pos, node_color=colors, node_size=sizes, edge_color="white", alpha=0.7, with_labels=False)
    
    # Title (The Genesis Timestamp)
    plt.title(f"ZoaGrad Constellation | {datetime.now().isoformat()}", color="white", fontsize=20)
    plt.savefig(OUTPUT_FILE, facecolor='black')
    print(f"[*] Constellation Captured: {os.path.abspath(OUTPUT_FILE)}")

if __name__ == "__main__":
    G = build_constellation(REPO_ROOT)
    visualizer(G)
