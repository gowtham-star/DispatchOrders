class Order:
    """
    Represents an order in the kitchen.

    Attributes:
        order_id (int): The unique identifier for the order.
        name (str): The name of the order.
        prep_time (int): The preparation time required for the order in seconds.
        ready_time (float): The time when the order is ready.
        courier_id (int): The ID of the courier assigned to this order (for matched strategy).
    """
    def __init__(self, order_id, name, prep_time):
        self.order_id = order_id
        self.name = name
        self.prep_time = prep_time
        self.ready_time = None
        self.courier_id = None
