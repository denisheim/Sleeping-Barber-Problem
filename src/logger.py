import logging

class AppLogger:
    """
    A wrapper around Python's logging module that supports callback
    functions for UI updates. Each log message can be passed to a callback
    to be displayed in the UI.
    """
    def __init__(self, log_level="INFO", log_file=None, callback=None):
        self.logger = logging.getLogger("BarberShopLogger")
        self.logger.setLevel(log_level.upper())
        self.logger.handlers = []
        self.callback = callback

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        # Console handler: logs to stdout
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Optional file handler
        if log_file:
            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _handle_log_callback(self, msg):
        if self.callback:
            self.callback(msg)

    def info(self, msg):
        self.logger.info(msg)
        self._handle_log_callback(f"[INFO] {msg}")

    def warning(self, msg):
        self.logger.warning(msg)
        self._handle_log_callback(f"[WARNING] {msg}")

    def error(self, msg):
        self.logger.error(msg)
        self._handle_log_callback(f"[ERROR] {msg}")
