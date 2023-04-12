Feature: The order service back-end
    As an Order Manager
    I need a RESTful catalog service
    So that I can keey track of all my orders

Background:
    Given the following orders:
        | customer_id | status | 
        | 5           | CONFIRMED    |
        | 9           | SHIPPED      |
        | 3           | SHIPPED      |
        | 2           | DELIVERED    |
        | 2           | CANCELLED    |
        | 5           | IN_PROGRESS  |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Order Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create an Order
    When I visit the "Home Page"
    And I set the "Customer ID" to "5"
    And I select "Confirmed" in the "Status" dropdown
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
# #Need retrieve function for complete testing