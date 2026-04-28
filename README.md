<!-- Folder Structure

SIMPROSYSAPI_TASK/
│
├── myenv/
│
├── task2/
│   │
│   ├── celery_service/
│   │   ├── config/
│   │   │   └── settings.py
│   │   ├── models/
│   │   │   └── db_model.py
│   │   ├── celery_tasks.py
│   │   └── requirements.txt
│   │
│   ├── fastapi_service/
│   │   ├── config/
│   │   │   └── settings.py
│   │   ├── models/
│   │   │   └── db_model.pys
│   │   ├── routes/
│   │   │   └── router.py
│   │   ├── schemas/
│   │   ├── main.py
│   │   └── requirements.txt
├── .env
├── notification.log
├── .gitignore
├── dump.rdb
├── notification.log
└── README.md

Create virtual environment
python3 -m venv <name>
Activate virtual env
source <name>/bin/activate


Run the following commands for installing requirements for fastapi_service
cd task2
cd fastapi_service
pip install -r requirements.txt OR pip3 install -r requirements.txt

Run the following commands for installing requirements for celery_service
cd task2
cd celery_service
pip install -r requirements.txt OR pip3 install -r requirements.txt


In Terminal-1 (fastapi_service)
From root directory(task2) run the command given below:
E.g (myenv) ashish@Ashishs-Mac-mini task2 % uvicorn fastapi_service.main:app --reload
Command: uvicorn fastapi_service.main:app --reload

In Terminal-2 (redis_server)
Run redis server
E.g (myenv) ashish@Ashishs-Mac-mini simprosysAPI_task % redis-server
Command: redis-server

In Terminal-3 (celery_service)
From root directory(task2) run the command given below:
E.g (myenv) ashish@Ashishs-Mac-mini task2 % celery -A celery_service.celery_tasks.celery worker --loglevel=info 
Command: celery -A celery_service.celery_tasks.celery worker --loglevel=info 


API Endpoints
/products/batch
Note: The format for input should be like following (list of product-dictionaries)
[
  {
    "product_id": 1,
    "product_name": "Mechanical Gaming Keyboard",
    "description": "RGB backlit mechanical keyboard with blue switches and anti-ghosting technology.",
    "price": "59.99",
    "category": "Electronics",
    "sku": "ELEC-MGK-045",
    "images": [
      "https://example.com"
    ]
  },
  {
    "product_id": 2,
    "product_name": "Noise Cancelling Headphones",
    "description": "Over-ear Bluetooth headphones with active noise cancellation and 40-hour battery life.",
    "price": "129.50",
    "category": "Electronics",
    "sku": "ELEC-NCH-088",
    "images": [
      "https://example.com"
    ]
  }
]

CURL - URL : curl -X 'POST' \
  'http://localhost:8000/products/batch' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "product_id": 1,
    "product_name": "Mechanical Gaming Keyboard",
    "description": "RGB backlit mechanical keyboard with blue switches and anti-ghosting technology.",
    "price": "59.99",
    "category": "Electronics",
    "sku": "ELEC-MGK-045",
    "images": [
      "https://example.com"
    ]
  },
  {
    "product_id": 2,
    "product_name": "Noise Cancelling Headphones",
    "description": "Over-ear Bluetooth headphones with active noise cancellation and 40-hour battery life.",
    "price": "129.50",
    "category": "Electronics",
    "sku": "ELEC-NCH-088",
    "images": [
      "https://example.com"
    ]
  },
  {
    "product_id": 3,
    "product_name": "Ultra-Wide 4K Monitor",
    "description": "32-inch curved 4K monitor with HDR support and ultra-thin bezels for immersive viewing.",
    "price": "349.00",
    "category": "Electronics",
    "sku": "ELEC-UWM-102",
    "images": [
      "https://example.com"
    ]
  }
]
'
Input: [
  {
    "product_id": 1,
    "product_name": "Mechanical Gaming Keyboard",
    "description": "RGB backlit mechanical keyboard with blue switches and anti-ghosting technology.",
    "price": "59.99",
    "category": "Electronics",
    "sku": "ELEC-MGK-045",
    "images": [
      "https://example.com"
    ]
  },
  {
    "product_id": 2,
    "product_name": "Noise Cancelling Headphones",
    "description": "Over-ear Bluetooth headphones with active noise cancellation and 40-hour battery life.",
    "price": "129.50",
    "category": "Electronics",
    "sku": "ELEC-NCH-088",
    "images": [
      "https://example.com"
    ]
  },
  {
    "product_id": 3,
    "product_name": "Ultra-Wide 4K Monitor",
    "description": "32-inch curved 4K monitor with HDR support and ultra-thin bezels for immersive viewing.",
    "price": "349.00",
    "category": "Electronics",
    "sku": "ELEC-UWM-102",
    "images": [
      "https://example.com"
    ]
  }
]
Output: {
  "task_id": "7e1a34ee-7f87-4141-b8ff-2978d364444f",
  "accepted_count": 3,
  "failed_count": 0,
  "errors": {}
}



/products/batch/{task_id}
Input: task_id (7e1a34ee-7f87-4141-b8ff-2978d364444f)
Output: {
  "task_id": "7e1a34ee-7f87-4141-b8ff-2978d364444f",
  "state": "SUCCESS",
  "meta": {
    "Total": 3,
    "Success": 3,
    "Failed": 0,
    "Errors": []
  }
}
CURL-URL: curl -X 'GET' \
  'http://localhost:8000/products/batch/7e1a34ee-7f87-4141-b8ff-2978d364444f' \
  -H 'accept: application/json'



/products
Input: None
Output: List of products
CURL-URL: curl -X 'GET' \
  'http://localhost:8000/products' \
  -H 'accept: application/json'



/products/{product_id}
Input: product_id (1)
Output: Details of that product
    {
        "product_id": 1,
        "product_name": "Mechanical Gaming Keyboard",
        "description": "RGB backlit mechanical keyboard with blue switches and anti-ghosting technology.",
        "price": "59.99",
        "category": "Electronics",
        "sku": "ELEC-MGK-045",
        "images": [
            "https://example.com/"
        ]
    }
CURL-URL: curl -X 'GET' \
  'http://localhost:8000/products/1' \
  -H 'accept: application/json' -->

# Folder Structure

```
SIMPROSYSAPI_TASK/
│
├── myenv/
│
├── task2/
│   │
│   ├── celery_service/
│   │   ├── config/
│   │   │   └── settings.py
│   │   ├── models/
│   │   │   └── db_model.py
│   │   ├── celery_tasks.py
│   │   └── requirements.txt
│   │
│   ├── fastapi_service/
│   │   ├── config/
│   │   │   └── settings.py
│   │   ├── models/
│   │   │   └── db_model.py
│   │   ├── routes/
│   │   │   └── router.py
│   │   ├── schemas/
│   │   ├── main.py
│   │   └── requirements.txt
│
├── .env
├── notification.log
├── .gitignore
├── dump.rdb
├── notification.log
└── README.md
```



# Create Virtual Environment

### Mac / Linux

```bash
python3 -m venv <name>
source <name>/bin/activate
```

### Windows (Command Prompt)

```cmd
python -m venv <name>
<name>\Scripts\activate
```

---

# Install Requirements

## For fastapi_service

```bash
cd task2
cd fastapi_service
pip install -r requirements.txt
# OR
pip3 install -r requirements.txt
```

## For celery_service

```bash
cd task2
cd celery_service
pip install -r requirements.txt
# OR
pip3 install -r requirements.txt
```



# Run Services

## Terminal-1 (fastapi_service)

From root directory (`task2`):

```bash
uvicorn fastapi_service.main:app --reload
```

Example:

```bash
(myenv) ashish@Ashishs-Mac-mini task2 % uvicorn fastapi_service.main:app --reload
```



## Terminal-2 (redis_server)

```bash
redis-server
```

Example:

```bash
(myenv) ashish@Ashishs-Mac-mini simprosysAPI_task % redis-server
```


## Terminal-3 (celery_service)

From root directory (`task2`):

```bash
celery -A celery_service.celery_tasks.celery worker --loglevel=info
```

Example:

```bash
(myenv) ashish@Ashishs-Mac-mini task2 % celery -A celery_service.celery_tasks.celery worker --loglevel=info
```



# API Endpoints

## `/products/batch`

### Input

(List of product dictionaries)

```json
[
  {
    "product_id": 1,
    "product_name": "Mechanical Gaming Keyboard",
    "description": "RGB backlit mechanical keyboard with blue switches and anti-ghosting technology.",
    "price": "59.99",
    "category": "Electronics",
    "sku": "ELEC-MGK-045",
    "images": [
      "https://example.com"
    ]
  },
  {
    "product_id": 2,
    "product_name": "Noise Cancelling Headphones",
    "description": "Over-ear Bluetooth headphones with active noise cancellation and 40-hour battery life.",
    "price": "129.50",
    "category": "Electronics",
    "sku": "ELEC-NCH-088",
    "images": [
      "https://example.com"
    ]
  },
  {
    "product_id": 3,
    "product_name": "Ultra-Wide 4K Monitor",
    "description": "32-inch curved 4K monitor with HDR support and ultra-thin bezels for immersive viewing.",
    "price": "349.00",
    "category": "Electronics",
    "sku": "ELEC-UWM-102",
    "images": [
      "https://example.com"
    ]
  }
]
```

---

### CURL

```bash
curl -X 'POST' \
'http://localhost:8000/products/batch' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d '[
  {
    "product_id": 1,
    "product_name": "Mechanical Gaming Keyboard",
    "description": "RGB backlit mechanical keyboard with blue switches and anti-ghosting technology.",
    "price": "59.99",
    "category": "Electronics",
    "sku": "ELEC-MGK-045",
    "images": [
      "https://example.com"
    ]
  },
  {
    "product_id": 2,
    "product_name": "Noise Cancelling Headphones",
    "description": "Over-ear Bluetooth headphones with active noise cancellation and 40-hour battery life.",
    "price": "129.50",
    "category": "Electronics",
    "sku": "ELEC-NCH-088",
    "images": [
      "https://example.com"
    ]
  },
  {
    "product_id": 3,
    "product_name": "Ultra-Wide 4K Monitor",
    "description": "32-inch curved 4K monitor with HDR support and ultra-thin bezels for immersive viewing.",
    "price": "349.00",
    "category": "Electronics",
    "sku": "ELEC-UWM-102",
    "images": [
      "https://example.com"
    ]
  }
]'
```

---

### Output

```json
{
  "task_id": "7e1a34ee-7f87-4141-b8ff-2978d364444f",
  "accepted_count": 3,
  "failed_count": 0,
  "errors": {}
}
```



## `/products/batch/{task_id}`

### Input

```
task_id = 7e1a34ee-7f87-4141-b8ff-2978d364444f
```

### Output

```json
{
  "task_id": "7e1a34ee-7f87-4141-b8ff-2978d364444f",
  "state": "SUCCESS",
  "meta": {
    "Total": 3,
    "Success": 3,
    "Failed": 0,
    "Errors": []
  }
}
```


### CURL

```bash
curl -X 'GET' \
'http://localhost:8000/products/batch/7e1a34ee-7f87-4141-b8ff-2978d364444f' \
-H 'accept: application/json'
```



## `/products`

### Input

```
None
```

### Output

List of products

---

### CURL

```bash
curl -X 'GET' \
'http://localhost:8000/products' \
-H 'accept: application/json'
```



## `/products/{product_id}`

### Input

```
product_id = 1
```

### Output

```json
{
  "product_id": 1,
  "product_name": "Mechanical Gaming Keyboard",
  "description": "RGB backlit mechanical keyboard with blue switches and anti-ghosting technology.",
  "price": "59.99",
  "category": "Electronics",
  "sku": "ELEC-MGK-045",
  "images": [
    "https://example.com/"
  ]
}
```

---

### CURL

```bash
curl -X 'GET' \
'http://localhost:8000/products/1' \
-H 'accept: application/json'
```
