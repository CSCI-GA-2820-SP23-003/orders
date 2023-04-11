Feature: The order service bank-end
    As a Orders Team Member
    I need a RESTful catalog service
    So that I can test order service and BDD test

Background:
    Given the server is started

Scenario: The server is running
    When I visit the "home page"
    Then I should see "Order Demo REST API Service"
    And  I should not see "404 Not Found"