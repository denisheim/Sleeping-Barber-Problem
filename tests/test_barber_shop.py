import unittest
import time
from src.barber_shop import BarberShop
from src.barber import Barber
from src.waiting_room import WaitingRoom


class MockLogger:
    def __init__(self):
        self.messages = []
    def info(self, msg):
        self.messages.append(msg)

class TestBarberShop(unittest.TestCase):
    def setUp(self):
        self.logger = MockLogger()
        self.waiting_room = WaitingRoom(capacity=2, logger=self.logger)
        self.barber = Barber(name="TestBarber", cut_time_min=0.01, cut_time_max=0.02, logger=self.logger)
        self.shop = BarberShop(barber=self.barber, waiting_room=self.waiting_room, logger=self.logger)

    def test_open_and_stop(self):
        self.shop.open_shop()
        time.sleep(0.1)
        self.shop.stop_shop()
        self.assertIn("Opening The barber shop is now open.", self.logger.messages)
        self.assertIn("Closing The barber shop is closing.", self.logger.messages)

if __name__ == '__main__':
    unittest.main()
