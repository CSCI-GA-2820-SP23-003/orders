"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
# pylint: disable=cyclic-import
from service.models import Order, OrderItem, OrderStatus

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        jsonify(
            name="Order REST API Service",
            version="1.0",
            paths=url_for("list_orders", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# ADD A NEW ORDER
######################################################################
@app.route("/orders", methods=["POST"])
def create_order():
    """
    Creates an Order
    This endpoint will create an Order based on the data in the body that is posted
    """
    app.logger.info("Request to create an order")
    check_content_type("application/json")
    order = Order()
    order.deserialize(request.get_json())
    order.create()
    location_url = url_for("get_order", order_id=order.id, _external=True)
    app.logger.info("Order with ID [%s] created.", order.id)
    return make_response(jsonify(order.serialize()), status.HTTP_201_CREATED, {"Location": location_url})


######################################################################
# GET AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    """
    Read a single Order
    This endpoint will return a Order based on it's id
    """
    app.logger.info("Request for order with id: %s", order_id)
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")
    app.logger.info("Returning order: %s", order.id)
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


######################################################################
# LIST ALL ORDERS
######################################################################
@app.route("/orders", methods=["GET"])
def list_orders():
    """List all of the Orders"""
    app.logger.info("Request for order list")
    orders = []

    customer_id = request.args.get("customer_id")
    order_status = request.args.get("status")
    product_id = request.args.get("product_id")

    if customer_id:
        app.logger.info("Request for query by customer id: %s", customer_id)
        orders = Order.find_by_customer(int(customer_id))
    elif order_status:
        if order_status not in OrderStatus.__members__:
            abort(status.HTTP_400_BAD_REQUEST, f"Invalid status '{order_status}'.")
        app.logger.info("Request for query by status: %s", order_status)
        orders = Order.find_by_status(OrderStatus[order_status])
    elif product_id:
        app.logger.info("Request for query by product id: %s", product_id)
        orders = Order.find_by_product(int(product_id))
    else:
        orders = Order.all()

    results = [order.serialize() for order in orders]
    app.logger.info("Returning %d orders", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# UPDATE AN EXISTING ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    """
    Update an Order

    This endpoint will update an Order based on the body that is posted
    """
    app.logger.info("Request to update order with id: %s", order_id)
    check_content_type("application/json")

    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    data = request.get_json()
    if "items" in data:
        del data["items"]
    order.deserialize(data)
    order.id = order_id
    order.update()

    app.logger.info("Order with ID [%s] updated.", order.id)
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    """
    Delete an Order

    This endpoint will delete an Order based on the id specified in the path
    """
    app.logger.info("Request to delete order with id: %s", order_id)
    order = Order.find(order_id)
    if order:
        order.delete()
        app.logger.info("Order with ID [%s] delete complete.", order_id)
    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# ADD AN ITEM TO AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items", methods=["POST"])
def create_item(order_id):
    """
    Create an item on an order
    This endpoint will add an item to an order
    """
    app.logger.info("Request to create an Item for Order with id: %s", order_id)
    check_content_type("application/json")

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' was not found.",
        )

    # Create an item from the json data
    item = OrderItem()
    item.deserialize(request.get_json())

    # Append the item to the order
    order.items.append(item)
    order.update()

    # Prepare a message to return
    message = item.serialize()
    location_url = url_for("get_item", order_id=order_id, item_id=item.id, _external=True)

    return make_response(jsonify(message), status.HTTP_201_CREATED, {"Location": location_url})


######################################################################
# LIST ALL ITEMS FROM AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items", methods=["GET"])
def list_items(order_id):
    """List all of the Items from Order"""
    app.logger.info("Request to list Items for Order with id: %s", order_id)

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")
    # Create an item from the json data
    results = [item.serialize() for item in order.items]
    app.logger.info("Returning %d items", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# RETRIEVE AN ITEM FROM AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["GET"])
def get_item(order_id, item_id):
    """
    Retrieve an item from an order
    """
    app.logger.info("Request to read an Item %s from Order with id: %s", item_id, order_id)

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' was not found.",
        )

    # Read an item with item_id
    result = OrderItem.find_by_order_and_item_id(order_id, item_id)
    if not result:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' was not found.",
        )

    # Prepare a message to return
    message = result.serialize()
    return make_response(jsonify(message), status.HTTP_200_OK)


######################################################################
# DELETE AN ITEM FROM AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def delete_item(order_id, item_id):
    """
    Delete an item from an order
    """
    app.logger.info(
        "Request to delete an Item %s from Order with id: %s", item_id, order_id)

    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' was not found.",
        )

    item = OrderItem.find_by_order_and_item_id(order_id, item_id)
    if item:
        item.delete()
        app.logger.info(
                "Item with ID [%s] and order ID [%s] delete complete.", item_id, order_id)
    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# UPDATE AN ITEM FROM AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["PUT"])
def update_item(order_id, item_id):
    """
    Update an item from an order
    """
    app.logger.info("Request to update an Item %s from Order with id: %s", item_id, order_id)
    check_content_type("application/json")

    # See if the order exists and abort if it doesn't
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' was not found.",
        )

    # Read an item with item_id
    item = OrderItem.find_by_order_and_item_id(order_id, item_id)
    if not item:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' was not found.",
        )

    data = request.get_json()
    item.deserialize(data)
    item.id = item_id
    item.order_id = order_id
    item.update()
    # Prepare a message to return
    message = item.serialize()
    return make_response(jsonify(message), status.HTTP_200_OK)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
