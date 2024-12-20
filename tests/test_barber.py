import unittest
from src.barber import Barber
from src.customer import Customer

class MockLogger:
    def __init__(self):
        self.messages = []
    def info(self, msg):
        self.messages.append(("INFO", msg))

class TestBarber(unittest.TestCase):
    def setUp(self):
        self.logger = MockLogger()
        self.barber = Barber(name="TestBarber", cut_time_min=0.1, cut_time_max=0.2, logger=self.logger)

    def test_initial_state(self):
        self.assertTrue(self.barber.is_sleeping)
        self.assertIsNone(self.barber.current_customer)

    def test_wake_up(self):
        self.barber.wake_up()
        self.assertFalse(self.barber.is_sleeping)
        self.assertIn(("INFO", "Barber TestBarber is awakened."), self.logger.messages)

    def test_sleep(self):
        self.barber.is_sleeping = False
        self.barber.sleep()
        self.assertTrue(self.barber.is_sleeping)

    def test_cut_hair(self):
        cust = Customer(name="Cust1")
        self.barber.cut_hair(cust)
        self.assertIsNone(self.barber.current_customer)
        start_msg = any("is cutting Cust1's hair" in m[1] for m in self.logger.messages)
        end_msg = any("finished cutting Cust1's hair" in m[1] for m in self.logger.messages)
        self.assertTrue(start_msg)
        self.assertTrue(end_msg)

    def test_stop(self):
        self.barber.stop()
        self.assertTrue(self.barber._stop_event.is_set())

if __name__ == '__main__':
    unittest.main()
