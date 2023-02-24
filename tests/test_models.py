"""
Test cases for Orders Model

"""
import os
import logging
import unittest
from service.models import Order, OrderStatus, DataValidationError, db
from service import app
from tests.factories import OrderFactory
from datetime import date
from werkzeug.exceptions import NotFound

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  O R D E R   M O D E L   T E S T   C A S E S
######################################################################


class TestOrderModel(unittest.TestCase):
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
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_order(self):
        """It should Create an order and assert that it exists"""
        today_date = date.today()
        order = Order(customer_id=4, status=OrderStatus.CONFIRMED, created_on=today_date, updated_on=today_date)
        self.assertEqual(str(order), "<Order: id=None, customer_id=4, status=OrderStatus.CONFIRMED>")
        self.assertTrue(order is not None)
        self.assertEqual(order.id, None)
        self.assertEqual(order.customer_id, 4)
        self.assertEqual(order.status, OrderStatus.CONFIRMED)
        self.assertEqual(order.created_on, today_date)
        self.assertEqual(order.updated_on, today_date)

    def test_add_an_order(self):
        """It should Create an order and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = Order(customer_id=4, status=OrderStatus.CONFIRMED)
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

    def test_deserialize_an_order(self):
        """It should de-serialize an Order"""
        data = OrderFactory().serialize()
        order = Order()
        order.deserialize(data)
        self.assertNotEqual(order, None)
        self.assertEqual(order.id, data['id'])
        self.assertEqual(order.customer_id, data['customer_id'])
        self.assertEqual(order.status.name, data['status'])
        self.assertEqual(order.updated_on, date.today())

    def test_deserialize_default_status(self):
        """It should de-serialize an Order"""
        data = OrderFactory().serialize()
        del data['status']
        order = Order()
        order.deserialize(data)
        self.assertNotEqual(order, None)
        self.assertEqual(order.id, data['id'])
        self.assertEqual(order.customer_id, data['customer_id'])
        self.assertEqual(order.status, OrderStatus.CONFIRMED)
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
