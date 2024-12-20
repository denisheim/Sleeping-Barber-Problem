import threading
from collections import deque

class WaitingRoom:
    """
    The waiting room holds customers waiting for the barber.
    It has a limited capacity.

    Customers who find it full leave immediately.
    """
    def __init__(self, capacity, logger=None):
        self.capacity = capacity
        self.logger = logger
        self.customers = deque()
        self.lock = threading.Lock()

    def is_full(self):
        with self.lock:
            return len(self.customers) >= self.capacity

    def add_customer(self, customer):
        """
        Attempts to add a customer to the waiting room.
        Returns True if successful, False if the room was full.
        """
        with self.lock:
            if len(self.customers) < self.capacity:
                self.customers.append(customer)
                if self.logger:
                    self.logger.info(f"Customer {customer.name} is waiting in the queue.")
                return True
            else:
                if self.logger:
                    self.logger.info(f"Room Waiting room is full. Customer {customer.name} leaves.")
                return False

    def get_next_customer(self):
        """
        Removes and returns the next customer from the queue (FIFO).
        Returns None if empty.
        """
        with self.lock:
            if self.customers:
                c = self.customers.popleft()
                if self.logger:
                    self.logger.info(f"Customer {c.name} is taken for a haircut.")
                return c
            return None

    def __len__(self):
        with self.lock:
            return len(self.customers)
