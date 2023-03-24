# NYU DevOps Project - Orders Service

[![Build Status](https://github.com/CSCI-GA-2820-SP23-003/orders/actions/workflows/tdd.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP23-003/orders/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP23-003/orders/branch/add-badges/graph/badge.svg?token=0I49NMTBPC)](https://codecov.io/gh/CSCI-GA-2820-SP23-003/orders)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

Orders Service - Represents the orders placed by Customers at an eCommerce Website

## Overview

This project contains the code for Orders Service. The service consists of Orders Resource and OrderItem Resource (subordinate). The `/service` folder contains the `models.py` file for Order and OrderItem models and a `routes.py` file for the service. The `/tests` folder contains the test cases for testing the model and the service separately.

## Running the service locally

To run the Orders service on a local machine, first clone the repository and then run the following commands:

1. `cd orders`
2. `code .`
3. Reopen the folder in Dev Container
4. Run `flask run` command on the terminal
5. The service is available at localhost: `http://localhost:8000`

To run the all the test cases locally, please run the command `nosetests`. The test cases have `97%` code coverage currently.

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for business models
└── test_routes.py  - test suite for service routes
```

## Order Service APIs

### Index

GET `/`

Success Response : `200 OK`

```
{
  "name": "Order REST API Service",
  "paths": "http://localhost:8000/orders",
  "version": "1.0"
}
```

### Order Operations

| Description     | Endpoint
| --------------- | -------------------------------
| Create an Order | POST `/orders` 
| Read/Get an Order by ID   | GET `/orders/<order_id>`
| Update an existing Order | PUT `/orders/<order_id>`
| Delete an Order | DELETE `/orders/<order_id>`
| List Orders     | GET `/orders`

### Order Item Operations

| Description     | Endpoint
| --------------- | -------------------------------
| Create an Order Item | POST `/orders/<order_id>/items`
| Read/Get an Order Item | GET `/orders/<order_id>/items/<item_id>`
| Update an Order Item | PUT `/orders/<order_id>/items/<item_id>`  
| Delete an Order Item | DELETE `/orders/<order_id>/items/<item_id>`
| List Items of an Order    | GET `/orders/<order_id>/items`  

## Order Service APIs - Usage

### Create an Order

Endpoint : `/orders`

Method : `POST`

Content-Type: `application/json`

Authentication required : `None`

The items can also be created with this API by sending an array of items in the JSON request.

Example:

Request Body (JSON)
```
{
  "customer_id": 6,
  "items": []
}
```

Success Response : `201 CREATED`
```
{
  "created_on": "2023-03-07",
  "customer_id": 6,
  "id": 1,
  "items": [],
  "status": "CONFIRMED",
  "updated_on": "2023-03-07"
}
```

### Read/Get an Order

Endpoint : `/orders/<order_id>`

Method : `GET`

Authentication required : `None`

Example:

`GET /orders/1`

Success Response : `200 OK`
```
{
  "created_on": "2023-03-07",
  "customer_id": 6,
  "id": 1,
  "items": [],
  "status": "CONFIRMED",
  "updated_on": "2023-03-07"
}
```

Failure Response : `404 NOT FOUND`
```
{
  "error": "Not Found",
  "message": "404 Not Found: Order with id '1' was not found.",
  "status": 404
}
```

### Update an Order

Endpoint : `/orders/<order_id>`

Method : `PUT`

Content-Type: `application/json`

Authentication required : `None`

This API will only update order attributes, and will not update any of the order items.

Example:

Request Body (JSON)
```
{
    "customer_id": 4,
    "status": "DELIVERED"
}
```

Success Response : `200 OK`
```
{
  "created_on": "2023-03-07",
  "customer_id": 4,
  "id": 1,
  "items": [],
  "status": "DELIVERED",
  "updated_on": "2023-03-07"
}
```

Failure Response : `404 NOT FOUND`
```
{
  "error": "Not Found",
  "message": "404 Not Found: Order with id '1' was not found.",
  "status": 404
}
```

### Delete an Order

Endpoint : `/orders/<order_id>`

Method : `DELETE`

Authentication required : `None`

This API will delete an order and all of its items.

Example:

`DELETE /orders/1`

Success Response : `204 NO CONTENT`

### List All Orders

Endpoint : `/orders`

Method : `GET`

Authentication required : `None`

Example:

`GET /orders`

Success Response : `200 OK`
```
[
  {
    "created_on": "2023-03-06",
    "customer_id": 6,
    "id": 1,
    "items": [],
    "status": "CONFIRMED",
    "updated_on": "2023-03-06"
  }
]
```

### Create an Order Item

Endpoint : `/orders/<order_id>/items`

Method : `POST`

Content-Type: `application/json`

Authentication required : `None`

Example:

Request Body (JSON)
```
{
  "product_id": 65,
  "price": 20,
  "quantity": 2
}
```

Success Response : `201 CREATED`
```
{
  "created_on": "2023-03-07",
  "id": 1,
  "order_id": 1,
  "price": 20.0,
  "product_id": 65,
  "quantity": 2,
  "updated_on": "2023-03-07"
}
```

Failure Response (When invalid Order ID is provided in the URL) : `404 NOT FOUND`
```
{
  "error": "Not Found",
  "message": "404 Not Found: Order with id '1' was not found.",
  "status": 404
}
```

### Read/Get an Order Item

Endpoint : `/orders/<order_id>/items/<item_id>`

Method : `GET`

Authentication required : `None`

Example:

`GET /orders/1/items/1`

Success Response : `200 OK`
```
{
  "created_on": "2023-03-07",
  "id": 1,
  "order_id": 1,
  "price": 20.0,
  "product_id": 65,
  "quantity": 2,
  "updated_on": "2023-03-07"
}
```

Failure Response : `404 NOT FOUND`
```
{
  "error": "Not Found",
  "message": "404 Not Found: Order with id '1' was not found.",
  "status": 404
}
```

```
{
  "error": "Not Found",
  "message": "404 Not Found: Item with id '1' was not found.",
  "status": 404
}
```

### Update an Order Item

Endpoint : `/orders/<order_id>/items/<item_id>`

Method : `PUT`

Content-Type: `application/json`

Authentication required : `None`

Example:

Request Body (JSON)
```
{
  "product_id": 3,
  "price": 89,
  "quantity": 1
}
```

Success Response : `200 OK`
```
{
  "created_on": "2023-03-06",
  "id": 1,
  "order_id": 1,
  "price": 89.0,
  "product_id": 3,
  "quantity": 1,
  "updated_on": "2023-03-07"
}
```

Failure Response : `404 NOT FOUND`
```
{
  "error": "Not Found",
  "message": "404 Not Found: Order with id '1' was not found.",
  "status": 404
}
```

```
{
  "error": "Not Found",
  "message": "404 Not Found: Item with id '1' was not found.",
  "status": 404
}
```

### Delete an Order Item

Endpoint : `/orders/<order_id>/items/<item_id>`

Method : `DELETE`

Authentication required : `None`

Example:

`DELETE /orders/1/items/1`

Success Response : `204 NO CONTENT`

Failure Response : `404 NOT FOUND`
```
{
  "error": "Not Found",
  "message": "404 Not Found: Order with id '1' was not found.",
  "status": 404
}
```

### List All Items of an Order

Endpoint : `/orders/<order_id>/items`

Method : `GET`

Authentication required : `None`

Example:

`GET /orders/1/items`

Example:

Success Response : `200 OK`

```
[
  {
    "created_on": "2023-03-06",
    "id": 1,
    "order_id": 1,
    "price": 89.0,
    "product_id": 3,
    "quantity": 1,
    "updated_on": "2023-03-07"
  }
]
```

Failure Response : `404 NOT FOUND`
```
{
  "error": "Not Found",
  "message": "404 Not Found: Order with id '1' was not found.",
  "status": 404
}
```


## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
