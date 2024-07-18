from abc import ABC, abstractmethod
import time
import logging
import threading
from enum import Enum

class DispatchStrategyType(Enum):
    """
    Enum to define dispatch strategies.
    """
    MATCHED = 'matched'
    FIFO = 'fifo'

class DispatchStrategy(ABC):
    """
    Abstract base class for dispatch strategies.
    """
    @abstractmethod
    def dispatch(self, kitchen, courier):
        pass

    @abstractmethod
    def courier_arrival(self, kitchen, courier):
        pass

class MatchedDispatchStrategy(DispatchStrategy):
    """
    Dispatch strategy where couriers are matched with specific orders.
    """
    def dispatch(self, kitchen, courier):
        with kitchen.lock:
            kitchen.couriers.append(courier)
            kitchen.courier_map[courier.courier_id] = courier
            logging.info(f"Courier: {courier.courier_id} dispatched for Order: {courier.order_id}")

    def courier_arrival(self, kitchen, courier):
        courier.arrival_time = time.time()
        logging.info(f"Courier (Matched): {courier.courier_id} arrived for Order: {courier.order_id}")
        with kitchen.lock:
            order = kitchen.order_map.get(courier.order_id)
            if order and order.ready_time and order in kitchen.orders:
                kitchen.orders.remove(order)
                kitchen.couriers.remove(courier)
                pickup_status = kitchen.pickup_order(order, courier)
                if not pickup_status:
                    threading.Timer(order.ready_time - time.time(), kitchen.courier_arrival, args=(courier,)).start()
            else:
                logging.info(f"Courier: {courier.courier_id} waiting for Order: {courier.order_id}")

class FIFODispatchStrategy(DispatchStrategy):
    """
    Dispatch strategy where couriers pick up orders in a FIFO manner.
    """
    def dispatch(self, kitchen, courier):
        with kitchen.lock:
            kitchen.couriers.append(courier)
            kitchen.courier_map[courier.courier_id] = courier
            logging.info(f"Courier: {courier.courier_id} dispatched for any Order")

    def courier_arrival(self, kitchen, courier):
        courier.arrival_time = time.time()
        logging.info(f"Courier: {courier.courier_id} arrived for any Order")
        with kitchen.lock:
            if kitchen.orders and courier in kitchen.couriers:
                order = kitchen.orders.popleft()
                kitchen.couriers.remove(courier)
                pickup_status = kitchen.pickup_order(order, courier)
                if not pickup_status:
                    if order.ready_time:
                        threading.Timer(order.ready_time - time.time(), kitchen.courier_arrival, args=(courier,)).start()
                    else:
                        kitchen.orders.append(order)
                        kitchen.couriers.append(courier)
            else:
                logging.info(f"Courier waiting for any Order: {courier.courier_id}")
