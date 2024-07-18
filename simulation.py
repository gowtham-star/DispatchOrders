import argparse
import json
import threading
import time
import random
import atexit
import logging
import os
from classes.kitchen import Kitchen
from classes.order import Order
from classes.courier import Courier
from classes.strategy import DispatchStrategyType, MatchedDispatchStrategy, FIFODispatchStrategy
from statistics import mean
from datetime import datetime

# Function to setup logging
def setup_logging():
    timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    logfile = f'logs/kitchen_simulation_{timestamp}.log'
    if os.path.exists(logfile):
        os.remove(logfile)
    logging.basicConfig(filename=logfile, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize logging
setup_logging()

threads = []

def simulate_order_generation(kitchen, orders):
    """
    Simulates the generation and preparation of orders in the kitchen.
    """
    try:
        for order in orders:
            kitchen.receive_order(order)
            t1 = threading.Thread(target=kitchen.prepare_order, args=(order,))
            threads.append(t1)
            t1.start()
            time.sleep(0.5)  # Simulate 2 orders per second
    except Exception as e:
        logging.error(f"Error in order generation: {e}")

def simulate_courier_dispatch(kitchen, orders, total_orders):
    """
    Simulates the dispatch and arrival of couriers at the kitchen.
    """
    try:
        for i in range(total_orders):
            courier = Courier(i)
            if isinstance(kitchen.strategy, MatchedDispatchStrategy):
                courier.order_id = orders[i].order_id
            kitchen.dispatch_courier(courier)
            t1 = threading.Timer(random.uniform(3, 15), kitchen.courier_arrival, args=(courier,))
            threads.append(t1)
            t1.start()
            time.sleep(0.5)  # Simulate dispatch of couriers
    except Exception as e:
        logging.error(f"Error in courier dispatch: {e}")

def stats(kitchen):
    """
    Logs the final statistics (average wait times) before the program exits.
    """
    logging.info("--- Final Statistics ---")
    if kitchen.food_wait_times:
        logging.info(f"Average Food Wait Time: {mean(kitchen.food_wait_times)} ms")
    else:
        logging.info("No Food Wait Time data available.")

    if kitchen.courier_wait_times:
        logging.info(f"Average Courier Wait Time: {mean(kitchen.courier_wait_times)} ms")
    else:
        logging.info("No Courier Wait Time data available.")

def main():
    """
    Main function to run the kitchen order dispatch simulation.
    """
    parser = argparse.ArgumentParser(description='Simulate a kitchen order dispatch system.')
    parser.add_argument('strategy', choices=[e.value for e in DispatchStrategyType], help='Dispatch strategy: matched or fifo')
    args = parser.parse_args()

    # Determine strategy based on input
    if args.strategy == DispatchStrategyType.MATCHED.value:
        strategy = MatchedDispatchStrategy()
    else:
        strategy = FIFODispatchStrategy()

    kitchen = Kitchen(strategy)

    # Load order data
    with open('dispatch_orders.json') as f:
        orders_data = json.load(f)
    orders = [Order(data['id'], data['name'], data['prepTime']) for data in orders_data]

    # Start simulation
    t1 = threading.Thread(target=simulate_order_generation, args=(kitchen, orders))
    threads.append(t1)
    t1.start()
    t2 = threading.Thread(target=simulate_courier_dispatch, args=(kitchen, orders, len(orders)))
    threads.append(t2)
    t2.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    kitchen.process_unpicked_orders()

    # Print the stats on exit
    atexit.register(stats, kitchen)

if __name__ == "__main__":
    main()
