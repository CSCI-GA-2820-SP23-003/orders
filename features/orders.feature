Feature: The order service back-end
    As an Order Manager
    I need a RESTful catalog service
    So that I can keey track of all my orders

    Background:
        Given the following orders:
            | Customer ID | Status    |
            | 5           | CONFIRMED |
            | 9           | SHIPPED   |
            | 2           | DELIVERED |
            | 2           | CANCELLED |
        Given the following items:
            | Product ID | Price | Quantity |
            | 233        | 31    | 42       |
            | 101        | 7     | 8        |
            | 151        | 11    | 12       |


    Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Orders RESTful Service" in the title
        And I should not see "404 Not Found"

    Scenario: Create an Order
        When I visit the "Home Page"
        And I set the "Customer ID" to "5"
        And I select "Shipped" in the "Status" dropdown
        And I press the "Create" button
        Then I should see the message "Success"
        And I should see "Today's date" in the "Created On" field
        And I should see "Today's date" in the "Updated On" field
        When I copy the "ID" field
        And I press the "Clear" button
        Then the "ID" field should be empty
        And the "Customer ID" field should be empty
        And the "Created On" field should be empty
        And the "Updated On" field should be empty
        When I paste the "ID" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "5" in the "Customer ID" field
        And I should see "Shipped" in the "status" dropdown
        And I should see "Today's date" in the "Created On" field
        And I should see "Today's date" in the "Updated On" field

    Scenario: Retrieve an Order
        When I visit the "Home Page"
        And I press the "Clear" button
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "CONFIRMED" in the "Search" results
        When I copy the "ID" field
        And I press the "Clear" button
        Then the "ID" field should be empty
        And the "Customer ID" field should be empty
        And the "Created On" field should be empty
        And the "Updated On" field should be empty
        When I paste the "ID" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "5" in the "Customer ID" field
        And I should see "Confirmed" in the "status" dropdown
        And I should see "Today's date" in the "Created On" field
        And I should see "Today's date" in the "Updated On" field

    Scenario: List all Orders
        When I visit the "Home Page"
        And I press the "Clear" button
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "CONFIRMED" in the "Search" results
        And I should see "SHIPPED" in the "Search" results
        And I should see "DELIVERED" in the "Search" results
        And I should see "CANCELLED" in the "Search" results
        And I should not see "IN_PROGRESS" in the "Search" results

    Scenario: Update an Order
        When I visit the "Home Page"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "CONFIRMED" in the "Search" results
        When I copy the "ID" field
        And I press the "Clear" button
        Then the "ID" field should be empty
        When I paste the "ID" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "5" in the "Customer ID" field
        And I should see "Confirmed" in the "status" dropdown
        When I change "Customer ID" to "6"
        And I select "Shipped" in the "status" dropdown
        And I press the "Update" button
        Then I should see the message "Success"
        And I should see "6" in the "Customer ID" field
        And I should see "Shipped" in the "status" dropdown
        And I should see "Today's date" in the "Updated On" field
        When I copy the "ID" field
        And I press the "Clear" button
        Then the "ID" field should be empty
        When I paste the "ID" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "6" in the "Customer ID" field
        And I should see "Shipped" in the "status" dropdown
        And I should see "Today's date" in the "Updated On" field

    Scenario: Cancel an Order
        When I visit the "Home Page"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "5" in the "Customer ID" field
        And I should see "Confirmed" in the "status" dropdown
        When I copy the "ID" field
        And I press the "Clear" button
        Then the "ID" field should be empty
        And the "Customer ID" field should be empty
        And the "Created On" field should be empty
        And the "Updated On" field should be empty
        When I paste the "ID" field
        And I press the "Cancel" button
        Then I should see the message "Order has been CANCELLED!"
        And I should see "5" in the "Customer ID" field
        And I should see "Cancelled" in the "status" dropdown
        And I should see "Today's date" in the "Updated On" field
        When I copy the "ID" field
        And I press the "Clear" button
        And I paste the "ID" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "5" in the "Customer ID" field
        And I should see "Cancelled" in the "status" dropdown
        And I should see "Today's date" in the "Updated On" field


    Scenario: Delete an Order
        When I visit the "Home Page"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "5" in the "Customer ID" field
        When I copy the "ID" field
        And I press the "Clear" button
        Then the "ID" field should be empty
        And the "Customer ID" field should be empty
        And the "Created On" field should be empty
        And the "Updated On" field should be empty
        When I paste the "ID" field
        And I press the "Delete" button
        Then I should see the message "Order has been Deleted!"
        When I press the "Retrieve" button
        Then I should see the message "not found"
        And the "Customer ID" field should be empty
        And the "Created On" field should be empty
        And the "Updated On" field should be empty

    Scenario: Search for Customers
        When I visit the "Home Page"
        And I set the "Customer ID" to "5"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "5" in the "Customer ID" field
        And I should see "CONFIRMED" in the "Search" results
        And I should not see "SHIPPED" in the "Search" results
        And I should not see "DELIVERED" in the "Search" results
        And I should not see "CANCELLED" in the "Search" results
        And I should not see "9" in the "Customer ID" field
        And I should not see "2" in the "Customer ID" field

    Scenario: Search for Order Status
        When I visit the "Home Page"
        And I select "Shipped" in the "Status" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "SHIPPED" in the "Search" results
        And I should not see "CONFIRMED" in the "Search" results
        And I should not see "DELIVERED" in the "Search" results
        And I should not see "CANCELLED" in the "Search" results
        And I should not see "IN_PROGRESS" in the "Search" results

    Scenario: Search for Product ID
        When I visit the "Home Page"
        And I press the "Clear" button
        And I set the "Search Product ID" to "233"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "233" in every row of column "Product ID" in "Search" results
        And I should see "5" in every row of column "Customer ID" in "Search" results
        And I should see "CONFIRMED" in every row of column "Status" in "Search" results
        And I should not see "2" in every row of column "Customer ID" in "Search" results
        And I should not see "9" in every row of column "Customer ID" in "Search" results
