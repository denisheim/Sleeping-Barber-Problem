import time
import threading
import random
from typing import Optional, Dict
from utils import Config, ConfigError
from barber import Barber
from barber_shop import BarberShop
from waiting_room import WaitingRoom
from customer import Customer
from logger import AppLogger

class Simulation:
    """
    The core class managing the "Sleeping Barber" simulation.

    Responsibilities:
    - Load configuration parameters (e.g., number of chairs, arrival and cutting times).
    - Initialize the Barber, WaitingRoom, and BarberShop.
    - Start and stop the simulation upon user action.
    - Generate customers at random intervals based on configuration.
    - Monitor the simulation to determine when all customers are handled.
    - Record detailed timing information (arrival, start cutting, end cutting) to compute real statistics.
    """

    def __init__(self, config_file='config.json', logger: Optional[AppLogger] = None):
        """
        Initialize the simulation by loading the configuration and setting up all necessary components.

        Parameters:
        - config_file: Path to the JSON configuration file.
        - logger: Optional custom logger. If not provided, a default AppLogger is created.

        Raises:
        - Exception if configuration is invalid.
        """
        try:
            self.config = Config(config_file)
        except ConfigError as ce:
            raise Exception(f"Configuration error: {ce}")

        bs_conf = self.config.get_barber_shop_config()
        log_conf = self.config.get_logging_config()

        # Basic parameters from config
        self.num_waiting_chairs = int(bs_conf["num_waiting_chairs"])
        self.base_customer_arrival_min = float(bs_conf["customer_arrival_time_min"])
        self.base_customer_arrival_max = float(bs_conf["customer_arrival_time_max"])
        self.base_barber_cut_min = float(bs_conf["barber_cut_time_min"])
        self.base_barber_cut_max = float(bs_conf["barber_cut_time_max"])
        self.total_customers = int(bs_conf["total_customers"])

        # Initialize waiting room and barber without starting them yet
        self.waiting_room = WaitingRoom(capacity=self.num_waiting_chairs)
        self.barber = Barber(
            name="Barber",
            cut_time_min=self.base_barber_cut_min,
            cut_time_max=self.base_barber_cut_max
        )

        # Set up the logger
        if logger is None:
            self.logger = AppLogger(
                log_level=log_conf.get("log_level", "INFO"),
                log_file=log_conf.get("log_file")
            )
        else:
            self.logger = logger

        # Link logger to components
        self.barber.logger = self.logger
        self.waiting_room.logger = self.logger

        # Create the barber shop that orchestrates barber and waiting room interaction
        self.barber_shop = BarberShop(barber=self.barber, waiting_room=self.waiting_room, logger=self.logger)

        self.customers_generated = 0
        self.stop_event = threading.Event()  # Signals when we need to halt the simulation
        self.done = False                    # Set to True when all customers are handled

        # Timestamps for statistics:
        # arrival_times: when each customer arrived
        # start_times: when haircut started for each customer
        # end_times: when haircut ended for each customer
        self.arrival_times: Dict[str, float] = {}
        self.start_times: Dict[str, float] = {}
        self.end_times: Dict[str, float] = {}
        self.customers_left = 0  # Count how many customers could not wait (left due to full waiting room)

        # Give the barber a reference to this simulation so it can record cutting times
        self.barber.simulation = self

    def start_simulation(self):
        """
        Called once the user decides to run the simulation.
        Opens the barber shop and starts threads for customer generation and monitoring.
        """
        self.logger.info("Announcement Simulation started based on user action.")
        self.barber_shop.open_shop()

        # Thread to generate customers at random intervals
        customer_thread = threading.Thread(target=self.generate_customers, daemon=True)
        customer_thread.start()

        # Thread to monitor when all customers are done
        monitor_thread = threading.Thread(target=self.monitor, daemon=True)
        monitor_thread.start()

    def generate_customers(self):
        """
        Creates customers at random intervals.
        Each customer tries to enter the waiting room.
        If the room is full, they leave immediately (customers_left is incremented).
        If they can sit, they wait for the barber. If the barber is sleeping, we wake him up.
        """
        for i in range(self.total_customers):
            if self.stop_event.is_set():
                break
            # Random delay before the next customer arrives
            arrival_time = random.uniform(self.base_customer_arrival_min, self.base_customer_arrival_max)
            time.sleep(arrival_time)

            c = Customer(name=f"Customer_{i+1}", logger=self.logger)
            arrival_t = time.time()
            self.arrival_times[c.name] = arrival_t

            # Attempt to seat the customer
            if self.waiting_room.add_customer(c):
                # If barber is sleeping, we should wake him so he can attend to the queue
                self.barber.wake_up()
            else:
                # Waiting room full, customer leaves
                self.customers_left += 1

            self.customers_generated += 1

    def monitor(self):
        """
        Periodically checks if the simulation should end.
        The simulation ends when:
        - All customers have been generated,
        - No one is waiting in the waiting room,
        - The barber is not currently cutting anyone.

        When these conditions are met, we set 'done' to True.
        """
        while not self.stop_event.is_set():
            if (self.customers_generated >= self.total_customers
                and len(self.waiting_room) == 0
                and self.barber.current_customer is None):
                self.logger.info("Announcement All customers have been handled.")
                self.done = True
                break
            time.sleep(0.5)

    def record_start_cut(self, customer_name: str):
        """
        Called by the barber when haircut begins.
        Records the start timestamp for later stats calculation.
        """
        self.start_times[customer_name] = time.time()

    def record_end_cut(self, customer_name: str):
        """
        Called by the barber when haircut ends.
        Records the end timestamp for stats calculation.
        """
        self.end_times[customer_name] = time.time()

    def stop(self):
        """
        Stops the simulation gracefully:
        - Sets the stop event to halt customer generation and monitoring.
        - Closes the barber shop.
        - Logs the stopping action.
        """
        self.logger.info("Stopping the simulation...")
        self.stop_event.set()
        self.barber_shop.stop_shop()
        self.logger.info("Simulation stopped.")

    def is_done(self):
        """
        Returns True if all customers have been handled and the simulation is complete.
        """
        return self.done

    def compute_real_stats(self):
        """
        Computes statistics from recorded times:
        - avg_wait: Average waiting time before haircut starts (start - arrival)
        - avg_cut: Average cutting time (end - start)
        - served_count: Number of customers actually served
        - left_count: Number of customers who left due to no space
        - waiting_count: How many are still waiting (should be zero if done)

        Returns a dictionary with these metrics.
        """
        served_customers = set(self.start_times.keys()) & set(self.end_times.keys()) & set(self.arrival_times.keys())
        if not served_customers:
            return {
                "avg_wait": None,
                "avg_cut": None,
                "served_count": 0,
                "left_count": self.customers_left,
                "waiting_count": len(self.waiting_room)
            }

        wait_times = [(self.start_times[c] - self.arrival_times[c]) for c in served_customers]
        cut_times = [(self.end_times[c] - self.start_times[c]) for c in served_customers]

        avg_wait = sum(wait_times) / len(wait_times) if wait_times else None
        avg_cut = sum(cut_times) / len(cut_times) if cut_times else None

        return {
            "avg_wait": avg_wait,
            "avg_cut": avg_cut,
            "served_count": len(served_customers),
            "left_count": self.customers_left,
            "waiting_count": len(self.waiting_room)
        }
