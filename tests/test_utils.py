import unittest
import os
import json
from src.utils import Config, ConfigError

class TestUtilsConfig(unittest.TestCase):
    def setUp(self):
        self.config_data = {
            "barber_shop": {
                "num_waiting_chairs": 3,
                "customer_arrival_time_min": 0.5,
                "customer_arrival_time_max": 1.0,
                "barber_cut_time_min": 1.0,
                "barber_cut_time_max": 2.0,
                "total_customers": 5
            },
            "logging": {
                "log_level": "INFO"
            }
        }
        self.config_file = "test_config.json"
        with open(self.config_file, 'w') as f:
            json.dump(self.config_data, f)

    def tearDown(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

    def test_valid_config(self):
        c = Config(self.config_file)
        bs = c.get_barber_shop_config()
        self.assertEqual(bs["num_waiting_chairs"], 3)

    def test_missing_file(self):
        with self.assertRaises(ConfigError):
            Config("no_such_file.json")

    def test_invalid_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({"logging": {"log_level": "INFO"}}, f)
        with self.assertRaises(ConfigError):
            Config(self.config_file)

if __name__ == '__main__':
    unittest.main()
