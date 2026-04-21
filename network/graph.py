from network.node import Node

class Graph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, name):
        self.nodes[name] = Node(name)

    def add_connection(self, node_a, node_b):
        self.nodes[node_a].connect(self.nodes[node_b])
        self.nodes[node_b].connect(self.nodes[node_a])

    def display(self):
        for name, node in self.nodes.items():
            print(f"{name} -> {[n.name for n in node.connections]}")