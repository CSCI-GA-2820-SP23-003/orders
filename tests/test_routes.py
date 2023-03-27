"""
Order API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from urllib.parse import quote_plus
from unittest import TestCase
from service import app
from service.models import db, init_db, OrderStatus
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
    # pylint: disable=too-many-public-methods
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
    #  O R D E R  -  P L A C E   T E S T   C A S E S   H E R E
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

    def test_query_order_list_by_customer(self):
        """It should Query Orders by Customer ID"""
        orders = self._create_orders(10)
        test_customer_id = orders[0].customer_id
        customer_orders = [order for order in orders if order.customer_id == test_customer_id]
        response = self.app.get(
            BASE_URL,
            query_string=f"customer_id={test_customer_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(customer_orders))
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["customer_id"], test_customer_id)

    def test_query_order_list_by_status(self):
        """It should Query Orders by Status"""
        orders = self._create_orders(10)
        test_status = orders[0].status
        status_orders = [order for order in orders if order.status == test_status]
        response = self.app.get(
            BASE_URL, query_string=f"status={quote_plus(test_status.name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(status_orders))
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["status"], test_status.name)

    def test_query_order_list_by_product(self):
        """It should Query Orders by Product ID"""
        orders = self._create_orders(3)
        items = OrderItemFactory.create_batch(3)

        test_product_id = 15
        items[0].product_id = test_product_id
        items[2].product_id = test_product_id

        # Create item 1
        resp = self.app.post(
            f"{BASE_URL}/{orders[0].id}/items", json=items[0].serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create item 2
        resp = self.app.post(
            f"{BASE_URL}/{orders[1].id}/items", json=items[1].serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create item 3
        resp = self.app.post(
            f"{BASE_URL}/{orders[2].id}/items", json=items[2].serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        response = self.app.get(
            BASE_URL,
            query_string=f"product_id={test_product_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["items"][0]["product_id"], test_product_id)

    def test_cancel_order(self):
        """Cancelling order"""
        # test cancel order
        test_order = OrderFactory()
        test_order.status = OrderStatus.CONFIRMED  # change status to confirmed
        resp = self.app.post(BASE_URL, json=test_order.serialize())
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["status"], OrderStatus.CONFIRMED.name)
        logging.debug(test_order)

        # try cancelling an order
        resp = self.app.put(f"{BASE_URL}/{data['id']}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # try get the order back and check for status
        resp = self.app.get(f"{BASE_URL}/{data['id']}")
        data = resp.get_json()
        logging.debug(test_order)
        self.assertEqual(data['status'], OrderStatus.CANCELLED.name)

    ######################################################################
    #  O R D E R  -  T E S T   S A D   P A T H S
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

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.app.put(BASE_URL, json={"not": "today"})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_order_bad_status(self):
        """It should not Create an Order with bad status data"""
        order = OrderFactory()
        # change status to a bad string
        test_order = order.serialize()
        test_order["status"] = "created"  # wrong value
        response = self.app.post(BASE_URL, json=test_order)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_query_order_list_by_bad_status(self):
        """It should not Query Orders by bad status"""
        bad_status = "unknown"
        response = self.app.get(BASE_URL, query_string=f"status={quote_plus(bad_status)}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.get_json()["message"], f"400 Bad Request: Invalid status '{bad_status}'.")

    def test_cancel_order_not_found(self):
        """Cancelling order not exists"""
        resp = self.app.put(f"{BASE_URL}/1/cancel")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_cancel_order_already_cancel(self):
        """Cancelling order already_cancel"""
        test_order = OrderFactory()
        test_order.status = OrderStatus.CANCELLED  # change status to cancelled
        resp = self.app.post(BASE_URL, json=test_order.serialize())
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["status"], OrderStatus.CANCELLED.name)
        logging.debug(test_order)
        # try cancelling an order again
        resp = self.app.put(f"{BASE_URL}/{data['id']}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(resp.get_json()["message"], f"409 Conflict: Order with id {data['id']} is already cancelled.")

    def test_cancel_order_wrong_status(self):
        """Cancelling order status is shipped or delivered"""
        test_order = OrderFactory()
        test_order.status = OrderStatus.SHIPPED  # change status to shipped
        resp = self.app.post(BASE_URL, json=test_order.serialize())
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["status"], OrderStatus.SHIPPED.name)
        logging.debug(test_order)
        # try cancelling an order again
        resp = self.app.put(f"{BASE_URL}/{data['id']}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(resp.get_json()["message"], f"409 Conflict: Order with id {data['id']} is {data['status']}, request conflicted.")

        test_order = OrderFactory()
        test_order.status = OrderStatus.DELIVERED  # change status to delivered
        resp = self.app.post(BASE_URL, json=test_order.serialize())
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["status"], OrderStatus.DELIVERED.name)
        logging.debug(test_order)
        # try cancelling an order again
        resp = self.app.put(f"{BASE_URL}/{data['id']}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(resp.get_json()["message"], f"409 Conflict: Order with id {data['id']} is {data['status']}, request conflicted.")

    ######################################################################
    #  I T E M  -  P L A C E   T E S T   C A S E S   H E R E
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

    def test_create_item(self):
        """It should Add an item to an order"""
        order = self._create_orders(1)[0]
        item = OrderItemFactory()
        response = self.app.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        data = response.get_json()
        self.assertIsNotNone(data["id"])
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["price"], item.price)

        # Check that the location header was correct
        response = self.app.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
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
        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["price"], item.price)

    def test_get_item_incorrect_order(self):
        """It should not Get an item by id if order id is incorrect"""
        # create an item
        orders = self._create_orders(2)

        item_0 = OrderItemFactory()
        response = self.app.post(
            f"{BASE_URL}/{orders[0].id}/items",
            json=item_0.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        item_id_order_0 = response.get_json()["id"]

        item_1 = OrderItemFactory()
        response = self.app.post(
            f"{BASE_URL}/{orders[1].id}/items",
            json=item_1.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        item_id_order_1 = response.get_json()["id"]

        # retrieve the items with wrong order id
        response = self.app.get(
            f"{BASE_URL}/{orders[0].id}/items/{item_id_order_1}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.get_json()["message"], f"404 Not Found: Item with id '{item_id_order_1}' was not found.")

        response = self.app.get(
            f"{BASE_URL}/{orders[1].id}/items/{item_id_order_0}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.get_json()["message"], f"404 Not Found: Item with id '{item_id_order_0}' was not found.")

        # Now retrieve them with correct order id
        response = self.app.get(f"{BASE_URL}/{orders[0].id}/items/{item_id_order_0}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.app.get(f"{BASE_URL}/{orders[1].id}/items/{item_id_order_1}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_item(self):
        """It should Delete an item from an order"""
        # create an item
        order = self._create_orders(1)[0]
        item = OrderItemFactory()
        response = self.app.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.get_json()
        item_id = data["id"]

        # make sure item exists before delete
        response = self.app.get(f"{BASE_URL}/{order.id}/items/{item_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # delete the item
        response = self.app.delete(f"{BASE_URL}/{order.id}/items/{item_id}",)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # make sure item does not exist after delete
        response = self.app.get(f"{BASE_URL}/{order.id}/items/{item_id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item_nonexistent_order(self):
        """It should not delete a item when order can't be find"""
        order_id = 5
        item_id = 5
        response = self.app.delete(f"{BASE_URL}/{order_id}/items/{item_id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertEqual(data["message"], f"404 Not Found: Order with id '{order_id}' was not found.")

    def test_delete_item_incorrect_order(self):
        """It should not delete a item when item with order id can't be found"""
        orders = self._create_orders(2)

        item_0 = OrderItemFactory()
        response = self.app.post(
            f"{BASE_URL}/{orders[0].id}/items",
            json=item_0.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        item_id_order_0 = response.get_json()["id"]

        item_1 = OrderItemFactory()
        response = self.app.post(
            f"{BASE_URL}/{orders[1].id}/items",
            json=item_1.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        item_id_order_1 = response.get_json()["id"]

        # make sure item exists before delete
        response = self.app.get(f"{BASE_URL}/{orders[0].id}/items/{item_id_order_0}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.app.get(f"{BASE_URL}/{orders[1].id}/items/{item_id_order_1}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # delete the item belong to incorrect order
        response = self.app.delete(f"{BASE_URL}/{orders[0].id}/items/{item_id_order_1}",)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # make sure both the items still exist
        response = self.app.get(f"{BASE_URL}/{orders[0].id}/items/{item_id_order_0}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.app.get(f"{BASE_URL}/{orders[1].id}/items/{item_id_order_1}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_item(self):
        """It should Update an item"""
        order = self._create_orders(1)[0]
        item = OrderItemFactory()

        # add item
        resp = self.app.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        item.id = data["id"]
        self.assertIsNotNone(data["id"])
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["price"], item.price)

        # update item order id
        updated_item = OrderItemFactory()
        updated_item.order_id = item.order_id
        updated_item.id = item.id
        resp = self.app.put(
            f"{BASE_URL}/{order.id}/items/{item.id}",
            json=updated_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp_item = resp.get_json()
        self.assertIsNotNone(resp_item["id"], item.id)
        self.assertEqual(resp_item["order_id"], order.id)
        self.assertEqual(resp_item["product_id"], updated_item.product_id)
        self.assertEqual(resp_item["quantity"], updated_item.quantity)
        self.assertEqual(resp_item["price"], updated_item.price)

        # make sure item updated using get
        resp = self.app.get(
            f"{BASE_URL}/{order.id}/items/{item.id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp_item = resp.get_json()
        self.assertIsNotNone(resp_item["id"], item.id)
        self.assertEqual(resp_item["order_id"], order.id)
        self.assertEqual(resp_item["product_id"], updated_item.product_id)
        self.assertEqual(resp_item["quantity"], updated_item.quantity)
        self.assertEqual(resp_item["price"], updated_item.price)

    ######################################################################
    #  I T E M  -  T E S T   S A D   P A T H S
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

    def test_update_item_not_found(self):
        """It should not Update an item given wrong order id and non-existent item"""
        order = self._create_orders(1)[0]
        item_id = 4

        # update non-existent item id
        item_data = OrderItemFactory()
        response = self.app.put(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            json=item_data.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertEqual(data["message"], f"404 Not Found: Item with id '{item_id}' was not found.")

    def test_update_item_nonexistent_order(self):
        """It should not Update an item given wrong order id"""
        order = self._create_orders(1)[0]
        item = OrderItemFactory()
        item.order_id = order.id

        # add item
        resp = self.app.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update item with wrong order id
        updated_item = OrderItemFactory()
        updated_item.order_id = item.order_id + 123
        updated_item.id = item.id
        resp = self.app.put(
            f"{BASE_URL}/{updated_item.order_id}/items/{updated_item.id}",
            json=updated_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        self.assertEqual(data["message"], f"404 Not Found: Order with id '{updated_item.order_id}' was not found.")

    def test_update_item_changed_id(self):
        """It should not Update an item's order id and item id"""
        order = self._create_orders(1)[0]
        item = OrderItemFactory()

        # add item
        resp = self.app.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()

        # update item order id
        updated_item = OrderItemFactory()
        updated_item.order_id = data["order_id"] + 1
        updated_item.id = data["id"] + 2
        resp = self.app.put(
            f"{BASE_URL}/{order.id}/items/{data['id']}",
            json=updated_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # make sure item NOT updated using get
        resp = self.app.get(
            f"{BASE_URL}/{order.id}/items/{data['id']}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp_item = resp.get_json()
        self.assertIsNotNone(resp_item["id"], item.id)
        self.assertEqual(resp_item["order_id"], order.id)
        self.assertEqual(resp_item["product_id"], updated_item.product_id)
        self.assertEqual(resp_item["quantity"], updated_item.quantity)
        self.assertEqual(resp_item["price"], updated_item.price)
