"""
Models for Orders Service

All of the models are stored in this module

Models
------
Order - An order placed by a customer

Attributes:
-----------
customer id (number) - id of the customer placing the order
status (string) - status of the order

Order Item

Attributes:
-----------
product id (number) - id of the product
quantity (number) - quantity of the item
price (number) - price of the product
order id (number) - id of the order containing the item
"""

import logging
from enum import Enum
from datetime import date
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """ Initializes the SQLAlchemy app """
    Order.init_db(app)
    OrderItem.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


class OrderStatus(Enum):
    """Enumeration of valid Order Statuses"""

    CONFIRMED = 0
    IN_PROGRESS = 1
    SHIPPED = 3
    DELIVERED = 4
    CANCELLED = 5


class Order(db.Model):
    """
    Class that represents an Order

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    app = None

    ##################################################
    # Table Schema
    ##################################################

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    status = db.Column(
        db.Enum(OrderStatus), nullable=False, server_default=(OrderStatus.CONFIRMED.name)
    )
    items = db.relationship('OrderItem', backref='order',
                            cascade="all, delete", lazy=True)
    created_on = db.Column(db.Date(), nullable=False, default=date.today())
    updated_on = db.Column(db.Date(), nullable=False, default=date.today())

    ##################################################
    # INSTANCE METHODS
    ##################################################

    def __repr__(self):
        return f"<Order: id={self.id}, customer_id={self.customer_id}, status={self.status}>"

    def create(self):
        """
        Creates an Order to the database
        """
        logger.info("Creating order of customer# %s", self.customer_id)
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates an Order to the database
        """
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        logger.info("Saving order# %s", self.id)
        db.session.commit()

    def delete(self):
        """ Removes an Order from the data store """
        logger.info("Deleting order# %s", self.id)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes an Order into a dictionary """
        items: list = []
        for item in self.items:
            items.append(OrderItem.serialize(item))
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "status": self.status.name,  # convert enum to string
            "items": items,
            "created_on": self.created_on.isoformat(),
            "updated_on": self.updated_on.isoformat()
        }

    def deserialize(self, data):
        """
        Deserializes an Order from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            if "id" in data:
                self.id = data["id"]
            self.customer_id = data["customer_id"]
            if "status" in data:
                self.status = getattr(OrderStatus, data["status"])
            else:
                self.status = OrderStatus.CONFIRMED
            self.items = []
            if "items" in data:
                for item in data["items"]:
                    self.items.append(OrderItem().deserialize(item))
            self.updated_on = date.today()
        except AttributeError as error:
            raise DataValidationError(
                "Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Order: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Order: body of request contained bad or no data - "
                "Error message: " + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def init_db(cls, app: Flask):
        """Initializes the database session

        :param app: the Flask app
        :type data: Flask

        """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls) -> list:
        """ Returns all of the Orders in the database """
        logger.info("Processing all Orders")
        return cls.query.all()

    @classmethod
    def find(cls, order_id: int):
        """Finds an Order by it's ID

        :param order_id: the id of the Order to find
        :type order_id: int

        :return: an instance with the order_id, or None if not found
        :return type: Order

        """
        logger.info("Processing lookup for order id %s ...", order_id)
        return cls.query.get(order_id)

    @classmethod
    def find_or_404(cls, order_id: int):
        """Find an Order by it's id

        :param order_id: the id of the Order to find
        :type order_id: int

        :return: an instance with the order_id, or 404_NOT_FOUND if not found
        :return type: Order

        """
        logger.info("Processing lookup or 404 for order id %s ...", order_id)
        return cls.query.get_or_404(order_id)


class OrderItem(db.Model):
    """
    Class that represents an Order Item

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    app = None

    ##################################################
    # Table Schema
    ##################################################

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Double, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    created_on = db.Column(db.Date(), nullable=False, default=date.today())
    updated_on = db.Column(db.Date(), nullable=False, default=date.today())

    ##################################################
    # INSTANCE METHODS
    ##################################################

    def __repr__(self):
        return f"<Order Item: id={self.id}, order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity}>"

    def create(self):
        """
        Creates an Order Item to the database
        """
        logger.info("Creating item of order# %s", self.order_id)
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates an Order Item to the database
        """
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        logger.info("Saving order item# %s", self.id)
        db.session.commit()

    def delete(self):
        """ Removes an Order Item from the data store """
        logger.info("Deleting order item# %s", self.id)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes an Order into a dictionary """
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,  # convert enum to string
            "price": self.price,
            "order_id": self.order_id,
            "created_on": self.created_on.isoformat(),
            "updated_on": self.updated_on.isoformat()
        }

    def deserialize(self, data):
        """
        Deserializes an Order from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            if "id" in data:
                self.id = data["id"]
            self.product_id = data["product_id"]
            self.quantity = data["quantity"]
            self.price = data["price"]
            if "order_id" in data:
                self.order_id = data["order_id"]
            self.updated_on = date.today()
        except KeyError as error:
            raise DataValidationError(
                "Invalid Order: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Order: body of request contained bad or no data - "
                "Error message: " + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def init_db(cls, app: Flask):
        """Initializes the database session

        :param app: the Flask app
        :type data: Flask

        """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls) -> list:
        """ Returns all of the Order Items in the database """
        logger.info("Processing all Order Items")
        return cls.query.all()

    @classmethod
    def find(cls, item_id: int):
        """Finds an Order Item by it's ID

        :param item_id: the id of the item to find
        :type item_id: int

        :return: an instance with the item_id, or None if not found
        :return type: Order Item

        """
        logger.info("Processing lookup for item id %s ...", item_id)
        return cls.query.get(item_id)

    @classmethod
    def find_or_404(cls, item_id: int):
        """Find an Order Item by it's id

        :param item_id: the id of the Order Item to find
        :type item_id: int

        :return: an instance with the item_id, or 404_NOT_FOUND if not found
        :return type: Order Item

        """
        logger.info("Processing lookup or 404 for item id %s ...", item_id)
        return cls.query.get_or_404(item_id)
