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
import re

ID_PREFIX = "order_"


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
            "customer_id": int(row['Customer ID']),
            "status": row['Status'],
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        expect(context.resp.status_code).to_equal(201)


@given('the following items')
def step_impl(context):
    """ Load all items to the first order """
    # Get the first order
    rest_endpoint = f"{context.BASE_URL}/api/orders"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    order = context.resp.json()[0]
    items_route = f"{rest_endpoint}/{order['id']}/items"
    # Add the new items in the table
    for row in context.table:
        payload = {
            "product_id": int(row['Product ID']),
            "price": float(row['Price']),
            "quantity": int(row['Quantity'])
        }
        context.resp = requests.post(items_route, json=payload)
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
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = Select(context.driver.find_element_by_id(element_id))
    element.select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = Select(context.driver.find_element_by_id(element_id))
    expect(element.first_selected_option.text).to_equal(text)


@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower().replace(' ', '-') + '-btn'
    context.driver.find_element_by_id(button_id).click()

def get_column_values(context, tablename, column_name):
    tablename = tablename.lower().replace(' ', '_') + '_results'
    element = context.driver.find_element_by_id(tablename)

    # Get the index of the column with the specified name
    headers = element.find_elements_by_tag_name('th')
    column_index = -1
    for i, header in enumerate(headers):
        if header.text.strip() == column_name:
            column_index = i
            break

    # Check if the column with the specified name was found
    assert column_index != -1, f'Column with name "{column_name}" not found in table'
    return [row.find_elements_by_tag_name('td')[column_index].text for row in element.find_elements_by_tag_name('tr')[1:]]

@then('I should see "{value}" in every row of column "{column_name}" in "{tablename}" results')
def step_impl(context, value, column_name, tablename):
    cell_values = get_column_values(context, tablename, column_name)
    expect(all([value in cell.split(',') if ',' in cell else value == cell for cell in cell_values])).to_be(True)

@then('I should not see "{value}" in every row of column "{column_name}" in "{tablename}" results')
def step_impl(context, value, column_name, tablename):
    cell_values = get_column_values(context, tablename, column_name)
    expect(any([value in cell.split(',') if ',' in cell else value == cell for cell in cell_values])).to_be(False)
    
@then('I should see "{value}" in the "{tablename}" results')
def step_impl(context, value, tablename):
    tablename = tablename.lower().replace(' ', '_') + '_results'
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, tablename),
            value
        )
    )
    expect(found).to_be(True)
    
@then('I should not see "{status}" in the "{tablename}" results')
def step_impl(context, status, tablename):
    tablename = tablename.lower().replace(' ', '_') + '_results'
    element = context.driver.find_element_by_id(tablename)
    error_msg = "I should not see '%s' in '%s'" % (status, element.text)
    ensure(status in element.text, False, error_msg)


@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'), message)
    )
    expect(found).to_be(True)


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    if text_string == "Today's date":
        text_string = date.today().isoformat()
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id), text_string)
    )
    expect(found).to_be(True)


@then('I should not see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = context.driver.find_element_by_id(element_id)
    error_msg = "I should not see '%s' in '%s'" % (text_string, element.text)
    ensure(text_string in element.text, False, error_msg)


@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = context.driver.find_element_by_id(element_id)
    expect(element.get_attribute('value')).to_be(u'')

##################################################################
# These two function simulate copy and paste
##################################################################


@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    logging.info('Clipboard contains: %s', context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)
