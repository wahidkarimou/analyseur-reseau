from collections import deque

class QueueManager:
    def __init__(self):
        self.queue = deque()

    def add_packet(self, packet):
        self.queue.append(packet)

    def process_packet(self):
        if self.queue:
            return self.queue.popleft()
        return None

    def is_empty(self):
        return len(self.queue) == 0