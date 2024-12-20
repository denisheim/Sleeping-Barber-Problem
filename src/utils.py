import json
import os

class ConfigError(Exception):
    pass

class Config:
    """
    Responsible for loading and validating the simulation's configuration from a JSON file.

    The configuration file must include:
    - A 'barber_shop' section specifying parameters like the number of waiting chairs,
      arrival times, cutting times, and total number of customers.
    - A 'logging' section specifying at least the logging level (and optionally a log file).

    If any required section or parameter is missing or invalid, a ConfigError is raised.
    """

    def __init__(self, config_file):
        """
        Load and validate the configuration from the given file.

        Raises:
        - ConfigError if the file does not exist or is missing required keys.
        """
        if not os.path.exists(config_file):
            raise ConfigError(f"Config file {config_file} does not exist.")

        with open(config_file, 'r', encoding='utf-8') as f:
            self.config_data = json.load(f)

        self._validate_config()

    def _validate_config(self):
        """
        Checks for the presence and validity of all required keys in the configuration.
        Ensures 'barber_shop' and 'logging' sections are present and have correct data types.
        """
        if "barber_shop" not in self.config_data:
            raise ConfigError("Missing 'barber_shop' section.")

        bs = self.config_data["barber_shop"]
        required_keys = [
            "num_waiting_chairs",
            "customer_arrival_time_min",
            "customer_arrival_time_max",
            "barber_cut_time_min",
            "barber_cut_time_max",
            "total_customers"
        ]

        # All these values must be positive numbers (int or float)
        for k in required_keys:
            if k not in bs or not isinstance(bs[k], (int, float)) or bs[k] <= 0:
                raise ConfigError(f"Invalid or missing '{k}' in 'barber_shop' config.")

        if "logging" not in self.config_data:
            raise ConfigError("Missing 'logging' section in config.")

        log = self.config_data["logging"]
        if "log_level" not in log or not isinstance(log["log_level"], str):
            raise ConfigError("Invalid logging configuration. 'log_level' must be a string.")

    def get_barber_shop_config(self):
        """
        Returns the barber shop configuration dictionary.
        Contains keys like 'num_waiting_chairs', arrival/cut times, and total_customers.
        """
        return self.config_data["barber_shop"]

    def get_logging_config(self):
        """
        Returns the logging configuration dictionary.
        Typically includes 'log_level' and optionally 'log_file'.
        """
        return self.config_data["logging"]
