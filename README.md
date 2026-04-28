## Project Title

# Batch Product Insertion.

## Description

microservices for the fastapi , celery and logging module

## Prerequisites

Make sure the following are installed and running:

- Python 3.9+
- MongoDB
- Redis

## Getting Started



# 1. celery

### Installing

* redirect your terminal to task2day2/task2-celery

    ### run - cd task2day2/task2-celery

* install required library 

    ### run - pip install -r requirements.txt

* set up .env file 

    create .env file with below example value

        MONGO_URL=mongodb://localhost:27017/
        BACKEND=redis://localhost:6379/0
        BROKER=redis://localhost:6379/0

### Executing program

* How to run the program
* make sure that you are in task2-celery directory
    
    ### run - celery -A celery_app worker --loglevel=info



# 2. Fastapi

### Installing

* make sure that celery task is runnig

* redirect your terminal to task2day2/task2-fastapi

    ### run - cd task2day2/task2-fastapi

* install required library 

    ### run - pip install -r requirements.txt

* set up .env file 

    create .env file with below example value

        MONGO_URL=mongodb://localhost:27017/
        BACKEND=redis://localhost:6379/0
        BROKER=redis://localhost:6379/0

### Executing program

* How to run the program
* make sure that you are in task2-fastapi directory

    ### run - uvicorn main:app --reload

* after performing above cammand visit 

    http://127.0.0.1:8000/docs


# folder structure

    DAY2TASKFINAL/
    │
    ├── task2day2/
    │   │
    │   ├── task2-celery/
    │   │   ├── .env
    │   │   ├── app.log
    │   │   ├── celery_app.py
    │   │   ├── celery_task.py
    │   │   ├── db.py
    │   │   └── requirements.txt
    │   │
    │   ├── task2-fastapi/
    │   │   ├── app/
    │   │   │   └── routes.py
    |   |   |   └── schema.py
    │   │   ├── .env
    │   │   ├── app.log
    │   │   ├── db.py
    │   │   ├── main.py
    │   │   └── requirements.txt
    │
    ├── .gitignore
    └── README.md


# Endpoints

## 1. POST /products/batch

to store the batch products 

### curl - 
    curl -X 'POST' \
    'http://127.0.0.1:8000/products/batch' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '[
    {
        "product_id": 2,
        "name": "pant",
        "sku": "CL-SAN-LT-8-BLU",
        "photo": [
        "https.exaple.con"
        ],
        "description": "this is the product of ...",
        "gtin": 4012345123456,
        "price": 2000,
        "product_type": "electronics"
    }
    ]'

### output
    {"task_id": "780e8a5f-7021-4760-876a-e067d7b5076c"}

## 2. GET /products/batch/{task_id} 

to check the process of the batch request

### curl -
    curl -X 'GET' \
    'http://127.0.0.1:8000/products/batch/780e8a5f-7021-4760-876a-e067d7b5076c'  \
    -H 'accept: application/json'

### output 
    {
        "task_id": "8652f6bd-998c-4875-9daa-a32e5254e050",
        "status": "SUCCESS",
        "result": {
            "status": "completed",
            "total": 1,
            "inserted_data": 1,
            "not_inserted_data": 0,
            "results": []
        }
    }


## 3. GET /products

to get all products details

### curl -
    curl -X 'GET' \
    'http://127.0.0.1:8000/products' \
    -H 'accept: application/json'

### output
    [
        {
            "_id": "69ef2d38d3866fa292439c72",
            "product_id": 2,
            "name": "pant",
            "sku": "CL-SAN-LT-8-BLU",
            "photo": [
            "https.exaple.con"
            ],
            "description": "this is the product of ...",
            "gtin": 4012345123456,
            "price": 2000,
            "product_type": "electronics"
        },
        {
            "_id": "69ef2d38d3866fa292439c73",
            "product_id": 92,
            "name": "pant",
            "sku": "CL-SAN-LT--BLU",
            "photo": [
            "https.exaple.con"
            ],
            "description": "this is the product of ...",
            "gtin": 401234553456,
            "price": 2000,
            "product_type": "electronics"
        },
        {
            "_id": "69ef2d38d3866fa292439c75",
            "product_id": 82,
            "name": "pant",
            "sku": "CL-SAN-L8-BLU",
            "photo": [
            "https.exaple.con"
            ],
            "description": "this is the product of ...",
            "gtin": 4012340023456,
            "price": 2000,
            "product_type": "electronics"
        }
    ]

## 4. GET /products/{id} 

to get specific product detail

### curl -
    curl -X 'GET' \
    'http://127.0.0.1:8000/products/2' \
    -H 'accept: application/json'

### output
    {
        "product_id": 2,
        "name": "pant",
        "sku": "CL-SAN-LT-8-BLU",
        "photo": [
            "https.exaple.con"
        ],
        "description": "this is the product of ...",
        "gtin": 4012345123456,
        "price": 2000,
        "product_type": "electronics"
    }
