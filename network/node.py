from collections import deque

class Node:
    def __init__(self, name, capacity=10):
        self.name = name
        self.connections = []
        self.queue = deque()
        self.capacity = capacity

    def connect(self, other_node):
        if other_node not in self.connections:
            self.connections.append(other_node)

    def receive_packet(self,packet):
        if len(self.queue) < self.capacity:
            self.queue.append(packet)
            return True
        else:
            print(f" Goulot détecté sur {self.name} !")
            return False

    def send_packet(self):
        if self.queue:
            return self.queue.popleft()
        return None

    def __str__(self):
        return self.name