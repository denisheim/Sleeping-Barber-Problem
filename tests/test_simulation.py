import unittest
import time
import json
import os
from src.simulation import Simulation

class MockLogger:
    def __init__(self):
        self.messages = []
    def info(self, msg):
        self.messages.append(("INFO", msg))

class TestSimulation(unittest.TestCase):
    def setUp(self):
        self.config_data = {
            "barber_shop": {
                "num_waiting_chairs": 2,
                "customer_arrival_time_min": 0.1,
                "customer_arrival_time_max": 0.2,
                "barber_cut_time_min": 0.05,
                "barber_cut_time_max": 0.1,
                "total_customers": 3
            },
            "logging": {
                "log_level": "INFO"
            }
        }
        self.config_file = "test_sim_config.json"
        with open(self.config_file, 'w') as f:
            json.dump(self.config_data, f)
        self.logger = MockLogger()
        self.sim = Simulation(config_file=self.config_file, logger=self.logger)

    def tearDown(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

    def test_initial_state(self):
        self.assertEqual(self.sim.num_waiting_chairs, 2)
        self.assertEqual(self.sim.total_customers, 3)
        self.assertFalse(self.sim.is_done())

    def test_run_simulation(self):
        self.sim.start_simulation()
        while not self.sim.is_done():
            time.sleep(0.1)
        stats = self.sim.compute_real_stats()
        served = stats["served_count"]
        left = stats["left_count"]
        self.assertEqual(served + left, self.sim.total_customers)

    def test_stop_simulation(self):
        self.sim.start_simulation()
        time.sleep(0.1)
        self.sim.stop()
        self.assertTrue(self.sim.stop_event.is_set())

if __name__ == '__main__':
    unittest.main()
