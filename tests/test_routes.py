"""
Order API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from service import app
from service.models import db, init_db
from service.common import status  # HTTP Status Codes
from tests.factories import OrderFactory, OrderItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/orders"

######################################################################
#  T E S T   C A S E S
######################################################################


class TestOrderService(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables
        self.app = app.test_client()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    def _create_orders(self, count):
        """Factory method to create orders in bulk"""
        orders = []
        for _ in range(count):
            test_order = OrderFactory()
            response = self.app.post(BASE_URL, json=test_order.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test order"
            )
            new_order = response.get_json()
            test_order.id = new_order["id"]
            orders.append(test_order)
        return orders

    ######################################################################
    #  ORDER - P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_order(self):
        """It should Create a new Order"""
        test_order = OrderFactory()
        test_item = OrderItemFactory()
        test_order.items = [test_item]
        response = self.app.post(
            BASE_URL, json=test_order.serialize(), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_order = response.get_json()
        self.assertNotEqual(new_order["id"], None)
        self.assertEqual(new_order["customer_id"], test_order.customer_id)
        self.assertEqual(new_order["status"], test_order.status.name)
        self.assertEqual(len(new_order["items"]), 1)

        new_item = new_order["items"][0]
        self.assertEqual(new_item["product_id"], test_item.product_id)
        self.assertEqual(new_item["quantity"], test_item.quantity)
        self.assertEqual(new_item["price"], test_item.price)
        self.assertEqual(new_item["order_id"], new_order["id"])

        # Check that the location header was correct
        response = self.app.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_order = response.get_json()
        self.assertNotEqual(new_order["id"], None)
        self.assertEqual(new_order["customer_id"], test_order.customer_id)
        self.assertEqual(new_order["status"], test_order.status.name)
        self.assertEqual(len(new_order["items"]), 1)

        new_item = new_order["items"][0]
        self.assertEqual(new_item["product_id"], test_item.product_id)
        self.assertEqual(new_item["quantity"], test_item.quantity)
        self.assertEqual(new_item["price"], test_item.price)
        self.assertEqual(new_item["order_id"], new_order["id"])

    def test_create_order_with_no_items(self):
        """It should Create a new Order"""
        test_order = OrderFactory()
        response = self.app.post(
            BASE_URL, json=test_order.serialize(), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check the data is correct
        new_order = response.get_json()
        self.assertNotEqual(new_order["id"], None)
        self.assertEqual(new_order["customer_id"], test_order.customer_id)
        self.assertEqual(new_order["status"], test_order.status.name)
        self.assertEqual(len(new_order["items"]), 0)

    def test_get_order(self):
        """It should Read a single Order"""
        # get the id of a order
        test_order = self._create_orders(1)[0]
        response = self.app.get(f"{BASE_URL}/{test_order.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["id"], test_order.id)

    def test_get_order_not_found(self):
        """It should not Read an Order thats not found"""
        response = self.app.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_list_orders(self):
        """ It should list orders"""
        self._create_orders(5)
        response = self.app.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_update_order(self):
        """It should Update an existing Order"""
        # create an order to update
        test_order = OrderFactory()
        response = self.app.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the order
        new_order = response.get_json()
        new_order["customer_id"] = 5
        new_order["status"] = "DELIVERED"
        response = self.app.put(f"{BASE_URL}/{new_order['id']}", json=new_order)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_order = response.get_json()
        self.assertEqual(updated_order["customer_id"], 5)
        self.assertEqual(updated_order["status"], "DELIVERED")

    def test_update_order_with_items(self):
        """It should not Update items of an existing Order"""
        # create an order to update
        test_order = OrderFactory()
        test_item = OrderItemFactory()
        test_order.items = [test_item]
        response = self.app.post(
            BASE_URL, json=test_order.serialize(), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the order
        new_order = response.get_json()
        new_order["customer_id"] = 5
        original_product_id = new_order["items"][0]["product_id"]
        new_order["items"][0]["product_id"] = original_product_id * 2

        response = self.app.put(f"{BASE_URL}/{new_order['id']}", json=new_order)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_order = response.get_json()
        self.assertEqual(updated_order["customer_id"], 5)
        self.assertEqual(len(updated_order["items"]), 1)
        item_data = updated_order["items"][0]
        self.assertNotEqual(item_data["product_id"], original_product_id * 2)
        self.assertEqual(item_data["product_id"], original_product_id)

    def test_update_nonexistent_order(self):
        """It should not Update a nonexisting Order"""
        test_order = OrderFactory()
        response = self.app.put(f"{BASE_URL}/{test_order.id}", json=test_order.serialize())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertEqual(data["message"], f"404 Not Found: Order with id '{test_order.id}' was not found.")

    def test_delete_order(self):
        """It should Delete an Order"""
        test_order = self._create_orders(1)[0]
        response = self.app.delete(f"{BASE_URL}/{test_order.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure the order is deleted
        response = self.app.get(f"{BASE_URL}/{test_order.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  ORDER - T E S T   S A D   P A T H S
    ######################################################################

    def test_create_order_no_data(self):
        """It should not Create an Order with missing data"""
        response = self.app.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_no_content_type(self):
        """It should not Create an Order with no content type"""
        response = self.app.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_order_incorrect_content_type(self):
        """It should not Create an Order with incorrect content type"""
        response = self.app.post(BASE_URL, json={}, content_type="application/xml")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_order_bad_status(self):
        """It should not Create an Order with bad status data"""
        order = OrderFactory()
        # change status to a bad string
        test_order = order.serialize()
        test_order["status"] = "created"  # wrong value
        response = self.app.post(BASE_URL, json=test_order)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ######################################################################
    #  ITEM - P L A C E   T E S T   C A S E S   H E R E
    ######################################################################
    def test_get_items_list(self):
        """It should Get a list of Items"""
        order = self._create_orders(1)[0]
        item_list = OrderItemFactory.create_batch(2)

        # Create item 1
        resp = self.app.post(
            f"{BASE_URL}/{order.id}/items", json=item_list[0].serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create item 2
        resp = self.app.post(
            f"{BASE_URL}/{order.id}/items", json=item_list[1].serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # get the list back and make sure there are 2
        resp = self.app.get(f"{BASE_URL}/{order.id}/items", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_get_items_list_no_order_id(self):
        """It should not Get a list of Items thats not found"""
        response = self.app.get(f"{BASE_URL}/0/items", content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])
       
    def test_add_item(self):
        """It should Add an item to an order"""
        order = self._create_orders(1)[0]
        item = OrderItemFactory()
        resp = self.app.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertIsNotNone(data["id"])
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["price"], item.price)

    def test_get_item(self):
        """It should Get an item from an order"""
        # create an item
        order = self._create_orders(1)[0]
        item = OrderItemFactory()
        resp = self.app.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        item_id = data["id"]

        # retrieve it back
        resp = self.app.get(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(data["id"], item.id)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["price"], item.price)

    
    ######################################################################
    #  ITEM - T E S T   S A D   P A T H S
    ######################################################################

    def test_add_item_no_order(self):
        """It should not Create a item when order can't be find"""
        order_id = 5
        item = OrderItemFactory()
        resp = self.app.post(
            f"{BASE_URL}/{order_id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_item_item_not_found(self):
        """
        When there is an order but no such item.
        It should not Read an item thats not found
        """
        order = self._create_orders(1)[0]
        resp = self.app.get(f"{BASE_URL}/{order.id}/items/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_item_order_not_found(self):
        """
        It should not Read an item when the order is not found
        """
        resp = self.app.get(f"{BASE_URL}/0/items/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)