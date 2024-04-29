import random
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque, defaultdict
import heapq

# Définition des constantes
NUM_TIER1_NODES = 10
NUM_TIER2_NODES = 20
NUM_TIER3_NODES = 70
TOTAL_NODES = NUM_TIER1_NODES + NUM_TIER2_NODES + NUM_TIER3_NODES

class Network:
    def __init__(self):
        self.nodes = self.create_network()
        self.routing_tables = self.calculate_routing_tables()

    def create_network(self):
        # Création des nœuds
        nodes = [{'tier': 1, 'connections': []} for _ in range(NUM_TIER1_NODES)]
        nodes += [{'tier': 2, 'connections': []} for _ in range(NUM_TIER2_NODES)]
        nodes += [{'tier': 3, 'connections': []} for _ in range(NUM_TIER3_NODES)]

        # Création des liens pour le backbone (Tier 1)
        for i in range(NUM_TIER1_NODES):
            for j in range(i + 1, NUM_TIER1_NODES):
                if random.random() < 0.75:
                    weight = random.randint(5, 10)
                    nodes[i]['connections'].append((j, weight))
                    nodes[j]['connections'].append((i, weight))

        # Création des liens pour les opérateurs de niveau 2 (Tier 2)
        tier2_start = NUM_TIER1_NODES
        tier2_end = NUM_TIER1_NODES + NUM_TIER2_NODES
        for i in range(tier2_start, tier2_end):
            tier1_connections = random.sample(range(NUM_TIER1_NODES), random.randint(1, 2))
            for tier1_node in tier1_connections:
                weight = random.randint(10, 20)
                nodes[i]['connections'].append((tier1_node, weight))
                nodes[tier1_node]['connections'].append((i, weight))

            tier2_connections = random.sample(range(tier2_start, tier2_end), random.randint(2, 3))
            for tier2_node in tier2_connections:
                if tier2_node != i:
                    weight = random.randint(10, 20)
                    nodes[i]['connections'].append((tier2_node, weight))
                    nodes[tier2_node]['connections'].append((i, weight))

        # Création des liens pour les opérateurs de niveau 3 (Tier 3)
        tier3_start = NUM_TIER1_NODES + NUM_TIER2_NODES
        for i in range(tier3_start, TOTAL_NODES):
            tier2_connections = random.sample(range(tier2_start, tier2_end), 2)
            for tier2_node in tier2_connections:
                weight = random.randint(20, 50)
                nodes[i]['connections'].append((tier2_node, weight))
                nodes[tier2_node]['connections'].append((i, weight))

        return nodes

    def bfs(self, start_node):
        """
        Parcours en largeur (BFS) pour vérifier si tous les nœuds sont accessibles
        à partir du nœud de départ.
        """
        visited = set()
        queue = [(start_node, None)]  # (nœud, nœud parent)

        while queue:
            node, parent = queue.pop(0)
            if node not in visited:
                visited.add(node)
                for neighbor, weight in self.nodes[node]['connections']:
                    queue.append((neighbor, node))

        # Si tous les nœuds ont été visités, le réseau est connexe
        return len(visited) == len(self.nodes)

    def dijkstra(self, start_node):
        """
        Algorithme de Dijkstra pour calculer les plus courts chemins
        à partir d'un nœud source vers tous les autres nœuds.
        """
        distances = {node: float('inf') for node in range(len(self.nodes))}
        distances[start_node] = 0
        pq = [(0, start_node)]
        prev = {node: None for node in range(len(self.nodes))}

        while pq:
            current_dist, current_node = heapq.heappop(pq)

            if current_dist > distances[current_node]:
                continue

            for neighbor, weight in self.nodes[current_node]['connections']:
                distance = current_dist + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    prev[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))

        return prev, distances

    def calculate_routing_tables(self):
        """
        Calcule les tables de routage pour chaque nœud en utilisant l'algorithme de Dijkstra.
        """
        routing_tables = [{} for _ in range(len(self.nodes))]

        for node in range(len(self.nodes)):
            prev, distances = self.dijkstra(node)
            for dest in range(len(self.nodes)):
                if dest != node and distances[dest] != float('inf'):
                    next_hop = prev[dest]
                    routing_tables[node][dest] = next_hop

        return routing_tables

    def reconstruct_path(self, source, destination):
        """
        Reconstitue le chemin entre deux nœuds en utilisant les tables de routage.
        """
        path = [destination]
        current_node = destination
        while current_node != source:
            next_hop = self.routing_tables[source][current_node]
            path.append(next_hop)
            current_node = next_hop
        path.reverse()
        return path

class VisualNetwork(Network):
    def __init__(self):
        super().__init__()

    def visualize(self):
        G = nx.Graph()
        positions = {}

        for node_idx, node in enumerate(self.nodes):
            G.add_node(node_idx, size=250 if node['tier'] == 1 else 200 if node['tier'] == 2 else 150)
            positions[node_idx] = (random.random(), random.random())

            for neighbor, weight in node['connections']:
                G.add_edge(node_idx, neighbor, weight=weight)

        node_colors = ['blue' if self.nodes[node]['tier'] == 1 else 'green' if self.nodes[node]['tier'] == 2 else 'orange' for node in G.nodes()]
        node_sizes = [G.nodes[node]['size'] for node in G.nodes()]
        nx.draw(G, pos=positions, with_labels=True, node_color=node_colors, node_size=node_sizes)

        # Ajuster l'épaisseur des liens en fonction de la valeur
        edge_widths = [0.5 + 0.2 * (G[u][v]['weight'] - 5) / 5 for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos=positions, width=edge_widths)

        plt.legend([plt.Line2D([0], [0], color='blue', lw=4), plt.Line2D([0], [0], color='green', lw=4), plt.Line2D([0], [0], color='orange', lw=4)],
                   ['Tier 1', 'Tier 2', 'Tier 3'], loc='upper left')

        plt.show()

    def select_nodes(self):
        while True:
            try:
                source_node = int(input("Enter the source node: "))
                if 0 <= source_node < len(self.nodes):
                    break
                else:
                    print("Source node out of range. Please enter a valid node.")
            except ValueError:
                print("Invalid input. Please enter an integer.")

        while True:
            try:
                dest_node = int(input("Enter the destination node: "))
                if 0 <= dest_node < len(self.nodes):
                    break
                else:
                    print("Destination node out of range. Please enter a valid node.")
            except ValueError:
                print("Invalid input. Please enter an integer.")

        return source_node, dest_node

    def visualize_path(self, path):
        G = nx.Graph()
        positions = {}

        for node_idx, node in enumerate(self.nodes):
            G.add_node(node_idx, size=250 if node['tier'] == 1 else 200 if node['tier'] == 2 else 150)
            positions[node_idx] = (random.random(), random.random())

            for neighbor, weight in node['connections']:
                G.add_edge(node_idx, neighbor, weight=weight)

        edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
        node_colors = ['blue' if self.nodes[node]['tier'] == 1 else 'green' if self.nodes[node]['tier'] == 2 else 'orange' for node in G.nodes()]
        node_sizes = [G.nodes[node]['size'] for node in G.nodes()]
        nx.draw(G, pos=positions, with_labels=True, node_color=node_colors, node_size=node_sizes)

        # Ajuster l'épaisseur des liens en fonction de la valeur
        edge_widths = [0.5 + 0.2 * (G[u][v]['weight'] - 5) / 5 for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos=positions, width=edge_widths)

        # Épaisseur du chemin sélectionné
        path_width = 3
        nx.draw_networkx_edges(G, pos=positions, edgelist=edges, edge_color='r', width=path_width)

        plt.legend([plt.Line2D([0], [0], color='blue', lw=4), plt.Line2D([0], [0], color='green', lw=4), plt.Line2D([0], [0], color='orange', lw=4)],
                   ['Tier 1', 'Tier 2', 'Tier 3'], loc='upper left')

        plt.show()

def main():
    visual_network = VisualNetwork()
    visual_network.visualize()

    # Select source and destination nodes
    source_node, dest_node = visual_network.select_nodes()

    # Reconstruct and visualize the path
    path = visual_network.reconstruct_path(source_node, dest_node)
    visual_network.visualize_path(path)

if __name__ == "__main__":
    main()