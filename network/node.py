class Node:
    def __init__(self, name):
        self.name = name
        self.connections = []

    def connect(self, other_node):
        if other_node not in self.connections:
            self.connections.append(other_node)

    def __str__(self):
        return self.name