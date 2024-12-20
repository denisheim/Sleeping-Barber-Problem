import unittest
from src.logger import AppLogger

class TestLogger(unittest.TestCase):
    def setUp(self):
        self.received = []
        def callback(msg):
            self.received.append(msg)
        self.logger = AppLogger(log_level="INFO", callback=callback)

    def test_info_log(self):
        self.logger.info("Test info message")
        self.assertTrue(any("[INFO] Test info message" in r for r in self.received))

    def test_warning_log(self):
        self.logger.warning("Watch out!")
        self.assertTrue(any("[WARNING] Watch out!" in r for r in self.received))

    def test_error_log(self):
        self.logger.error("Something bad happened")
        self.assertTrue(any("[ERROR] Something bad happened" in r for r in self.received))

if __name__ == '__main__':
    unittest.main()
