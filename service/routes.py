"""
Orders Service with Swagger

Paths:
------
GET / - Displays a UI for Selenium testing
GET /orders - Returns a list all of the Orders
GET /orders/{id} - Returns the Order with a given id number
POST /orders - creates a new Order record in the database
PUT /orders/{id} - updates an Order record in the database
DELETE /orders/{id} - deletes an Order record in the database

GET /orders/{order_id}/items - Returns a list all of the Items of the given Order id
GET /orders/{order_id}/items/{item_id} - Returns the Order Item with a given id number
POST /orders/{order_id}/items - creates a new Order Item record in the database
PUT /orders/{order_id}/items/{item_id} - updates an Order Item record in the database
DELETE /orders/{order_id}/items/{item_id} - deletes an Order Item record in the database
"""

from flask import jsonify
from flask_restx import Resource, fields, reqparse
from service.common import status  # HTTP Status Codes
# pylint: disable=cyclic-import
from service.models import Order, OrderItem, OrderStatus

# Import Flask application
from . import app, api

# Models
item_create_model = api.model('ItemCreate', {
    'product_id': fields.Integer(required=True, min=0,
                                 description='ID of the product that was purchased'),
    'quantity': fields.Integer(required=True, min=1,
                               description='The quantity of the product purchased'),
    'price': fields.Float(required=True, min=0,
                          description='The price at which the product was purchased'),
})

item_model = api.inherit(
    'Item',
    item_create_model,
    {
        'order_id': fields.Integer(readOnly=True,
                                   description='The order in which the product was purchased'),
        'id': fields.Integer(readOnly=True,
                             description='The unique id assigned internally by service'),
        'created_on': fields.Date(readOnly=True, description='The day the order item was created'),
        'updated_on': fields.Date(readOnly=True, description='The day the order item was updated')
    },
)

order_core_model = api.model('OrderCore', {
    'customer_id': fields.Integer(required=True, min=0,
                                  description='ID of the customer who placed the order'),
    'status': fields.String(enum=[s.name for s in OrderStatus], description='The status of the order'),
})

order_create_model = api.inherit(
    'OrderCreate',
    order_core_model,
    {
        'items': fields.List(fields.Nested(item_create_model),
                             required=False,
                             description='The product items that the order contains'),
    }
)

order_model = api.inherit(
    'Order',
    order_core_model,
    {
        'items': fields.List(fields.Nested(item_model),
                             required=False,
                             description='The product items that the order contains'),
        'id': fields.Integer(readOnly=True,
                             description='The unique id assigned internally by service'),
        'created_on': fields.Date(readOnly=True, description='The day the order was created'),
        'updated_on': fields.Date(readOnly=True, description='The day the order was updated')
    }
)

# Query string arguments
order_args = reqparse.RequestParser()
order_args.add_argument('customer_id', type=int, required=False, help='List orders of a customer')
order_args.add_argument('status', type=str, required=False, help='List orders by status')
order_args.add_argument('product_id', type=int, required=False, help='List orders containing a particular product')


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """Base URL for our service"""
    return app.send_static_file('index.html')


######################################################################
# HEALTH ENDPOINT
######################################################################
@app.route('/health')
def health():
    """ Health check for Kubernetes"""
    return jsonify({"status": "OK"}), status.HTTP_200_OK


######################################################################
#  PATH: /orders/{id}
######################################################################
@api.route('/orders/<int:order_id>')
@api.param('order_id', 'The Order identifier')
class OrderResource(Resource):
    """
    OrderResource class

    Allows the manipulation of a single Order
    GET /orders/{id} - Returns an Order with the id
    PUT /orders/{id} - Updates an Order with the id
    DELETE /orders/{id} - Deletes an order with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE AN ORDER
    # ------------------------------------------------------------------
    @api.doc('get_orders')
    @api.response(404, 'Order not found')
    @api.marshal_with(order_model)
    def get(self, order_id):
        """
        Retrieve a single Order

        This endpoint will return an Order based on its ID.
        """
        app.logger.info('Request for order with id: %s', order_id)
        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")
        app.logger.info('Returning order: %s', order.id)
        return order.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING ORDER
    # ------------------------------------------------------------------
    @api.doc('update_orders')
    @api.response(404, 'Order not found')
    @api.response(400, 'The posted Order data was not valid')
    @api.expect(order_model)
    @api.marshal_with(order_model)
    def put(self, order_id):
        """
        Update an Order

        This endpoint will update an Order based on the body that is posted.
        """
        app.logger.info('Request to update order with id: %s', order_id)
        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

        data = api.payload
        if 'items' in data:
            del data['items']
        order.deserialize(data)
        order.id = order_id
        order.update()

        app.logger.info('Order with ID [%s] updated.', order.id)
        return order.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN ORDER
    # ------------------------------------------------------------------
    @api.doc('delete_orders')
    @api.response(204, 'Order deleted')
    def delete(self, order_id):
        """
        Delete an Order

        This endpoint will delete an Order based on the id specified in the path.
        """
        app.logger.info('Request to delete order with id: %s', order_id)
        order = Order.find(order_id)
        if order:
            order.delete()
            app.logger.info('Order with ID [%s] delete complete.', order_id)
        return '', status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /orders
######################################################################
@api.route('/orders', strict_slashes=False)
class OrderCollection(Resource):
    """ Handles all interactions with collections of Orders """
    # ------------------------------------------------------------------
    # LIST ALL ORDERS
    # ------------------------------------------------------------------
    @api.doc('list_orders')
    @api.response(400, 'Invalid order status')
    @api.expect(order_args, validate=True)
    @api.marshal_list_with(order_model)
    def get(self):
        """
        List all of the Orders

        This endpoint will return all the orders matching the specified criteria.
        """
        app.logger.info('Request to list Orders...')
        orders = []
        args = order_args.parse_args()
        if args['customer_id']:
            app.logger.info('Filtering by customer id: %s', args['customer_id'])
            orders = Order.find_by_customer(args['customer_id'])
        elif args['status']:
            if args['status'] not in OrderStatus.__members__:
                abort(status.HTTP_400_BAD_REQUEST, f"Invalid status '{args['status']}'.")
            app.logger.info('Filtering by order status: %s', args['status'])
            orders = Order.find_by_status(OrderStatus[args['status']])
        elif args['product_id']:
            app.logger.info('Filtering by product id: %s', args['product_id'])
            orders = Order.find_by_product(args['product_id'])
        else:
            app.logger.info('Returning unfiltered list...')
            orders = Order.all()

        results = [order.serialize() for order in orders]
        app.logger.info('[%s] Orders returned', len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW ORDER
    # ------------------------------------------------------------------
    @api.doc('create_orders')
    @api.response(400, 'The posted data was not valid')
    @api.expect(order_create_model)
    @api.marshal_with(order_model, code=201)
    def post(self):
        """
        Creates an Order

        This endpoint will create an Order based on the data in the body that is posted.
        """
        app.logger.info('Request to Create an Order')
        order = Order()
        order.deserialize(api.payload)
        order.create()
        location_url = api.url_for(OrderResource, order_id=order.id, _external=True)
        app.logger.info('Order with ID [%s] created.', order.id)
        return order.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /orders/{id}/cancel
######################################################################
@api.route('/orders/<int:order_id>/cancel')
@api.param('order_id', 'The Order identifier')
class CancelOrderResource(Resource):
    """ Cancel action on an Order """
    @api.doc('cancel_orders')
    @api.response(404, 'Order not found')
    @api.response(409, 'Order cannot be cancelled')
    def put(self, order_id):
        """
        Cancel an Order

        This endpoint will cancel an Order by ID.
        """
        app.logger.info('Request to cancel order with order_id: [%s]', order_id)
        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")
        # If order status passed Shipped, then we set to conflict
        if order.status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED):
            abort(
                status.HTTP_409_CONFLICT,
                f"Order with id {order_id} is {order.status.name}, request conflicted.")
        if order.status == OrderStatus.CANCELLED:
            abort(
                status.HTTP_409_CONFLICT,
                f"Order with id {order_id} is already cancelled.")
        order.status = OrderStatus.CANCELLED
        order.update()
        app.logger.info('Order with id [%s] has been cancelled.', order.id)
        return order.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /orders/{order_id}/items/{item_id}
######################################################################
@api.route('/orders/<int:order_id>/items/<int:item_id>')
@api.param('order_id', 'The Order identifier')
@api.param('item_id', 'The Order Item identifier')
class OrderItemResource(Resource):
    """
    ItemResource class

    Allows the manipulation of a single Order Item
    GET /orders/{order_id}/items/{item_id} - Returns an Order Item with the id
    PUT /orders/{order_id}/items/{item_id} - Update an Order Item with the id
    DELETE /orders/{order_id}/items/{item_id} -  Deletes an Order Item with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE AN ORDER ITEM
    # ------------------------------------------------------------------
    @api.doc('get_order_items')
    @api.response(404, 'Order Item not found')
    @api.marshal_with(item_model)
    def get(self, order_id, item_id):
        """
        Retrieve an order item

        This endpoint will return an item from an order based on its ID.
        """
        app.logger.info('Request to retrieve an Item %s from Order with id: %s', item_id, order_id)
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )
        item = OrderItem.find_by_order_and_item_id(order_id, item_id)
        if not item:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item with id '{item_id}' was not found.",
            )
        app.logger.info('Returning order item: %s', item.id)
        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING ORDER ITEM
    # ------------------------------------------------------------------
    @api.doc('update_order_items')
    @api.response(404, 'Order Item not found')
    @api.response(400, 'The posted Order Item data was not valid')
    @api.expect(item_model)
    @api.marshal_with(item_model)
    def put(self, order_id, item_id):
        """
        Update an item from an order

        This endpoint will update an Order Item based on the body that is posted.
        """
        app.logger.info('Request to update item with order_id [%s] and item_id [%s] ...', order_id, item_id)

        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

        item = OrderItem.find_by_order_and_item_id(order_id, item_id)
        if not item:
            abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")

        data = api.payload
        item.deserialize(data)
        item.id = item_id
        item.order_id = order_id
        item.update()

        app.logger.info('Item with order_id [%s] and item_id [%s] updated.', order.id, item.id)
        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN ORDER ITEM
    # ------------------------------------------------------------------
    @api.doc('delete_order_items')
    @api.response(204, 'Order Item deleted')
    def delete(self, order_id, item_id):
        """
        Delete an item from an order

        This endpoint will delete an Order Item based on the id specified in the path.
        """
        app.logger.info('Request to delete item with order_id [%s] and item_id [%s] ...', item_id, order_id)

        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

        item = OrderItem.find_by_order_and_item_id(order_id, item_id)
        if item:
            item.delete()
            app.logger.info('Item with ID [%s] and order ID [%s] delete complete.', item_id, order_id)
        return '', status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /orders/{order_id}/items
######################################################################
@api.route('/orders/<int:order_id>/items', strict_slashes=False)
@api.param('order_id', 'The Order identifier')
class OrderItemCollection(Resource):
    """ Handles all interactions with collections of Order Items """
    # ------------------------------------------------------------------
    # LIST ALL ITEMS FOR AN ORDER
    # ------------------------------------------------------------------
    @api.doc('list_order_items')
    @api.marshal_list_with(item_model)
    def get(self, order_id):
        """
        List all of the Items from an Order

        This endpoint will return all the Items by Order ID.
        """
        app.logger.info('Request to list Items for Order with id: %s', order_id)
        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

        results = [item.serialize() for item in order.items]
        app.logger.info("Returning %d items", len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW ITEM TO AN ORDER
    # ------------------------------------------------------------------
    @api.doc('create_order_items')
    @api.response(400, 'The posted data was not valid')
    @api.expect(item_create_model)
    @api.marshal_with(item_model, code=201)
    def post(self, order_id):
        """
        Create an item on an order

        This endpoint will add a new item to an order.
        """
        app.logger.info('Request to create an Item for Order with id: %s', order_id)
        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

        item = OrderItem()
        item.deserialize(api.payload)
        item.order_id = order_id
        item.create()

        location_url = api.url_for(OrderItemResource, order_id=order.id, item_id=item.id, _external=True)
        app.logger.info('Item with ID [%s] created for order: [%s].', item.id, order.id)
        return item.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)
