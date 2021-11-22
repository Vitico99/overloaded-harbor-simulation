# A simple priority queue
import heapq

class PQueue:
    def __init__(self) -> None:
        self.q = []

    def insert(self, x):
        heapq.heappush(self.q, x)
    
    def min(self):
        if self.q:
            return self.q[0]
        return float('+inf'), float('+inf')
    
    def pop(self):
        if self.q:
            return heapq.heappop(self.q)
        return float('+inf'), float('+inf')

    def len(self):
        return len(self.q)