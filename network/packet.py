class Packet:
    def __init__(self, id_packet, source, destination, size):
        self.id_packet = id_packet
        self.source = source
        self.destination = destination
        self.size = size

    def __str__(self):
        return f"Packet {self.id_packet} | {self.source} -> {self.destination} ({self.size} KB)"