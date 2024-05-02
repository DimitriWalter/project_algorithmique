import random
import networkx as nx
import matplotlib.pyplot as plt

# Définition des constantes
nombre_noeud_tier1 = 10
nombre_noeud_tier2 = 20
nombre_noeud_tier3 = 70
nombre_noeud_total = nombre_noeud_tier1 + nombre_noeud_tier2 + nombre_noeud_tier3

class Reseau:
    """
    Classe qui crée le réseau des 100 noeuds avec leurs paliers (tier) et leurs liens
    """
    def __init__(self):
        self.noeuds = self.creer_reseau()
        self.table_routage = self.calculer_table_routage()

    def creer_reseau(self):
        # Création des noeuds
        noeuds = [{"tier": 1, "liens": []} for _ in range(nombre_noeud_tier1)]
        noeuds += [{"tier": 2, "liens": []} for _ in range(nombre_noeud_tier2)]
        noeuds += [{"tier": 3, "liens": []} for _ in range(nombre_noeud_tier3)]

        # Création des liens pour le backbone (Tier 1)
        for i in range(nombre_noeud_tier1):
            for j in range(i + 1, nombre_noeud_tier1):
                if random.random() < 0.75: # Vérifie si nous sommes dans les 75% de chance de créer un lien entre i et j
                    poids = random.randint(5, 10)
                    # Dans la liste, qui est la valeur de la clé 'liens', est ajoutée un tuple pour indiquer le noeud avec lequel le lien existe ainsi le poid du lien
                    noeuds[i]["liens"].append((j, poids))
                    noeuds[j]["liens"].append((i, poids))

        # Création des liens pour les opérateurs de transit (Tier 2)
        debut_tier2 = nombre_noeud_tier1
        fin_tier2 = nombre_noeud_tier1 + nombre_noeud_tier2
        for i in range(debut_tier2, fin_tier2):
            tier1_liens = random.sample(range(nombre_noeud_tier1), random.randint(1, 2)) # Nombre de liens qu'aura un noeud du tier2 avec un/des noeud(s) du tier1
            for noeud_tier1 in tier1_liens:
                poids = random.randint(10, 20)
                noeuds[i]["liens"].append((noeud_tier1, poids))
                noeuds[noeud_tier1]["liens"].append((i, poids))

            tier2_liens = random.sample(range(debut_tier2, fin_tier2), random.randint(2, 3)) # Nombre de liens qu'aura un noeud du tier2 avec un/des noeud(s) du tier2
            for noeud_tier2 in tier2_liens:
                if noeud_tier2 != i:
                    poids = random.randint(10, 20)
                    noeuds[i]["liens"].append((noeud_tier2, poids))
                    noeuds[noeud_tier2]["liens"].append((i, poids))

        # Création des liens pour les opérateurs de niveau 3 (Tier 3)
        debut_tier3 = nombre_noeud_tier1 + nombre_noeud_tier2
        for i in range(debut_tier3, nombre_noeud_total):
            tier2_liens = random.sample(range(debut_tier2, fin_tier2), 2) # Liens qu'aura chaque noeud du tier3 avec 2 noeuds du tier2 
            for noeud_tier2 in tier2_liens:
                poids = random.randint(20, 50)
                noeuds[i]["liens"].append((noeud_tier2, poids))
                noeuds[noeud_tier2]["liens"].append((i, poids))

        return noeuds

    def parcours_largeur(self, noeud_depart):
        """
        Parcours en largeur pour vérifier si tous les noeuds sont accessibles à partir du noeud de départ.
        """
        visite = list() # Création d'une liste pour y mettre les noeuds qu'auront été parcouru
        file = [(noeud_depart, None)]  # (noeud, noeud parent)

        while file:
            noeud, parent = file.pop(0) # Récupère le premier noeud de la liste file
            if noeud not in visite:
                visite.append(noeud) # Marque le noeud en l'ajoutant dans la liste visite
                for voisin, poids in self.noeuds[noeud]["liens"]:
                    file.append((voisin, noeud)) # Ajoute les voisins dans la file

        # Si tous les noeuds ont été visités, le réseau est connexe et l"égalité ci-dessous est vrai
        return len(visite) == len(self.noeuds)

    def dijkstra(self, noeud_depart):
        """
        Algorithme de Dijkstra pour calculer les plus courts chemins
        à partir d"un noeud source vers tous les autres noeuds.
        """
        distances = {noeud: float("inf") for noeud in range(len(self.noeuds))} # Dictionnaire des distances min depuis le noeud de départ vers chaque autre noeud
        distances[noeud_depart] = 0 
        file_priorite = [(0, noeud_depart)] # Fil de priorités, noeud avec la plus petite distance
        prev = {noeud: None for noeud in range(len(self.noeuds))} # Dictionnaire des prédecesseur

        while file_priorite:
            distance_actuelle, noeud_actuelle = file_priorite.pop(0) # Récupére le noeud avec la distance la plus faible

            if distance_actuelle > distances[noeud_actuelle]:
                continue

            for voisin, poids in self.noeuds[noeud_actuelle]["liens"]: # Parcours les voisins du noeuds actuels
                distance = distance_actuelle + poids
                if distance < distances[voisin]:
                    distances[voisin] = distance
                    prev[voisin] = noeud_actuelle
                    file_priorite.append((distance, voisin)) # Ajoute le voisin dans la fil de priorité

        return prev, distances

    def calculer_table_routage(self):
        """
        Calcule les tables de routage pour chaque noeud en utilisant l'algorithme de Dijkstra.
        """
        table_routage = [{} for _ in range(len(self.noeuds))] # Initialisation d'une liste de dictionnaires pour stocker les tables de routage pour chaque noeud

        for noeud in range(len(self.noeuds)): 
            prev, distances = self.dijkstra(noeud) # Récupére le tableau des prédécesseurs et le tableau des distances à partir de Dijkstra
            # Pour chaque destination, détermine le prochain saut
            for destination in range(len(self.noeuds)):
                if destination != noeud and distances[destination] != float("inf"): # Ignore le cas où la destination est le noeud lui-même ou n'est pas atteignable
                    prochain_saut = prev[destination] # Trouve le premier saut pour atteindre la destination à partir du noeud courant
                    table_routage[noeud][destination] = prochain_saut # Stocke le prochain saut dans la table de routage pour le noeud courant

        return table_routage

    def reconstruire_chemin(self, source, destination):
        """
        Reconstitue le chemin entre deux noeuds en utilisant les tables de routage.
        """
        chemin = [destination] # Initialise une liste pour stocker le chemin, en commençant par la destination
        noeud_actuel = destination
        while noeud_actuel != source: # Tant que nous n'avons pas atteint la source, remonte le chemin
            prochain_saut = self.table_routage[source][noeud_actuel] # Trouve le prochain saut à partir de la source vers le noeud actuel
            chemin.append(prochain_saut) # Ajoute le prochain saut au chemin
            noeud_actuel = prochain_saut #Met à jour noeud_actuel
        chemin.reverse() # Inverse le chemin pour obtenir l'ordre correct, de la source à la destination
        return chemin


class ReseauGraphique(Reseau):
    def __init__(self):
        super().__init__()

    def afficher(self, chemin=None):
        """
        Fonction qui affiche le graphe sur le graphique avec où sans le chemin à afficher
        """
        G = nx.Graph() # Création du graphe vide à l'aide de networkx
        positions = {} # Création du dictionnaire des positions des noeuds dans le graphique

        for numero_noeud, dico in enumerate(self.noeuds): # Parcourt de chaque noeuds et dictionnaire du graphe
            # Ajout du noeud dans le graphe avec sa taille variant selon son palier
            G.add_node(numero_noeud, size=300 if dico["tier"] == 1 else 250 if dico["tier"] == 2 else 200) 
            positions[numero_noeud] = (random.random(), random.random()) # Positionnement aléatoire du noeud

            for voisin, poids in dico["liens"]: # Parcourt du lien de chaque noeud
                G.add_edge(numero_noeud, voisin, poids=poids) # Ajout du lien entre le noeud et chacun de ses voisins

        # Création de la liste des couleurs en fonction du palier, et la liste des tailles de chaque noeuds 
        couleurs_noeuds = ["blue" if self.noeuds[noeud]["tier"] == 1 else "red" if self.noeuds[noeud]["tier"] == 2 else "green" for noeud in G.nodes()]
        taille_noeuds = [G.nodes[noeud]["size"] for noeud in G.nodes()]
        nx.draw(G, pos=positions, with_labels=True, node_color=couleurs_noeuds, node_size=taille_noeuds) # Dessin du noeud sur le graphique

        largeur_bordures = [0.5 + 0.2 * (G[u][v]["poids"] - 5) / 5 for u, v in G.edges()] # Changement de l'épaisseur des liens en fonction de la valeur
        nx.draw_networkx_edges(G, pos=positions, width=largeur_bordures, edge_color="black") # Dessin de chaque lien

        if chemin: # Si il y a un chemin à afficher
            liens = [(chemin[i], chemin[i+1]) for i in range(len(chemin)-1)] # Création de la liste de chaque tuples de noeuds liés
            epaisseur_chemin = 3
            nx.draw_networkx_edges(G, pos=positions, edgelist=liens, edge_color="yellow", width=epaisseur_chemin) # Dessin du chemin séléctionné en rouge

        plt.legend([plt.Line2D([0], [0], color="blue", lw=4), plt.Line2D([0], [0], color="red", lw=4), plt.Line2D([0], [0], color="green", lw=4)],
                   ["Tier 1", "Tier 2", "Tier 3"], loc="upper left") # Création de la légende du graphique

        def clic_noeud(event):
            """
            Fonction qui permet d'afficher tous les liens du noeud cliqué
            """
            if event.inaxes is None: # Vérification si le clic est dans la zone du graphe
                return
            for noeud in G.nodes(): # Parcourt de chaque noeud du graphe
                if (positions[noeud][0] - event.xdata)**2 + (positions[noeud][1] - event.ydata)**2 < 0.001: # Si la position du noeud est proche de la position du clic
                    # Création de la liste de chaque noeuds liés au noeud
                    liens_noeud = [self.noeuds[noeud]["liens"][i][0] for i in range(len(self.noeuds[noeud]["liens"]))]
                    print(f"Noeud : {noeud} | Liens : {liens_noeud}") # Affichage du noeud et de ses liens dans le terminal
                    print()

        plt.gcf().canvas.mpl_connect("button_press_event", clic_noeud) # Appelle de la fonction clic_noeud dès le clic du graphique

        plt.show() # Affichage du graphique

    def selectionner_noeuds(self):
        """
        Fonction qui permet de selectionner les noeuds source et destination
        """
        while True:
            try:
                source_noeud = int(input("Entrez le noeud source: "))
                if 0 <= source_noeud < len(self.noeuds):
                    break
                else:
                    print("Noeud source non existant, entrez un noeud du graphe.")
                    print()
            except ValueError:
                print("Noeud source incorrect, entrez un entier.")
                print()
        while True:
            try:
                destination_noeud = int(input("Entrez le noeud de destination: "))
                if 0 <= destination_noeud < len(self.noeuds):
                    break
                else:
                    print("Noeud de destination non existant, entrez un noeud du graphe.")
                    print()
            except ValueError:
                print("Noeud de destination incorrect, entrez un entier.")
                print()

        return source_noeud, destination_noeud


def main():
    reseau = Reseau() # Création d'une instance Reseau qui contiendra touts les noeuds et la table de routage càd notre graphe
    noeud_depart = 0 # Premier noeud est le n°0
    connexe = reseau.parcours_largeur(noeud_depart) # On vérifie la connexité depuis le sommet de départ 

    print() # Tabulation
    while not connexe: # Tant que le graphe n'est pas connexe, on en recréé un...
        print("Le réseau n'est pas connexe. Création d'un nouveau réseau...")
        reseau = Reseau()
        connexe = reseau.parcours_largeur(noeud_depart)
    
    print("Le reseaux est connexe, on peut l'afficher: ") # Le test de connexité est passé, on peut afficher le graphe
    print()
    reseau_graphique = ReseauGraphique() # Création de l'interface graphique de notre graphe
    reseau_graphique.afficher() # Affichage du graphe

    while True: # Tant que l'utilisateur le souhaite, il peut regarder le chemin entre 2 noeuds
        source_noeud, destination_noeud = reseau_graphique.selectionner_noeuds() # On sélectionne 2 noeuds 
        chemin = reseau_graphique.reconstruire_chemin(source_noeud, destination_noeud) # On construit le chemin
        print(f"Chemin de {source_noeud} à {destination_noeud} : {' -> '.join(map(str, chemin))}")
        print()
        reseau_graphique.afficher(chemin) # On affiche le graphe avec le chemin surligné en rouge
        reponse = str(input("Voulez-vous observer le chemin entre 2 autres noeuds? (oui/non) "))
        print()
        if reponse == "oui":
            continue
        else:
            break


if __name__ == "__main__":
    main()