# SimprosysAPI Task

## Architecture Overview

The project contains two folders:

- Batch_Worker_Service: contains the files of celery worker processing
- WebAPI_services: contains the files of FastAPI



## Setup Guide

### Prerequisites

- Python 3.12 version is installed
- MongoDB server running on `localhost:27017`
- Redis server running on `localhost:6379`

# Steps to start the app


git init

Clone the repo, then create two terminals and run the following:

**Terminal 1:**
```
cd Batch_Worker_Service
pip install -r requirements.txt
celery -A celery_app worker --loglevel=info
```
**Terminal 2:**
```
cd WebAPI_services
pip install -r requirements.txt
uvicorn main:app --reload
```

## Environment Variables

Both folders use a `.env` file to get the environment variables.

**Batch_Worker_Service/.env`:**
```
REDIS_URL=redis://localhost:6379/0
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=product_task_2_f-1
```
**WebAPI_services/.env:**
```
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=product_task_2_f-1
```


### Where the Service Starts

- FastAPI: http://127.0.0.1:8000/docs


# Project / API Guide

## POST `/products/batch`

Give batch of products to the Celery broker to create a task to insert the products in the database.

**Request Body:**
```json
[
  {
    "product_id": 1,
    "product_name": "Wireless Mouse",
    "sku": "WM-001",
    "product_image": "https://example.com/mouse",
    "price": 799,
    "description": "Ergonomic wireless mouse"
  }
]
```
**Sample cURL:**
```json
curl -X 'POST' \
  'http://127.0.0.1:8000/products/batch' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "product_id": 1,
    "product_name": "Wireless Mouse",
    "sku": "WM-001",
    "product_image": "https://example.com/mouse",
    "price": 799,
    "description": "Ergonomic wireless mouse"
  }]'
```
**Response:**
```json

{
  "task_id": "4f7d72e0-11ea-412a-9dba-afbf58e3ffc4"
}
```


## GET `/products/batch/{task_id}`

This API is used to get the status of the Celery task whether the task is completed or not completed.

**Request:** Give the task id returned by the POST API.

**Sample cURL:**
```json
curl -X 'GET' \
  'http://127.0.0.1:8000/products/batch/4f7d72e0-11ea-412a-9dba-afbf58e3ffc4' \
  -H 'accept: application/json'
```

**Response:**
```json
{
  "task_id": "4f7d72e0-11ea-412a-9dba-afbf58e3ffc4",
  "state": "SUCCESS",
  "meta": {
    "total": 1,
    "success": 1,
    "failed": 0,
    "errors": []
  }
}
```

## GET `/products`

Return all the products that are in the database.
```json
**Sample cURL:**
curl -X 'GET' \
  'http://127.0.0.1:8000/products' \
  -H 'accept: application/json'
```

**Response:**
```json
[
  {
    "_id": "69f082eb48e5a0d9b23f2e4f",
    "product_id": 1,
    "product_name": "Wireless Mouse",
    "sku": "WM-001",
    "product_image": "https://example.com/mouse",
    "price": 799,
    "description": "Ergonomic wireless mouse"
  }
]
```

## GET `/products/by-product-id/{product_id}`

Return the single product details by `product_id`.
```json
**Sample cURL:**
curl -X 'GET' \
  'http://127.0.0.1:8000/products/by-product-id/1' \
  -H 'accept: application/json'
```
**Response:**
```json
{
  "_id": "69f082eb48e5a0d9b23f2e4f",
  "product_id": 1,
  "product_name": "Wireless Mouse",
  "sku": "WM-001",
  "product_image": "https://example.com/mouse",
  "price": 799,
  "description": "Ergonomic wireless mouse"
}
```



# Logger Package

To install the package:


pip install workerlogger --index-url https://gitlab.com/api/v4/projects/81705392/packages/pypi/simple

# Folder Structure

![alt text](image.png)

# Sample data for testing
```json
[
  {
    "product_id": 1,
    "product_name": "Wireless Mouse",
    "sku": "WM-001",
    "product_image": "https://example.com/mouse",
    "price": 799,
    "description": "Ergonomic wireless mouse"
  },
  {
    "product_id": 2,
    "product_name": "Mechanical Keyboard",
    "sku": "MK-002",
    "product_image": "https://example.com/keyboard",
    "price": 2499,
    "description": "RGB mechanical keyboard"
  },
  {
    "product_id": 3,
    "product_name": "Bluetooth Speaker",
    "sku": "BS-003",
    "product_image": "https://example.com/speaker",
    "price": 1599,
    "description": "Portable Bluetooth speaker"
  },
  {
    "product_id": 4,
    "product_name": "Smart Watch",
    "sku": "SW-004",
    "product_image": "https://example.com/watch",
    "price": 4999,
    "description": "Fitness tracking smartwatch"
  },
  {
    "product_id": 5,
    "product_name": "USB-C Charger",
    "sku": "UC-005",
    "product_image": "https://example.com/charger",
    "price": 999,
    "description": "Fast charging USB-C adapter"
  },
  {
    "product_id": 6,
    "product_name": "Laptop Stand",
    "sku": "LS-006",
    "product_image": "https://example.com/stand",
    "price": 1299,
    "description": "Adjustable laptop stand"
  },
  {
    "product_id": 7,
    "product_name": "Noise Cancelling Headphones",
    "sku": "NH-007",
    "product_image": "https://example.com/headphones",
    "price": 6999,
    "description": "Over-ear noise cancelling headphones"
  },
  {
    "product_id": 8,
    "product_name": "Gaming Chair",
    "sku": "GC-008",
    "product_image": "https://example.com/chair",
    "price": 10999,
    "description": "Comfortable gaming chair"
  },
  {
    "product_id": 9,
    "product_name": "External Hard Drive",
    "sku": "HD-009",
    "product_image": "https://example.com/harddrive",
    "price": 3999,
    "description": "1TB external storage"
  },
  {
    "product_id": 10,
    "product_name": "LED Monitor",
    "sku": "LM-010",
    "product_image": "https://example.com/monitor",
    "price": 8999,
    "description": "24-inch Full HD monitor"
  },
  {
    "product_id": 11,
    "product_name": "Wireless Earbuds",
    "sku": "WE-011",
    "product_image": "https://example.com/earbuds",
    "price": 1999,
    "description": "True wireless earbuds"
  },
  {
    "product_id": 12,
    "product_name": "Power Bank",
    "sku": "PB-012",
    "product_image": "https://example.com/powerbank",
    "price": 1499,
    "description": "10000mAh power bank"
  },
  {
    "product_id": 13,
    "product_name": "Webcam",
    "sku": "WC-013",
    "product_image": "https://example.com/webcam",
    "price": 1799,
    "description": "HD webcam for video calls"
  },
  {
    "product_id": 14,
    "product_name": "Smartphone Stand",
    "sku": "SS-014",
    "product_image": "https://example.com/standphone",
    "price": 499,
    "description": "Adjustable mobile stand"
  },
  {
    "product_id": 15,
    "product_name": "Gaming Mouse Pad",
    "sku": "MP-015",
    "product_image": "https://example.com/mousepad",
    "price": 699,
    "description": "Large RGB mouse pad"
  }
]
```