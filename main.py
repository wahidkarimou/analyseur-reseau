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

# III. File d'attente
queue = QueueManager()
queue.add_packet(p1)
queue.add_packet(p2)
queue.add_packet(p3)

# IV. Simulation
simulator = Simulator(graph, queue)
simulator.run()