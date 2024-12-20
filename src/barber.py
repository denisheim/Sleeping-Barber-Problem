import time
import threading
import random

class Barber:
    """
    Represents the barber who can sleep if no customers are available,
    and cut hair if there is a customer ready.
    """

    def __init__(self, name, cut_time_min, cut_time_max, logger=None):
        self.name = name
        self.cut_time_min = cut_time_min
        self.cut_time_max = cut_time_max
        self.is_sleeping = True
        self.current_customer = None
        self.logger = logger
        self._stop_event = threading.Event()
        self.condition = threading.Condition()
        self.simulation = None  # Will be set from simulation.py so barber can record start/end of cutting

    def stop(self):
        """
        Stops the barber's activity.
        """
        self._stop_event.set()
        with self.condition:
            self.condition.notify_all()

    def wake_up(self):
        """
        Wakes the barber if he is sleeping.
        """
        if self.is_sleeping:
            self.is_sleeping = False
            if self.logger:
                self.logger.info(f"Barber {self.name} is awakened.")
            with self.condition:
                self.condition.notify_all()

    def sleep(self):
        """
        Puts the barber to sleep if no customers are waiting.
        """
        if not self.is_sleeping:
            self.is_sleeping = True
            if self.logger:
                self.logger.info(f"Barber {self.name} goes to sleep.")

    def cut_hair(self, customer):
        """
        Handles the process of cutting a customer's hair.
        Sets current_customer first, logs the event, and if a simulation is set,
        records the start and end cutting times.
        """
        # Set current_customer before logging and record times,
        # so the UI sees that the barber is actually busy.
        self.current_customer = customer

        # If simulation is available, record start of cutting
        if self.simulation:
            self.simulation.record_start_cut(customer.name)

        cut_time = random.uniform(self.cut_time_min, self.cut_time_max)
        if self.logger:
            self.logger.info(f"Barber {self.name} is cutting {customer.name}'s hair for {cut_time:.2f}s.")

        # Simulate cutting
        time.sleep(cut_time)

        if self.logger:
            self.logger.info(f"Barber {self.name} finished cutting {customer.name}'s hair.")

        # If simulation is available, record end of cutting
        if self.simulation:
            self.simulation.record_end_cut(customer.name)

        # After finishing, no current customer
        self.current_customer = None
