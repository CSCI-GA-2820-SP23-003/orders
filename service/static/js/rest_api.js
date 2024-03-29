$(function () {
    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_id").val(res.id);
        $("#order_customer_id").val(res.customer_id);
        $("#order_status").val(res.status);
        $("#order_created_on").val(res.created_on);
        $("#order_updated_on").val(res.updated_on);
    }

    // Updates the form with data from the response for the item section
    function update_item_form_data(res) {
        $("#order_item_id").val(res.id);
        $("#order_product_id").val(res.product_id);
        $("#order_price").val(res.price);
        $("#order_quantity").val(res.quantity);
        $("#order_order_id").val(res.order_id);
        $("#order_created_on").val(res.created_on);
        $("#order_updated_on").val(res.updated_on);
    }

    // Clears all form fields
    function clear_form_data() {
        $("#order_customer_id").val("");
        $("#order_status").val("");
        $("#order_created_on").val("");
        $("#order_updated_on").val("");
    }

    // Clears all item form fields
    function clear_item_form_data() {
        $("#order_product_id").val("");
        $("#order_price").val("");
        $("#order_quantity").val("");
        $("#order_item_created_on").val("");
        $("#order_item_updated_on").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create an Order
    // ****************************************

    $("#create-btn").click(function () {

        let customer_id = $("#order_customer_id").val();
        let status = $("#order_status").val();

        if (!customer_id) {
            flash_message("Missing required fields: Customer ID")
            return
        }

        customer_id = parseInt(customer_id, 10)

        let data = {
            "customer_id": customer_id,
            "status": status,
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: "/api/orders",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Retrieve an Order
    // ****************************************

    $("#retrieve-btn").click(function () {

        let order_id = $("#order_id").val();

        if (!order_id) {
            flash_message("Order ID is required for Retrieve Operation")
            return
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/orders/${order_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Search Orders
    // ****************************************

    $("#search-btn").click(function () {

        let customer_id = $("#order_customer_id").val();
        let status = $("#order_status").val();
        let product_id = $("#order_search_product_id").val();

        let queryString = "";

        if (customer_id) {
            queryString += 'customer_id=' + customer_id;
        } else if (status) {
            queryString += 'status=' + status;
        } else if (product_id) {
            queryString += 'product_id=' + product_id;
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/orders?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Customer ID</th>'
            table += '<th class="col-md-2">Status</th>'
            table += '<th class="col-md-2">Product IDs</th>'
            table += '<th class="col-md-2">Created On</th>'
            table += '<th class="col-md-2">Updated On</th>'
            table += '</tr></thead><tbody>'
            let firstOrder = "";
            for (let i = 0; i < res.length; i++) {
                let order = res[i];
                item_product_ids = order.items.map(item => item.product_id).join(',');
                table += `<tr id="row_${i}"><td>${order.id}</td><td>${order.customer_id}</td><td>${order.status}</td><td>${item_product_ids}</td><td>${order.created_on}</td><td>${order.updated_on}</td></tr>`;
                if (i == 0) {
                    firstOrder = order;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstOrder != "") {
                update_form_data(firstOrder)
            }
            else{
                $("#order_id").val("");
                $("#order_created_on").val("");
                $("#order_updated_on").val("");
            }

            flash_message("Success")
        });

        ajax.fail(function (res) {
            $("#search_results").empty();
            $("#order_id").val("");
            $("#order_created_on").val("");
            $("#order_updated_on").val("");
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Update an Order
    // ****************************************

    $("#update-btn").click(function () {

        let order_id = $("#order_id").val();

        if (!order_id) {
            flash_message("Order ID is required for Update Operation")
            return
        }
        
        let customer_id = $("#order_customer_id").val();
        let status = $("#order_status").val();

        if (!customer_id) {
            flash_message("Missing required fields: Customer ID")
            return
        }

        customer_id = parseInt(customer_id, 10)

        let data = {
            "customer_id": customer_id,
            "status": status
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/orders/${order_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Cancel an Order
    // ****************************************

    $("#cancel-btn").click(function () {

        let order_id = $("#order_id").val();

        if (!order_id) {
            flash_message("Order ID is required for Cancel Operation")
            return
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/orders/${order_id}/cancel`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Order has been CANCELLED!")
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an Order
    // ****************************************

    $("#delete-btn").click(function () {
        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        if (!order_id) {
            flash_message("Order ID is required for Delete Operation")
            return
        }

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/orders/${order_id}`,
            contentType: "application/json"
        })

        ajax.done(function (res) {
            // remove the order from the form and table
            clear_form_data();
            flash_message("Order has been Deleted!")
        });

        ajax.fail(function (res) {
            clear_form_data();
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#order_id").val("");
        $("#order_search_product_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Create an Item
    // ****************************************

    $("#create-item-btn").click(function () {
        let product_id = $("#order_product_id").val();
        let quantity = $("#order_quantity").val();
        let order_id = $("#order_order_id").val();
        let price = $("#order_price").val();

        if (!product_id || !quantity || !order_id || !price) {
            flash_message("Missing required fields")
            return
        }

        product_id = parseInt(product_id, 10)
        quantity = parseInt(quantity, 10)
        price = parseFloat(price, 10)

        let data = {
            "product_id": product_id,
            "quantity": quantity,
            "order_id": order_id,
            "price": price
        };

        $("#flash_message").empty();
        let ajax = $.ajax({
            type: "POST",
            url: "/api/orders/" + order_id + "/items",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_item_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // List Items
    // ****************************************

    $("#list-item-btn").click(function () {

        let order_id = $("#order_order_id").val();

        if (!order_id || order_id == "") {
            clear_item_form_data();
            flash_message("Order ID is required for List Operation")
            return
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/orders/${order_id}/items`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            $("#list_item_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">Item ID</th>'
            table += '<th class="col-md-2">Product ID</th>'
            table += '<th class="col-md-2">Price</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-2">Created On</th>'
            table += '<th class="col-md-2">Updated On</th>'
            table += '</tr></thead><tbody>'
            let firstItem = "";
            for (let i = 0; i < res.length; i++) {
                let item = res[i];
                table += `<tr id="row_${i}"><td>${item.id}</td><td>${item.product_id}</td><td>${item.price}</td><td>${item.quantity}</td><td>${item.created_on}</td><td>${item.updated_on}</td></tr>`;
                if (i == 0) {
                    firstItem = item;
                }
            }
            table += '</tbody></table>';
            $("#list_item_results").append(table);

            // copy the first result to the form
            if (firstItem != "") {
                update_item_form_data(firstItem)
            }
            else{
                $("#order_item_id").val("");
                clear_item_form_data();
            }

            flash_message("Success")
        });

        ajax.fail(function (res) {
            $("#list_item_results").empty();
            $("#order_item_id").val("");
            clear_item_form_data();
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Clear the item form
    // ****************************************

    $("#clear-item-btn").click(function () {
        $("#order_item_id").val("");
        $("#order_order_id").val("");
        $("#flash_message").empty();
        clear_item_form_data()
    });

    // ****************************************
    // Retrieve an Item
    // ****************************************

    $("#retrieve-item-btn").click(function () {

        let item_id = $("#order_item_id").val();
        let order_id = $("#order_order_id").val();

        if (!order_id) {
            flash_message("Order ID is required for Retrieving Item")
            return
        }

        if (!item_id) {
            flash_message("Item ID is required for Retrieve Operation")
            return
        }
        
        var ajax = $.ajax({
            type: "GET",
            url: `/api/orders/${order_id}/items/${item_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            update_item_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_item_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Update an Item
    // ****************************************

    $("#update-item-btn").click(function () {

        let order_id = $("#order_order_id").val();
        let item_id = $("#order_item_id").val();

        if (!order_id) {
            flash_message("Order ID is required for Updating Item")
            return
        }

        if (!item_id) {
            flash_message("Item ID is required for Update Operation")
            return
        }

        let price = $("#order_price").val();
        let quantity = $("#order_quantity").val();
        let product_id = $("#order_product_id").val();

        if (!product_id || !quantity || !price) {
            flash_message("Missing required fields")
            return
        }

        product_id = parseInt(product_id, 10)
        quantity = parseInt(quantity, 10)
        price = parseFloat(price, 10)

        let data = {
            "price": price,
            "quantity": quantity,
            "product_id": product_id
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/orders/${order_id}/items/${item_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_item_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an Item
    // ****************************************

    $("#delete-item-btn").click(function () {
        let order_id = $("#order_order_id").val();
        let item_id = $("#order_item_id").val();

        if (!order_id) {
            flash_message("Order ID is required for Deleting Item")
            return
        }

        if (!item_id) {
            flash_message("Item ID is required for Delete Operation")
            return
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/orders/${order_id}/items/${item_id}`,
            contentType: "application/json"
        })

        ajax.done(function (res) {
            // remove the order from the form and table
            clear_item_form_data();
            flash_message("Item has been Deleted!")
        });

        ajax.fail(function (res) {
            clear_item_form_data();
            flash_message(res.responseJSON.message)
        });
    });
})
