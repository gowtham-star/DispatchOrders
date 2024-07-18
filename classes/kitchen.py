import time
import threading
import logging
from queue import deque
from statistics import mean
from classes.strategy import DispatchStrategy, FIFODispatchStrategy, MatchedDispatchStrategy

class Kitchen:
    """
    Represents the kitchen where orders are prepared and dispatched to couriers.
    """

    def __init__(self, strategy: DispatchStrategy):
        self.orders = deque()  # Queue for orders
        self.couriers = deque()  # Queue for couriers
        self.strategy = strategy  # Dispatch strategy
        self.lock = threading.Lock()  # Lock for thread safety
        self.food_wait_times = []  # List to store food wait times
        self.courier_wait_times = []  # List to store courier wait times
        self.order_map = {}  # Map to store orders by ID
        self.courier_map = {}  # Map to store couriers by ID

    def receive_order(self, order):
        """
        Receives an order and adds it to the kitchen's order queue.
        """
        with self.lock:
            self.orders.append(order)
            self.order_map[order.order_id] = order
            logging.info(f"Order received: {order.order_id} - {order.name}, Prep Time: {order.prep_time}s")

    def dispatch_courier(self, courier):
        """
        Dispatches a courier to the kitchen based on the selected strategy.
        """
        self.strategy.dispatch(self, courier)

    def prepare_order(self, order):
        """
        Prepares an order by simulating the preparation time.
        """
        time.sleep(order.prep_time)
        order.ready_time = time.time()
        logging.info(f"Order prepared: {order.order_id} - {order.name}")

    def courier_arrival(self, courier):
        """
        Handles the arrival of a courier at the kitchen.
        """
        self.strategy.courier_arrival(self, courier)

    def pickup_order(self, order, courier):
        """
        Handles the pickup of an order by a courier.
        """
        current_time = time.time()

        if order.ready_time is None:
            return False

        if courier.arrival_time is None:
            return False

        if order.ready_time > current_time:
            return False

        food_wait_time = abs(current_time - order.ready_time) * 1000  # Calculate food wait time in milliseconds
        self.food_wait_times.append(food_wait_time)

        courier_wait_time = abs(current_time - courier.arrival_time) * 1000  # Calculate courier wait time in milliseconds
        self.courier_wait_times.append(courier_wait_time)

        logging.info(f"Order picked up: {order.order_id} by Courier: {courier.courier_id}")
        logging.info(f"Food wait time: {food_wait_time} ms")
        logging.info(f"Courier wait time: {courier_wait_time} ms")
        return True

    def process_unpicked_orders(self):
        """
        Processes any unpicked orders in the kitchen.
        """
        while True:
            with self.lock:
                if not self.orders:
                    break

                for courier in list(self.couriers):
                    if isinstance(self.strategy, FIFODispatchStrategy) and self.orders:
                        order = self.orders.popleft()
                        self.couriers.remove(courier)
                        pickup_status = self.pickup_order(order, courier)
                        if not pickup_status:
                            self.orders.append(order)
                            self.couriers.appendleft(courier)
                    elif isinstance(self.strategy, MatchedDispatchStrategy) and courier.order_id is not None and self.orders:
                        order = self.order_map.get(courier.order_id)
                        self.orders.remove(order)
                        self.couriers.remove(courier)
                        pickup_status = self.pickup_order(order, courier)
                        if not pickup_status:
                            self.orders.append(order)
                            self.couriers.appendleft(courier)
