Feature: The order service back-end
    As an Order Manager
    I need a RESTful catalog service
    So that I can keey track of all my items in orders

    Background:
        Given the following orders:
            | Customer ID | Status    |
            | 5           | CONFIRMED |
        Given the following items:
            | Product ID | Price | Quantity |
            | 233        | 31    | 42       |
            | 101        | 7     | 8        |
            | 151        | 11    | 12       |

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
        And I paste the "Order ID" field
        And I set the "Product ID" to "1"
        And I set the "Price" to "5"
        And I set the "Quantity" to "3"
        And I press the "Create Item" button
        Then I should see the message "Success"

    Scenario: List Items
        When I visit the "Home Page"
        And I press the "Clear" button
        And I press the "Search" button
        Then I should see the message "Success"
        When I press the "Clear Item" button
        Then the "Item ID" field should be empty
        When I copy the "ID" field
        And I paste the "Order ID" field
        And I press the "List Item" button
        Then I should see the message "Success"
        And I should see "233" in the "List Item" results
        And I should see "101" in the "List Item" results
        And I should see "151" in the "List Item" results

    Scenario: Update an Item
        When I visit the "Home Page"
        And I press the "Clear" button
        And I press the "Search" button
        Then I should see the message "Success"
        When I press the "Clear Item" button
        Then the "Item ID" field should be empty
        When I copy the "ID" field
        And I paste the "Order ID" field
        And I press the "List Item" button
        Then I should see the message "Success"
        When I set the "Product ID" to "9164"
        And I set the "Price" to "112"
        And I set the "Quantity" to "17"
        And I press the "Update Item" button
        And I press the "List Item" button
        Then I should see "9164" in the "List Item" results
        And I should see "112" in the "List Item" results
        And I should see "17" in the "List Item" results
        And I should not see "31" in the "List Item" results
        And I should not see "42" in the "List Item" results

    Scenario: Delete an Item
        When I visit the "Home Page"
        And I press the "Clear" button
        And I press the "Search" button
        Then I should see the message "Success"
        When I press the "Clear Item" button
        Then the "Item ID" field should be empty
        When I copy the "ID" field
        And I paste the "Order ID" field
        And I press the "List Item" button
        Then I should see the message "Success"
        And I should see "233" in the "List Item" results
        When I press the "Delete Item" button
        And I paste the "Order ID" field
        And I press the "List Item" button
        Then I should not see "233" in the "List Item" results
        
    Scenario: Retrieve an Item
        When I visit the "Home Page"
        And I press the "Search" button
        Then I should see the message "Success"
        When I copy the "ID" field
        And I paste the "Order ID" field
        And I press the "List Item" button
        Then I should see the message "Success"
        When I copy the "Item ID" field
        And I paste the "Item ID" field
        And I press the "Retrieve Item" button
        Then I should see the message "Success"
        And I should see "233" in the "Product ID" field
        And I should see "3" in the "Price" field
        And I should see "4" in the "Quantity" field
