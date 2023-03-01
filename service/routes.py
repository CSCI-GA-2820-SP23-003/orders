"""
My Service

Describe what your service does here
"""

from flask import Flask, jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
from service.models import Order

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        "Reminder: return some useful information in json format about the service here",
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
    return jsonify(order.serialize()), status.HTTP_201_CREATED, {"Location": location_url}

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
# List Orders
######################################################################
@app.route("/orders", methods=["GET"])
def list_orders():
    """List all orders in the database

    Returns:
        list: an array of order id
    """
    app.logger.info("Request to list all orders...")
    orders = [order.serialize() for counter in Order.all()]
    return jsonify(counters)


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
