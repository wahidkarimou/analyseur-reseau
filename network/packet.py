class Packet:
    def __init__(self, source, destination, size):
        self.source = source
        self.destination = destination
        self.size = size

    def __str__(self):
        return f"{self.source} -> {self.destination} ({self.size} KB)"