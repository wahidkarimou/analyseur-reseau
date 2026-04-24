from network.graph import Graph
from network.packet import Packet
from simulation.queue_manager import QueueManager
from simulation.simulator import Simulator

# I. Création du réseau
graph = Graph()

graph.add_node("A")
graph.add_node("B")
graph.add_node("C")

graph.add_connection("A", "B")
graph.add_connection("B", "C")

print("Structure du réseau :")
graph.display()

# II. Création des paquets
p1 = Packet(1, "A", "B", 10)
p2 = Packet(2, "A", "C", 20)
p3 = Packet(3, "B", "C", 5)

# III. File d'attente (avec capacité limitée)
queue = QueueManager(capacity=2)

# Création des paquets (liste)
packets = [
    Packet(1, "A", "B", 10),
    Packet(2, "A", "C", 20),
    Packet(3, "B", "C", 5),
    Packet(4, "C", "A", 15),
]

# Ajout dans la file
for p in packets:
    queue.add_packet(p)

# IV. Simulation
simulator = Simulator(graph, queue)
simulator.run()