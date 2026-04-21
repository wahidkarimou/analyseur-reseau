class Simulator:
    def __init__(self, graph, queue_manager):
        self.graph = graph
        self.queue_manager = queue_manager

    def run(self):
        print("Simulation du trafic réseau...\n")

        while not self.queue_manager.is_empty():
            packet = self.queue_manager.process_packet()
            print(f"Traitement du paquet : {packet}")

        print("\nSimulation terminée.")