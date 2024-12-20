class Customer:
    """
    Represents a single customer with a name.
    Used for identification and logging.
    """
    def __init__(self, name, logger=None):
        self.name = name
        self.logger = logger

    def __repr__(self):
        return f"Customer(name={self.name})"
