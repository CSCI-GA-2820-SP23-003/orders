Feature: The order service back-end
    As an Order Manager
    I need a RESTful catalog service
    So that I can keey track of all my items in orders

    Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Orders RESTful Service" in the title
        And I should not see "404 Not Found"

    Scenario: Create an Item
        When I visit the "Home Page"
        And I set the "Customer ID" to "5"
        And I select "Confirmed" in the "Status" dropdown
        And I press the "Create" button
        Then I should see the message "Success"
        When I copy the "ID" field
        And I paste the item "Order ID" field
        And I set the item "Product ID" to "1"
        And I set the item "Price" to "5"
        And I set the item "Quantity" to "3"
        And I press the item "Create" button
        Then I should see the message "Success"
