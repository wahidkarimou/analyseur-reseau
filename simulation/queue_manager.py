from collections import deque

class QueueManager:
    def __init__(self, capacity=2):
        self.queue = deque()
        self.capacity = capacity
        self.dropped_packets = 0  # paquets rejetés

    def add_packet(self, packet):
        if len(self.queue) >= self.capacity:
            print(f" Goulot d'étranglement ! Paquet rejeté : {packet}")
            self.dropped_packets += 1
        else:
            self.queue.append(packet)
            print(f"Ajout : {packet}")

    def process_packet(self):
        if self.queue:
            packet = self.queue.popleft()
            print(f"Traitement : {packet}")
            return packet
        return None

    def is_empty(self):
        return len(self.queue) == 0

    def stats(self):
        return {
            "restants": len(self.queue),
            "perdus": self.dropped_packets
        }