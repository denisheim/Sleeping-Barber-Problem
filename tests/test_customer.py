import unittest
from src.customer import Customer

class TestCustomer(unittest.TestCase):
    def test_init(self):
        c = Customer("C1")
        self.assertEqual(c.name, "C1")

    def test_repr(self):
        c = Customer("C2")
        self.assertEqual(repr(c), "Customer(name=C2)")

if __name__ == '__main__':
    unittest.main()
