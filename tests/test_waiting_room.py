import unittest
from src.waiting_room import WaitingRoom
from src.customer import Customer

class MockLogger:
    def __init__(self):
        self.messages = []
    def info(self, msg):
        self.messages.append(msg)

class TestWaitingRoom(unittest.TestCase):
    def setUp(self):
        self.logger = MockLogger()
        self.room = WaitingRoom(capacity=2, logger=self.logger)

    def test_initial_state(self):
        self.assertEqual(len(self.room), 0)
        self.assertFalse(self.room.is_full())

    def test_add_customer(self):
        c1 = Customer("C1")
        res = self.room.add_customer(c1)
        self.assertTrue(res)
        self.assertEqual(len(self.room), 1)

    def test_full_room(self):
        self.room.add_customer(Customer("C1"))
        self.room.add_customer(Customer("C2"))
        self.assertTrue(self.room.is_full())
        res = self.room.add_customer(Customer("C3"))
        self.assertFalse(res)

    def test_get_next_customer(self):
        self.room.add_customer(Customer("C1"))
        self.room.add_customer(Customer("C2"))
        c = self.room.get_next_customer()
        self.assertEqual(c.name, "C1")
        self.assertEqual(len(self.room), 1)

if __name__ == '__main__':
    unittest.main()
