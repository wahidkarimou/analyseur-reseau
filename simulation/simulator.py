import time

class Simulator:
    def __init__(self, graph, queue_manager):
        self.graph = graph
        self.queue_manager = queue_manager

    def run(self):
        print("\n🚀 Simulation en cours...\n")

        while not self.queue_manager.is_empty():
            self.queue_manager.process_packet()
            time.sleep(1)

        print("\n✅ Simulation terminée.")

        stats = self.queue_manager.stats()
        print("\n📊 Statistiques :")
        print(f"Paquets restants : {stats['restants']}")
        print(f"Paquets perdus : {stats['perdus']}")