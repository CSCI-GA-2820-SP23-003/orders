"""
Test Factory to make fake objects for testing
"""
from datetime import date
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from service.models import Order, OrderItem, OrderStatus


class OrderFactory(factory.Factory):
    """Creates fake orders that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""
        model = Order

    id = factory.Sequence(lambda n: n)
    customer_id = factory.Sequence(lambda n: n)
    status = FuzzyChoice(choices=[
                         OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED])
    created_on = FuzzyDate(date(2008, 1, 1))
    updated_on = FuzzyDate(date(2008, 1, 1))
    items = []


class OrderItemFactory(factory.Factory):
    """Creates fake order items that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""
        model = OrderItem

    id = factory.Sequence(lambda n: n)
    product_id = factory.Sequence(lambda n: n)
    quantity = factory.Sequence(lambda n: n)
    price = factory.Sequence(lambda n: n*100)
    order_id = factory.Sequence(lambda n: n)
    created_on = FuzzyDate(date(2008, 1, 1))
    updated_on = FuzzyDate(date(2008, 1, 1))
