"""
Test cases for Orders Model

"""
import os
import logging
import unittest
from datetime import date
from werkzeug.exceptions import NotFound
from service.models import Order, OrderItem, OrderStatus, DataValidationError, db
from service import app
from tests.factories import OrderFactory, OrderItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  O R D E R   M O D E L   T E S T   C A S E S
######################################################################


class TestOrderModel(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Test Cases for Order Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Order.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_order(self):
        """It should Create an order and assert that it exists"""
        today_date = date.today()
        items = [OrderItem(product_id=1, quantity=1, price=5, created_on=today_date, updated_on=today_date)]
        order = Order(customer_id=4, status=OrderStatus.CONFIRMED, items=items, created_on=today_date, updated_on=today_date)
        self.assertEqual(str(order), "<Order: id=None, customer_id=4, status=OrderStatus.CONFIRMED>")
        self.assertTrue(order is not None)
        self.assertEqual(order.id, None)
        self.assertEqual(order.customer_id, 4)
        self.assertEqual(order.status, OrderStatus.CONFIRMED)
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.created_on, today_date)
        self.assertEqual(order.updated_on, today_date)

    def test_add_an_order(self):
        """It should Create an order and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = Order(customer_id=4, status=OrderStatus.CONFIRMED, items=[])
        self.assertTrue(order is not None)
        self.assertEqual(order.id, None)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

    def test_read_an_order(self):
        """It should Read an Order"""
        order = OrderFactory()
        order.id = None
        order.create()
        self.assertIsNotNone(order.id)
        # Fetch it back
        found_order = Order.find(order.id)
        self.assertEqual(found_order.id, order.id)
        self.assertEqual(found_order.customer_id, order.customer_id)
        self.assertEqual(found_order.status, order.status)

    def test_update_an_order(self):
        """It should Update an Order"""
        order = OrderFactory()
        order.id = None
        order.create()
        self.assertIsNotNone(order.id)

        order.customer_id = 10
        original_id = order.id
        order.update()
        self.assertEqual(order.id, original_id)
        self.assertEqual(order.customer_id, 10)

        # Fetch it back and make sure the id hasn't changed but the data did change
        orders = Order.all()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].id, original_id)
        self.assertEqual(orders[0].customer_id, 10)

    def test_update_no_id(self):
        """It should not Update an Order with no id"""
        order = OrderFactory()
        order.id = None
        self.assertRaises(DataValidationError, order.update)

    def test_delete_an_order(self):
        """It should Delete an Order"""
        order = OrderFactory()
        order.create()
        self.assertEqual(len(Order.all()), 1)
        # Delete the order and make sure it isn't in the database
        order.delete()
        self.assertEqual(len(Order.all()), 0)

    def test_list_all_orders(self):
        """It should List all Orders in the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        # Create 5 Orders
        for _ in range(5):
            order = OrderFactory()
            order.create()
        # See if we get back 5 orders
        orders = Order.all()
        self.assertEqual(len(orders), 5)

    def test_serialize_an_order(self):
        """It should serialize an Order"""
        order = OrderFactory()
        item = OrderItemFactory()
        order.items = [item]
        data = order.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], order.id)
        self.assertIn('customer_id', data)
        self.assertEqual(data['customer_id'], order.customer_id)
        self.assertIn('status', data)
        self.assertEqual(data['status'], order.status.name)
        self.assertIn('created_on', data)
        self.assertEqual(date.fromisoformat(data['created_on']), order.created_on)
        self.assertIn('updated_on', data)
        self.assertEqual(date.fromisoformat(data['updated_on']), order.updated_on)
        self.assertEqual(len(data['items']), 1)
        items = data['items']
        self.assertEqual(items[0]['id'], item.id)
        self.assertEqual(items[0]['product_id'], item.product_id)
        self.assertEqual(items[0]['quantity'], item.quantity)
        self.assertEqual(items[0]['price'], item.price)
        self.assertEqual(items[0]['order_id'], item.order_id)

    def test_deserialize_an_order(self):
        """It should de-serialize an Order"""
        order_data = OrderFactory()
        item = OrderItemFactory()
        order_data.items = [item]
        serialized_data = order_data.serialize()
        order = Order()
        order.deserialize(serialized_data)
        self.assertNotEqual(order, None)
        self.assertEqual(order.customer_id, serialized_data['customer_id'])
        self.assertEqual(order.status.name, serialized_data['status'])
        self.assertEqual(order.updated_on, date.today())
        items = order.items
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].product_id, item.product_id)
        self.assertEqual(items[0].quantity, item.quantity)
        self.assertEqual(items[0].price, item.price)
        self.assertEqual(items[0].updated_on, date.today())

    def test_deserialize_default_status(self):
        """It should de-serialize an Order"""
        data = OrderFactory().serialize()
        del data['status']
        order = Order()
        order.deserialize(data)
        self.assertNotEqual(order, None)
        self.assertEqual(order.customer_id, data['customer_id'])
        self.assertEqual(order.status, OrderStatus.CONFIRMED)
        self.assertEqual(order.updated_on, date.today())

    def test_deserialize_zero_customer_id(self):
        """It should de-serialize an Order"""
        data = OrderFactory().serialize()
        data['customer_id'] = 0
        order = Order()
        order.deserialize(data)
        self.assertNotEqual(order, None)
        self.assertEqual(order.customer_id, data['customer_id'])
        self.assertEqual(order.updated_on, date.today())

    def test_deserialize_missing_data(self):
        """It should not deserialize an Order with missing data"""
        data = {"id": 1}
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_deserialize_with_key_error(self):
        """ Deserialize an order with a KeyError """
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, {})

    def test_deserialize_with_type_error(self):
        """ Deserialize an order with a TypeError """
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, [])

    def test_deserialize_bad_status(self):
        """It should not deserialize a bad status attribute"""
        test_order = OrderFactory()
        data = test_order.serialize()
        data['status'] = "created"  # wrong case
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_deserialize_bad_customer_id(self):
        """ Deserialize an order with bad customer id """
        test_order = OrderFactory()
        data = test_order.serialize()
        data['customer_id'] = "abcd"  # wrong value
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_deserialize_string_customer_id(self):
        """ Deserialize an order with bad customer id """
        test_order = OrderFactory()
        data = test_order.serialize()
        data['customer_id'] = "123"  # wrong value
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_deserialize_negative_customer_id(self):
        """ Deserialize an order with bad customer id """
        test_order = OrderFactory()
        data = test_order.serialize()
        data['customer_id'] = "-1"  # wrong value
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, data)

        data['customer_id'] = -1  # wrong value
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_find_order(self):
        """It should Find an Order by ID"""
        orders = OrderFactory.create_batch(5)
        for order in orders:
            order.create()
        # make sure they got saved
        self.assertEqual(len(Order.all()), 5)
        # find the 2nd order in the list
        order = Order.find(orders[1].id)
        self.assertIsNot(order, None)
        self.assertEqual(order.id, orders[1].id)
        self.assertEqual(order.customer_id, orders[1].customer_id)
        self.assertEqual(order.status, orders[1].status)
        self.assertEqual(order.created_on, orders[1].created_on)
        self.assertEqual(order.updated_on, orders[1].updated_on)

    def test_find_or_404_found(self):
        """It should Find or return 404 not found"""
        orders = OrderFactory.create_batch(3)
        for order in orders:
            order.create()

        order = Order.find_or_404(orders[1].id)
        self.assertIsNot(order, None)
        self.assertEqual(order.id, orders[1].id)
        self.assertEqual(order.customer_id, orders[1].customer_id)
        self.assertEqual(order.status, orders[1].status)
        self.assertEqual(order.created_on, orders[1].created_on)
        self.assertEqual(order.updated_on, orders[1].updated_on)

    def test_find_or_404_not_found(self):
        """It should return 404 not found"""
        self.assertRaises(NotFound, Order.find_or_404, 0)

    def test_add_an_order_with_items(self):
        """It should Create an order and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        item = OrderItem(id=1, product_id=3, quantity=2, price=100, order_id=1)
        order = Order(id=1, customer_id=4, status=OrderStatus.CONFIRMED, items=[item])
        self.assertTrue(order is not None)
        self.assertEqual(order.id, 1)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)
        self.assertEqual(len(orders[0].items), 1)
        self.assertEqual(orders[0].items[0].id, item.id)

    def test_read_an_order_with_items(self):
        """It should Read an Order"""
        order = OrderFactory()
        order.id = None
        item = OrderItemFactory()
        order.items = [item]
        order.create()
        self.assertIsNotNone(order.id)
        # Fetch it back
        found_order = Order.find(order.id)
        self.assertEqual(found_order.id, order.id)
        self.assertEqual(found_order.customer_id, order.customer_id)
        self.assertEqual(found_order.status, order.status)
        self.assertEqual(len(found_order.items), 1)
        self.assertEqual(found_order.items[0].id, item.id)

    def test_update_an_order_with_items(self):
        """It should Update an Order"""
        order = OrderFactory()
        item = OrderItemFactory()
        order.id = None
        item.id = None
        order.items = [item]
        order.create()
        self.assertIsNotNone(order.id)

        order = Order.find(order.id)
        old_item = order.items[0]
        self.assertEqual(old_item.product_id, item.product_id)

        original_id = order.id
        old_item.product_id = 5
        order.update()
        self.assertEqual(order.id, original_id)
        self.assertEqual(order.items[0].product_id, 5)

        # Fetch it back and make sure the id hasn't changed but the data did change
        orders = Order.all()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].id, original_id)
        self.assertEqual(orders[0].items[0].product_id, 5)

    def test_delete_order_item(self):
        """ Delete an order's item """
        order = OrderFactory()
        item = OrderItemFactory()
        order.id = None
        item.id = None
        order.items = [item]
        order.create()
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        # Fetch it back
        order = Order.find(order.id)
        item = order.items[0]
        item.delete()
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        self.assertEqual(len(order.items), 0)

    def test_find_by_customer(self):
        """It should Find Orders by Customer ID"""
        orders = OrderFactory.create_batch(10)
        for order in orders:
            order.create()

        # Make sure the orders got saved
        self.assertEqual(len(Order.all()), 10)

        # Fetch filtered orders - same customer
        customer_id = orders[0].customer_id
        count = len([order for order in orders if order.customer_id == customer_id])
        found_orders = Order.find_by_customer(customer_id)
        self.assertEqual(found_orders.count(), count)
        for order in found_orders:
            self.assertEqual(order.customer_id, customer_id)

        # Fetch filtered orders - different customer
        self.assertEqual(Order.find_by_customer(4).count(), 0)

    def test_find_by_status(self):
        """It should Find Orders by Status"""
        orders = OrderFactory.create_batch(10)
        for order in orders:
            order.create()

        # Make sure the orders got saved
        self.assertEqual(len(Order.all()), 10)

        status = orders[0].status
        count = len([order for order in orders if order.status == status])
        found_orders = Order.find_by_status(status)
        self.assertEqual(found_orders.count(), count)
        for order in found_orders:
            self.assertEqual(order.status, status)

    def test_find_by_product(self):
        """It should Find an Orders by Product ID"""
        orders = OrderFactory.create_batch(3)
        for order in orders:
            order.create()

        test_product_id = 12
        items = OrderItemFactory.create_batch(3)
        items[0].product_id = test_product_id
        items[1].product_id = test_product_id

        for i in range(3):
            items[i].order_id = orders[i].id
            items[i].create()

        # make sure they got saved
        self.assertEqual(len(Order.all()), 3)
        self.assertEqual(len(OrderItem.all()), 3)

        count = len([order for order in orders if any(order_item.product_id == test_product_id for order_item in order.items)])
        found_orders = Order.find_by_product(test_product_id)
        self.assertEqual(found_orders.count(), count)
        for order in found_orders:
            self.assertTrue(any(item.product_id == test_product_id for item in order.items))

######################################################################
#  O R D E R   I T E M   M O D E L   T E S T   C A S E S
######################################################################


class TestOrderItemModel(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """ Test Cases for Order Item Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Order.init_db(app)
        OrderItem.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_order_item(self):
        """It should Create an order item and assert that it exists"""
        today_date = date.today()
        item = OrderItem(product_id=4, quantity=2, price=100, order_id=1, created_on=today_date, updated_on=today_date)
        self.assertEqual(str(item), "<Order Item: id=None, order_id=1, product_id=4, quantity=2>")
        self.assertTrue(item is not None)
        self.assertEqual(item.id, None)
        self.assertEqual(item.product_id, 4)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.price, 100)
        self.assertEqual(item.order_id, 1)
        self.assertEqual(item.created_on, today_date)
        self.assertEqual(item.updated_on, today_date)

    def test_add_an_order_item(self):
        """It should Create an order item and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = Order(customer_id=4, status=OrderStatus.CONFIRMED, items=[])
        self.assertTrue(order is not None)
        self.assertEqual(order.id, None)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)

        items = OrderItem.all()
        self.assertEqual(items, [])
        item = OrderItem(product_id=4, quantity=2, price=100, order_id=order.id)
        self.assertTrue(item is not None)
        self.assertEqual(item.id, None)
        item.create()
        self.assertIsNotNone(item.id)
        items = OrderItem.all()
        self.assertEqual(len(items), 1)

    def test_read_an_order_item(self):
        """It should Read an Order Item"""
        order = OrderFactory()
        item = OrderItemFactory()
        order.id = None
        order.create()
        self.assertIsNotNone(order.id)

        item.order_id = order.id
        item.id = None
        item.create()
        self.assertIsNotNone(item.id)

        # Fetch it back
        found_order_item = OrderItem.find(item.id)
        self.assertEqual(found_order_item.id, item.id)
        self.assertEqual(found_order_item.product_id, item.product_id)
        self.assertEqual(found_order_item.quantity, item.quantity)
        self.assertEqual(found_order_item.price, item.price)
        self.assertEqual(found_order_item.order_id, item.order_id)

    def test_update_an_order_item(self):
        """It should Update an Order Item"""
        order = OrderFactory()
        order.id = None
        order.create()
        self.assertIsNotNone(order.id)

        item = OrderItemFactory()
        item.id = None
        item.order_id = order.id
        item.create()
        self.assertIsNotNone(item.id)

        item.product_id = 45
        original_id = item.id
        item.update()
        self.assertEqual(item.id, original_id)
        self.assertEqual(item.product_id, 45)

        # Fetch it back and make sure the id hasn't changed but the data did change
        items = OrderItem.all()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id, original_id)
        self.assertEqual(items[0].product_id, 45)

    def test_update_no_id(self):
        """It should not Update an Order Item with no id"""
        item = OrderItemFactory()
        item.id = None
        self.assertRaises(DataValidationError, item.update)

    def test_delete_an_order_item(self):
        """It should Delete an Order Item"""
        order = OrderFactory()
        order.create()
        self.assertEqual(len(Order.all()), 1)

        item = OrderItemFactory()
        item.order_id = order.id
        item.create()
        self.assertEqual(len(OrderItem.all()), 1)

        # Delete the order and make sure it isn't in the database
        item.delete()
        self.assertEqual(len(OrderItem.all()), 0)

    def test_list_all_order_items(self):
        """It should List all Order Items in the database"""
        order = OrderFactory()
        order.create()
        self.assertEqual(len(Order.all()), 1)

        items = OrderItem.all()
        self.assertEqual(items, [])

        # Create 5 Orders
        for _ in range(5):
            item = OrderItemFactory()
            item.order_id = order.id
            item.create()

        # See if we get back 5 orders
        items = OrderItem.all()
        self.assertEqual(len(items), 5)

    def test_serialize_an_order_item(self):
        """It should serialize an Order Item"""
        item = OrderItemFactory()
        data = item.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], item.id)
        self.assertIn('product_id', data)
        self.assertEqual(data['product_id'], item.product_id)
        self.assertIn('quantity', data)
        self.assertEqual(data['quantity'], item.quantity)
        self.assertIn('price', data)
        self.assertEqual(data['price'], item.price)
        self.assertIn('order_id', data)
        self.assertEqual(data['order_id'], item.order_id)
        self.assertIn('created_on', data)
        self.assertEqual(date.fromisoformat(data['created_on']), item.created_on)
        self.assertIn('updated_on', data)
        self.assertEqual(date.fromisoformat(data['updated_on']), item.updated_on)

    def test_deserialize_an_order_item(self):
        """It should de-serialize an Order Item"""
        data = OrderItemFactory().serialize()
        item = OrderItem()
        item.deserialize(data)
        self.assertNotEqual(item, None)
        self.assertEqual(item.product_id, data['product_id'])
        self.assertEqual(item.quantity, data['quantity'])
        self.assertEqual(item.price, data['price'])
        self.assertEqual(item.updated_on, date.today())

    def test_deserialize_zero_numerical_values(self):
        """It should de-serialize an Order """
        data = OrderItemFactory().serialize()
        data['product_id'] = 0
        data['quantity'] = 1
        data['price'] = 0.0
        item = OrderItem()
        item.deserialize(data)
        self.assertNotEqual(item, None)
        self.assertEqual(item.product_id, data['product_id'])
        self.assertEqual(item.quantity, data['quantity'])
        self.assertEqual(item.price, data['price'])
        self.assertEqual(item.updated_on, date.today())

    def test_deserialize_missing_data(self):
        """It should not deserialize an Order Item with missing data"""
        data = {"id": 1}
        item = OrderItem()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        item = OrderItem()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_with_key_error(self):
        """ Deserialize an order item with a KeyError """
        item = OrderItem()
        self.assertRaises(DataValidationError, item.deserialize, {})

    def test_deserialize_with_type_error(self):
        """ Deserialize an order item with a TypeError """
        item = OrderItem()
        self.assertRaises(DataValidationError, item.deserialize, [])

    def test_deserialize_bad_product_id(self):
        """ Deserialize an order item with a ValueError """
        test_order_item = OrderItemFactory()
        data = test_order_item.serialize()
        data['product_id'] = "abcd"  # wrong value
        order_item = OrderItem()
        self.assertRaises(DataValidationError, order_item.deserialize, data)

        data['product_id'] = "123"  # wrong value
        self.assertRaises(DataValidationError, order_item.deserialize, data)

        data['product_id'] = "-1"  # wrong value
        self.assertRaises(DataValidationError, order_item.deserialize, data)

        data['product_id'] = -1  # wrong value
        self.assertRaises(DataValidationError, order_item.deserialize, data)

    def test_deserialize_bad_quantity(self):
        """ Deserialize an order item with a ValueError """
        test_order_item = OrderItemFactory()
        data = test_order_item.serialize()
        data['quantity'] = "abcd"  # wrong value
        order_item = OrderItem()
        self.assertRaises(DataValidationError, order_item.deserialize, data)

        data['quantity'] = "123"  # wrong value
        self.assertRaises(DataValidationError, order_item.deserialize, data)

        data['quantity'] = "-1"  # wrong value
        self.assertRaises(DataValidationError, order_item.deserialize, data)

        data['quantity'] = "0"  # wrong value
        self.assertRaises(DataValidationError, order_item.deserialize, data)

        data['quantity'] = -1  # wrong value
        self.assertRaises(DataValidationError, order_item.deserialize, data)

        data['quantity'] = 0  # wrong value
        self.assertRaises(DataValidationError, order_item.deserialize, data)

    def test_deserialize_bad_price(self):
        """ Deserialize an order item with a ValueError """
        test_order_item = OrderItemFactory()
        data = test_order_item.serialize()
        data['price'] = "abcd"  # wrong value
        order_item = OrderItem()
        self.assertRaises(DataValidationError, order_item.deserialize, data)

        data['price'] = "123"  # wrong value
        self.assertRaises(DataValidationError, order_item.deserialize, data)

        data['price'] = "-1"  # wrong value
        self.assertRaises(DataValidationError, order_item.deserialize, data)

        data['price'] = -1  # wrong value
        self.assertRaises(DataValidationError, order_item.deserialize, data)

    def test_find_order_item(self):
        """It should Find an Order Item by ID"""
        order = OrderFactory()
        order.create()
        items = OrderItemFactory.create_batch(5)
        for item in items:
            item.order_id = order.id
            item.create()
        # make sure they got saved
        self.assertEqual(len(OrderItem.all()), 5)
        # find the 2nd order item in the list
        item = OrderItem.find(items[1].id)
        self.assertIsNot(item, None)
        self.assertEqual(item.id, items[1].id)
        self.assertEqual(item.product_id, items[1].product_id)
        self.assertEqual(item.quantity, items[1].quantity)
        self.assertEqual(item.price, items[1].price)
        self.assertEqual(item.order_id, items[1].order_id)
        self.assertEqual(item.created_on, items[1].created_on)
        self.assertEqual(item.updated_on, items[1].updated_on)

    def test_find_or_404_found(self):
        """It should Find or return 404 not found"""
        order = OrderFactory()
        order.create()
        self.assertEqual(len(Order.all()), 1)

        items = OrderItemFactory.create_batch(3)
        for item in items:
            item.order_id = order.id
            item.create()

        item = OrderItem.find_or_404(items[1].id)
        self.assertIsNot(item, None)
        self.assertEqual(item.id, items[1].id)
        self.assertEqual(item.product_id, items[1].product_id)
        self.assertEqual(item.quantity, items[1].quantity)
        self.assertEqual(item.price, items[1].price)
        self.assertEqual(item.order_id, items[1].order_id)
        self.assertEqual(item.created_on, items[1].created_on)
        self.assertEqual(item.updated_on, items[1].updated_on)

    def test_find_or_404_not_found(self):
        """It should return 404 not found"""
        self.assertRaises(NotFound, OrderItem.find_or_404, 0)

    def test_find_order_item_by_order_id(self):
        """It should Find an Order Item by ID and Order id"""
        order = OrderFactory()
        order.create()
        items = OrderItemFactory.create_batch(5)
        for item in items:
            item.order_id = order.id
            item.create()
        # make sure they got saved
        self.assertEqual(len(OrderItem.all()), 5)

        # find the 2nd order item in the list
        item = OrderItem.find_by_order_and_item_id(order.id, items[1].id)
        self.assertIsNot(item, None)
        self.assertEqual(item.id, items[1].id)
        self.assertEqual(item.product_id, items[1].product_id)
        self.assertEqual(item.quantity, items[1].quantity)
        self.assertEqual(item.price, items[1].price)
        self.assertEqual(item.order_id, items[1].order_id)
        self.assertEqual(item.created_on, items[1].created_on)
        self.assertEqual(item.updated_on, items[1].updated_on)

    def test_find_order_item_by_nonexistent_order_id(self):
        """It should not Find an Order Item by ID and Order id"""
        order = OrderFactory()
        order.create()
        items = OrderItemFactory.create_batch(5)
        for item in items:
            item.order_id = order.id
            item.create()
        # make sure they got saved
        self.assertEqual(len(OrderItem.all()), 5)

        # find the 2nd order item in the list, but pass wrong order id
        item = OrderItem.find_by_order_and_item_id(order.id * 2, items[1].id)
        self.assertIsNone(item)
