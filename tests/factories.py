"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from service.models import Order, OrderStatus
from datetime import date


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
