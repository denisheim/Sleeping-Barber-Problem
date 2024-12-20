import threading

class BarberShop:
    """
    Manages the interaction between the barber and the waiting room.
    A separate thread runs the barber's loop:
    - If a customer is available, barber cuts hair.
    - If not, barber sleeps until awakened.
    """
    def __init__(self, barber, waiting_room, logger=None):
        self.barber = barber
        self.waiting_room = waiting_room
        self.logger = logger
        self.stop_event = threading.Event()
        self.barber_thread = None

    def open_shop(self):
        """
        Starts the barber thread.
        """
        if self.logger:
            self.logger.info("Opening The barber shop is now open.")
        self.barber_thread = threading.Thread(target=self.run_barber, daemon=True)
        self.barber_thread.start()

    def run_barber(self):
        """
        Barber's main loop:
        Wait for customers, cut their hair, or sleep if none available.
        """
        while not self.stop_event.is_set():
            customer = self.waiting_room.get_next_customer()
            if customer is None:
                # No customer, barber sleeps.
                self.barber.sleep()
                with self.barber.condition:
                    self.barber.condition.wait(timeout=1.0)
            else:
                # Customer found, barber wakes up and cuts hair.
                self.barber.wake_up()
                self.barber.cut_hair(customer)

    def stop_shop(self):
        """
        Stops the barber shop (ends the barber thread).
        """
        if self.logger:
            self.logger.info("Closing The barber shop is closing.")
        self.stop_event.set()
        self.barber.stop()
        with self.barber.condition:
            self.barber.condition.notify_all()
        if self.barber_thread:
            self.barber_thread.join()
