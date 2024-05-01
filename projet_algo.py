import random
import networkx as nx
import matplotlib.pyplot as plt
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
        # Création des nœuds
        noeuds = [{'tier': 1, 'connections': []} for _ in range(nombre_noeud_tier1)]
        noeuds += [{'tier': 2, 'connections': []} for _ in range(nombre_noeud_tier2)]
        noeuds += [{'tier': 3, 'connections': []} for _ in range(nombre_noeud_tier3)]

        # Création des liens pour le backbone (Tier 1)
        for i in range(nombre_noeud_tier1):
            for j in range(i + 1, nombre_noeud_tier1):
                if random.random() < 0.75:
                    poids = random.randint(5, 10)
                    noeuds[i]['connections'].append((j, poids))
                    noeuds[j]['connections'].append((i, poids))

        # Création des liens pour les opérateurs de niveau 2 (Tier 2)
        debut_tier2 = nombre_noeud_tier1
        fin_tier2 = nombre_noeud_tier1 + nombre_noeud_tier2
        for i in range(debut_tier2, fin_tier2):
            tier1_connections = random.sample(range(nombre_noeud_tier1), random.randint(1, 2))
            for noeud_tier1 in tier1_connections:
                poids = random.randint(10, 20)
                noeuds[i]['connections'].append((noeud_tier1, poids))
                noeuds[noeud_tier1]['connections'].append((i, poids))

            tier2_connections = random.sample(range(debut_tier2, fin_tier2), random.randint(2, 3))
            for noeud_tier2 in tier2_connections:
                if noeud_tier2 != i:
                    poids = random.randint(10, 20)
                    noeuds[i]['connections'].append((noeud_tier2, poids))
                    noeuds[noeud_tier2]['connections'].append((i, poids))

        # Création des liens pour les opérateurs de niveau 3 (Tier 3)
        debut_tier3 = nombre_noeud_tier1 + nombre_noeud_tier2
        for i in range(debut_tier3, nombre_noeud_total):
            tier2_connections = random.sample(range(debut_tier2, fin_tier2), 2)
            for noeud_tier2 in tier2_connections:
                poids = random.randint(20, 50)
                noeuds[i]['connections'].append((noeud_tier2, poids))
                noeuds[noeud_tier2]['connections'].append((i, poids))

        return noeuds

    def bfs(self, noeud_depart):
        """
        Parcours en largeur (BFS) pour vérifier si tous les nœuds sont accessibles
        à partir du nœud de départ.
        """
        visite = set()
        queue = [(noeud_depart, None)]  # (nœud, nœud parent)

        while queue:
            noeud, parent = queue.pop(0)
            if noeud not in visite:
                visite.add(noeud)
                for voisin, poids in self.noeuds[noeud]['connections']:
                    queue.append((voisin, noeud))

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
            distance_actuelle, noeud_actuelle = heapq.heappop(pq)

            if distance_actuelle > distances[noeud_actuelle]:
                continue

            for voisin, poids in self.noeuds[noeud_actuelle]['connections']:
                distance = distance_actuelle + poids
                if distance < distances[voisin]:
                    distances[voisin] = distance
                    prev[voisin] = noeud_actuelle
                    heapq.heappush(pq, (distance, voisin))

        return prev, distances

    def calculer_table_routage(self):
        """
        Calcule les tables de routage pour chaque nœud en utilisant l'algorithme de Dijkstra.
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
        Reconstitue le chemin entre deux nœuds en utilisant les tables de routage.
        """
        chemin = [destination]
        noeud_actuelle = destination
        while noeud_actuelle != source:
            prochain_saut = self.table_routage[source][noeud_actuelle]
            chemin.append(prochain_saut)
            noeud_actuelle = prochain_saut
        chemin.reverse()
        return chemin


class ReseauGraphique(Reseau):
    def __init__(self):
        super().__init__()

    def afficher(self, chemin=None):
        G = nx.Graph()
        positions = {}

        for noeud_idx, noeud in enumerate(self.noeuds):
            G.add_node(noeud_idx, size=250 if noeud['tier'] == 1 else 200 if noeud['tier'] == 2 else 150)
            positions[noeud_idx] = (random.random(), random.random())

            for voisin, poids in noeud['connections']:
                G.add_edge(noeud_idx, voisin, poids=poids)

        couleurs_noeuds = ['blue' if self.noeuds[noeud]['tier'] == 1 else 'green' if self.noeuds[noeud]['tier'] == 2 else 'orange' for noeud in G.nodes()]
        taille_noeuds = [G.nodes[noeud]['size'] for noeud in G.nodes()]
        nx.draw(G, pos=positions, with_labels=True, node_color=couleurs_noeuds, node_size=taille_noeuds)

        # Ajuster l'épaisseur des liens en fonction de la valeur
        largeur_bordures = [0.5 + 0.2 * (G[u][v]['poids'] - 5) / 5 for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos=positions, width=largeur_bordures)

        if chemin:
            liens = [(chemin[i], chemin[i+1]) for i in range(len(chemin)-1)]
            # Épaisseur du chemin sélectionné
            epaisseur_chemin = 3
            nx.draw_networkx_edges(G, pos=positions, edgelist=liens, edge_color='r', width=epaisseur_chemin)

        plt.legend([plt.Line2D([0], [0], color='blue', lw=4), plt.Line2D([0], [0], color='green', lw=4), plt.Line2D([0], [0], color='orange', lw=4)],
                   ['Tier 1', 'Tier 2', 'Tier 3'], loc='upper left')

        plt.show()

    def selectionner_noeuds(self):
        while True:
            try:
                source_noeud = int(input("Entrez le noeud source: "))
                if 0 <= source_noeud < len(self.noeuds):
                    break
                else:
                    print("Noeud source non existant, entrez un noeud du graphe.")
            except ValueError:
                print("Noeud source incorrect, entrez un entier.")

        while True:
            try:
                destination_noeud = int(input("Entrez le noeud de destination: "))
                if 0 <= destination_noeud < len(self.noeuds):
                    break
                else:
                    print("Noeud de destination non existant, entrez un noeud du graphe.")
            except ValueError:
                print("Noeud de destination incorrect, entrez un entier.")

        return source_noeud, destination_noeud


def main():
    reseau = Reseau()
    connexe = reseau.bfs(0)

    while not connexe:
        print("Le réseau n'est pas connexe. Création d'un nouveau réseau...")
        reseau = Reseau()
        connexe = reseau.bfs(0)
    print("Le reseaux est connexe, on peut l'afficher: ")  
    reseau_graphique = ReseauGraphique()
    reseau_graphique.afficher()

    source_noeud, destination_noeud = reseau_graphique.selectionner_noeuds()

   
    chemin = reseau_graphique.reconstruire_chemin(source_noeud, destination_noeud)
    print(f"Chemin de {source_noeud} à {destination_noeud} : {' -> '.join(map(str, chemin))}")
    reseau_graphique.afficher(chemin)
    

if __name__ == "__main__":
    main()