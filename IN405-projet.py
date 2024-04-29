import random as rd
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque, defaultdict
import heapq

# Définition des constantes
nombre_noeud_tier1 = 10
nombre_noeud_tier2 = 20
nombre_noeud_tier3 = 70
nombre_noeud_total = nombre_noeud_tier1 + nombre_noeud_tier2 + nombre_noeud_tier3


class Reseau:
    def __init__(self):
        self.noeuds = self.creer_reseau()
        self.table_routage = self.calculer_table_routage()

    def creer_reseau(self):
        # Création des noeuds
        noeuds = [{'tier': 1, 'connections': []} for _ in range(nombre_noeud_tier1)]
        noeuds += [{'tier': 2, 'connections': []} for _ in range(nombre_noeud_tier2)]
        noeuds += [{'tier': 3, 'connections': []} for _ in range(nombre_noeud_tier3)]

        # Création des liens pour le backbone (Tier 1)
        for i in range(nombre_noeud_tier1):
            for j in range(i + 1, nombre_noeud_tier1):
                if rd.random() < 0.75:
                    poids = rd.randint(5, 10)
                    noeuds[i]['connections'].append((j, poids))
                    noeuds[j]['connections'].append((i, poids))

        # Création des liens pour les opérateurs de niveau 2 (Tier 2)
        debut_tier2 = nombre_noeud_tier1
        fin_tier2 = nombre_noeud_tier1 + nombre_noeud_tier2
        for i in range(debut_tier2, fin_tier2):
            connections_tier1 = rd.sample(range(nombre_noeud_tier1), rd.randint(1, 2))
            for noeud_tier1 in connections_tier1:
                poids = rd.randint(10, 20)
                noeuds[i]['connections'].append((noeud_tier1, poids))
                noeuds[noeud_tier1]['connections'].append((i, poids))

            connections_tier2 = rd.sample(range(debut_tier2, fin_tier2), rd.randint(2, 3))
            for noeud_tier2 in connections_tier2:
                if noeud_tier2 != i:
                    poids = rd.randint(10, 20)
                    noeuds[i]['connections'].append((noeud_tier2, poids))
                    noeuds[noeud_tier2]['connections'].append((i, poids))

        # Création des liens pour les opérateurs de niveau 3 (Tier 3)
        debut_tier3 = nombre_noeud_tier1 + nombre_noeud_tier2
        for i in range(debut_tier3, nombre_noeud_total):
            connections_tier2 = rd.sample(range(debut_tier2, fin_tier2), 2)
            for noeud_tier2 in connections_tier2:
                poids = rd.randint(20, 50)
                noeuds[i]['connections'].append((noeud_tier2, poids))
                noeuds[noeud_tier2]['connections'].append((i, poids))

        return noeuds

    def bfs(self, noeud_depart):
        """
        Parcours en largeur (BFS) pour vérifier si tous les noeuds sont accessibles
        à partir du noeud de départ.
        """
        visite = set()
        file = [(noeud_depart, None)]  # (nœud, nœud parent)

        while file:
            noeud, parent = file.pop(0)
            if noeud not in visite:
                visite.add(noeud)
                for voisin, poids in self.noeuds[noeud]['connections']:
                    file.append((voisin, noeud))

        # Si tous les nœuds ont été visités, le réseau est connexe
        return len(visite) == len(self.noeuds)

    def dijkstra(self, noeud_depart):
        """
        Algorithme de Dijkstra pour calculer les plus courts chemins
        à partir d'un nœud source vers tous les autres nœuds.
        """
        distances = {noeud: float('inf') for noeud in range(len(self.noeuds))}
        distances[noeud_depart] = 0
        pq = [(0, noeud_depart)]
        prev = {noeud: None for noeud in range(len(self.noeuds))}

        while pq:
            distance_actuelle, noeud_actuel = heapq.heappop(pq)

            if distance_actuelle > distances[noeud_actuel]:
                continue

            for voisin, poids in self.noeuds[noeud_actuel]['connections']:
                distance = distance_actuelle + poids
                if distance < distances[voisin]:
                    distances[voisin] = distance
                    prev[voisin] = noeud_actuel
                    heapq.heappush(pq, (distance, voisin))

        return prev, distances

    def calculer_table_routage(self):
        """
        Calcule les tables de routage pour chaque noeud en utilisant l'algorithme de Dijkstra.
        """
        table_routage = [{} for _ in range(len(self.noeuds))]

        for noeud in range(len(self.noeuds)):
            prev, distances = self.dijkstra(noeud)
            for destination in range(len(self.noeuds)):
                if destination != noeud and distances[destination] != float('inf'):
                    prochain_saut = prev[destination]
                    table_routage[noeud][destination] = prochain_saut

        return table_routage

    def reconstruire_chemin(self, source, destination):
        """
        Reconstitue le chemin entre deux noeuds en utilisant les tables de routage
        """
        chemin = [destination]
        noeud_actuel = destination
        while noeud_actuel != source:
            prochain_saut = self.table_routage[source][noeud_actuel]
            chemin.append(prochain_saut)
            noeud_actuel = prochain_saut
        chemin.reverse()
        return chemin


class Reseau_graphique(Reseau):
    def __init__(self):
        super().__init__()

    def afficher(self):
        G = nx.Graph()
        positions = {}

        for noeud_idx, noeud in enumerate(self.noeuds):
            G.add_node(noeud_idx, size=250 if noeud['tier'] == 1 else 200 if noeud['tier'] == 2 else 150)
            positions[noeud_idx] = (rd.random(), rd.random())

            for voisin, poids in noeud['connections']:
                G.add_edge(noeud_idx, voisin, poids=poids)

        couleurs_noeuds = ['blue' if self.noeuds[noeud]['tier'] == 1 else 'green' if self.noeuds[noeud]['tier'] == 2 else 'orange' for noeud in G.nodes()]
        taille_noeuds = [G.nodes[noeud]['size'] for noeud in G.nodes()]
        nx.draw(G, pos=positions, with_labels=True, node_color=couleurs_noeuds, node_size=taille_noeuds)

        # Ajuster l'épaisseur des liens en fonction de la valeur
        largeur_bordures = [0.5 + 0.2 * (G[u][v]['poids'] - 5) / 5 for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos=positions, width=largeur_bordures)

        plt.legend([plt.Line2D([0], [0], color='blue', lw=4), plt.Line2D([0], [0], color='green', lw=4), plt.Line2D([0], [0], color='orange', lw=4)],
                   ['Tier 1', 'Tier 2', 'Tier 3'], loc='upper left')

        plt.show()

    def selectionner_noeuds(self):
        while True:
            try:
                source_noeud = int(input("Entrez le noeud source : "))
                if 0 <= source_noeud < len(self.noeuds):
                    break
                else:
                    print("Noeud source non existant, entrez un noeud du graphe")
            except ValueError:
                print("Noeud source incorrect, entrez un entier")

        while True:
            try:
                destination_noeud = int(input("Entrez le noeud de destination : "))
                if 0 <= destination_noeud < len(self.noeuds):
                    break
                else:
                    print("Noeud destination non existant, entrez un noeud du graphe")
            except ValueError:
                print("Noeud destination incorrect, entrez un entier")

        return source_noeud, destination_noeud

    def afficher_chemin(self, chemin):
        G = nx.Graph()
        positions = {}

        for noeud_idx, noeud in enumerate(self.noeuds):
            G.add_node(noeud_idx, size=250 if noeud['tier'] == 1 else 200 if noeud['tier'] == 2 else 150)
            positions[noeud_idx] = (rd.random(), rd.random())

            for voisin, poids in noeud['connections']:
                G.add_edge(noeud_idx, voisin, poids=poids)

        bordures = [(chemin[i], chemin[i+1]) for i in range(len(chemin)-1)]
        couleurs_noeuds = ['blue' if self.noeuds[noeud]['tier'] == 1 else 'green' if self.noeuds[noeud]['tier'] == 2 else 'orange' for noeud in G.nodes()]
        taille_noeuds = [G.nodes[noeud]['size'] for noeud in G.nodes()]
        nx.draw(G, pos=positions, with_labels=True, node_color=couleurs_noeuds, node_size=taille_noeuds)

        # Ajuster l'épaisseur des liens en fonction de la valeur
        largeur_bordures = [0.5 + 0.2 * (G[u][v]['poids'] - 5) / 5 for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos=positions, width=largeur_bordures)

        # Épaisseur du chemin sélectionné
        largeur_chemin = 3
        nx.draw_networkx_edges(G, pos=positions, edgelist=bordures, edge_color='r', width=largeur_chemin)

        plt.legend([plt.Line2D([0], [0], color='blue', lw=4), plt.Line2D([0], [0], color='green', lw=4), plt.Line2D([0], [0], color='orange', lw=4)],
                   ['Tier 1', 'Tier 2', 'Tier 3'], loc='upper left')

        plt.show()


def main():
    le_reseau_graphique = Reseau_graphique()
    le_reseau_graphique.afficher()

    # Selectionne le noeud source et destination
    source_noeud, destination_noeud = le_reseau_graphique.selectionner_noeuds()

    # Reconstruit et affiche le chemin
    chemin = le_reseau_graphique.reconstruire_chemin(source_noeud, destination_noeud)
    le_reseau_graphique.afficher_chemin(chemin)


if __name__ == "__main__":
    main()
