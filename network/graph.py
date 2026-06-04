from network.node import Node

class Graph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, name):
        if name not in self.nodes:
            self.nodes[name] = Node(name)
        else:
            print(f"❌Le noeud {name} existe déjà !")

    def add_connection(self, node_a, node_b):
        if node_a in self.nodes and node_b in self.nodes:
            self.nodes[node_a].connect(self.nodes[node_b])
            self.nodes[node_b].connect(self.nodes[node_a])
        else:
            if node_a not in self.nodes:
                print (f"❌Le noeud {node_a} n'exixte pas !")
                
            if node_b not in self.nodes:
                print (f"❌Le noeud {node_b} n'exixte pas !")

    def send_packet(self, node_a, node_b, packet):
        if node_a in self.nodes and node_b in self.nodes:
            self.nodes[node_b].receive_packet(packet)
        else:
            if node_a not in self.nodes:
                print (f"❌Le noeud {node_a} n'existe pas !")
            
            if node_b not in self.nodes:
                print (f"❌Le noeud {node_b} n'existe pas !")

    def display(self):
        for name, node in self.nodes.items():
            print(f"{name} -> {[n.name for n in node.connections]}")