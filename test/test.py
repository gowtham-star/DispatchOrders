import unittest
import argparse
from unittest.mock import patch
import json
import time
from classes.kitchen import Kitchen
from classes.order import Order
from classes.courier import Courier
from classes.strategy import MatchedDispatchStrategy, FIFODispatchStrategy, DispatchStrategyType
import simulation as simulation

class TestOrder(unittest.TestCase):
    def test_order_initialization(self):
        order = Order(1, 'Pizza', 5)
        self.assertEqual(order.order_id, 1)
        self.assertEqual(order.name, 'Pizza')
        self.assertEqual(order.prep_time, 5)
        self.assertIsNone(order.ready_time)
        self.assertIsNone(order.courier_id)

class TestCourier(unittest.TestCase):
    def test_courier_initialization(self):
        courier = Courier(1)
        self.assertEqual(courier.courier_id, 1)
        self.assertIsNone(courier.arrival_time)
        self.assertIsNone(courier.order_id)

class TestMatchedDispatchStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = MatchedDispatchStrategy()
        self.kitchen = Kitchen(self.strategy)
        self.order = Order(1, 'Pizza', 5)
        self.courier = Courier(1)
        self.courier.order_id = self.order.order_id

    def test_dispatch(self):
        self.strategy.dispatch(self.kitchen, self.courier)
        self.assertIn(self.courier, self.kitchen.couriers)

    def test_courier_arrival(self):
        self.kitchen.receive_order(self.order)
        self.kitchen.prepare_order(self.order)
        self.strategy.dispatch(self.kitchen, self.courier)
        self.strategy.courier_arrival(self.kitchen, self.courier)
        self.assertEqual(len(self.kitchen.orders), 0)

class TestFIFODispatchStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = FIFODispatchStrategy()
        self.kitchen = Kitchen(self.strategy)
        self.order = Order(1, 'Pizza', 5)
        self.courier = Courier(1)

    def test_dispatch(self):
        self.strategy.dispatch(self.kitchen, self.courier)
        self.assertIn(self.courier, self.kitchen.couriers)

    def test_courier_arrival(self):
        self.kitchen.receive_order(self.order)
        self.kitchen.prepare_order(self.order)
        self.strategy.dispatch(self.kitchen, self.courier)
        self.strategy.courier_arrival(self.kitchen, self.courier)
        self.assertEqual(len(self.kitchen.orders), 0)

class TestKitchen(unittest.TestCase):
    def setUp(self):
        self.kitchen_fifo = Kitchen(FIFODispatchStrategy())
        self.kitchen_matched = Kitchen(MatchedDispatchStrategy())

    def test_receive_order(self):
        order = Order(1, 'Pizza', 5)
        self.kitchen_fifo.receive_order(order)
        self.assertIn(order, self.kitchen_fifo.orders)

    def test_dispatch_courier_fifo(self):
        courier = Courier(1)
        self.kitchen_fifo.dispatch_courier(courier)
        self.assertIn(courier, self.kitchen_fifo.couriers)

    def test_dispatch_courier_matched(self):
        courier = Courier(1)
        order = Order(1, 'Pizza', 5)
        self.kitchen_matched.receive_order(order)
        self.kitchen_matched.prepare_order(order)
        courier.order_id = order.order_id
        self.kitchen_matched.dispatch_courier(courier)
        self.assertIn(courier, self.kitchen_matched.couriers)

    def test_prepare_order(self):
        order = Order(1, 'Pizza', 1)
        start_time = time.time()
        self.kitchen_fifo.prepare_order(order)
        end_time = time.time()
        self.assertIsNotNone(order.ready_time)
        self.assertGreaterEqual(end_time - start_time, order.prep_time)

    def test_pickup_order(self):
        order = Order(1, 'Pizza', 1)
        courier = Courier(1)
        self.kitchen_fifo.receive_order(order)
        self.kitchen_fifo.prepare_order(order)
        courier.arrival_time = time.time()
        self.assertTrue(self.kitchen_fifo.pickup_order(order, courier))

class TestSimulation(unittest.TestCase):
    @patch('simulation.Kitchen.process_unpicked_orders')
    def test_simulation(self, mock_process):
        with patch('builtins.open', unittest.mock.mock_open(read_data=json.dumps([
            {'id': 1, 'name': 'Pizza', 'prepTime': 5},
            {'id': 2, 'name': 'Burger', 'prepTime': 3}
        ]))):
            with patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(strategy='fifo')):
                simulation.main()
                self.assertTrue(mock_process.called)

if __name__ == '__main__':
    unittest.main()