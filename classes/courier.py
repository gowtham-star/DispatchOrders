class Courier:
    """
    Represents a courier in the kitchen dispatch system.

    Attributes:
        courier_id (int): The unique identifier for the courier.
        arrival_time (float): The time when the courier arrives at the kitchen.
        order_id (int): The ID of the order assigned to this courier (for matched strategy).
    """
    def __init__(self, courier_id):
        self.courier_id = courier_id
        self.arrival_time = None
        self.order_id = None
