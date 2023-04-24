# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
import logging
import requests
from datetime import date
from behave import given, when, then
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

ORDER_ID_PREFIX = "order_"
ITEM_ID_PREFIX = "item_"


@given('the following orders')
def step_impl(context):
    """ Delete all Orders and load new ones """
    # List all of the orders and delete them one by one
    rest_endpoint = f"{context.BASE_URL}/api/orders"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for order in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{order['id']}")
        expect(context.resp.status_code).to_equal(204)

    # load the database with new orders
    for row in context.table:
        payload = {
            "customer_id": row['Customer ID'],
            "status": row['Status'],
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        expect(context.resp.status_code).to_equal(201)


@when('I visit the "home page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.BASE_URL)


@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)


@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, 'body')
    error_msg = "I should not see '%s' in '%s'" % (text_string, element.text)
    ensure(text_string in element.text, False, error_msg)


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ORDER_ID_PREFIX + element_name.lower().replace(' ', '_')
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)
    
@when('I set the item "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ITEM_ID_PREFIX + element_name.lower().replace(' ', '_')
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ORDER_ID_PREFIX + element_name.lower().replace(' ', '_')
    element = Select(context.driver.find_element_by_id(element_id))
    element.select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ORDER_ID_PREFIX + element_name.lower().replace(' ', '_')
    element = Select(context.driver.find_element_by_id(element_id))
    expect(element.first_selected_option.text).to_equal(text)


@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()
    
@when('I press the item "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + '-item-btn'
    context.driver.find_element_by_id(button_id).click()


@then('I should see "{order_status}" in the results')
def step_impl(context, order_status):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_results'),
            order_status
        )
    )
    expect(found).to_be(True)


@then('I should not see "{order_status}" in the results')
def step_impl(context, order_status):
    element = context.driver.find_element_by_id('search_results')
    error_msg = "I should not see '%s' in '%s'" % (order_status, element.text)
    ensure(order_status in element.text, False, error_msg)


@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'), message)
    )
    expect(found).to_be(True)

@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ORDER_ID_PREFIX + element_name.lower().replace(' ', '_')
    if text_string == "Today's date":
        text_string = date.today().isoformat()
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id), text_string)
    )
    expect(found).to_be(True)


@then('I should not see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ORDER_ID_PREFIX + element_name.lower().replace(' ', '_')
    element = context.driver.find_element_by_id(element_id)
    error_msg = "I should not see '%s' in '%s'" % (text_string, element.text)
    ensure(text_string in element.text, False, error_msg)


@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = ORDER_ID_PREFIX + element_name.lower().replace(' ', '_')
    element = context.driver.find_element_by_id(element_id)
    expect(element.get_attribute('value')).to_be(u'')

##################################################################
# These two function simulate copy and paste
##################################################################


@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ORDER_ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    logging.info('Clipboard contains: %s', context.clipboard)
    

@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ORDER_ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)
    
@when('I paste the item "{element_name}" field')
def step_impl(context, element_name):
    element_id = ITEM_ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ORDER_ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)
