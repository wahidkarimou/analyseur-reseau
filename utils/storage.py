import json
import os

FICHIER = "reseau.json"

def sauvegarder(graph):
    """Sauvegarde les noeuds et connexions dans reseau.json"""
    data = {
        "noeuds": list(graph.nodes.keys()),
        "connexions": [
            [a, b]
            for a, node in graph.nodes.items()
            for b in [n.name for n in node.connections]
            if a < b  # evite les doublons A-B et B-A
        ]
    }
    with open(FICHIER, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Réseau sauvegardé dans {FICHIER}")

def charger(graph, nx_graph):
    """Charge les noeuds et connexions depuis reseau.json"""
    if not os.path.exists(FICHIER):
        return False
    with open(FICHIER, "r") as f:
        data = json.load(f)
    for noeud in data["noeuds"]:
        if noeud not in graph.nodes:
            graph.add_node(noeud)
            nx_graph.add_node(noeud)
    for a, b in data["connexions"]:
        graph.add_connection(a, b)
        nx_graph.add_edge(a, b)
        nx_graph.add_edge(b, a)
    return True