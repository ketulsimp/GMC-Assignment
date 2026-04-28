# Simprosys API Task

## Task Definition: 

Split the monolith into two independently runnable services: Web API (HTTP traffic) and Batch Worker (Celery). They share the same MongoDB and Redis but have no code-level dependencies on each other. The custom logger code is isolated in each service..

## Project Structure:
```
/Day-2-Task
    /FASTAPI
        /app 
            /config
                celery_client.py
                settings.py 
                db.py
            /models
                product_model.py
            /routes
                product.py 
            /services
                product_service.py
            /utilities
                product_utils.py
        __init__.py
        main.py 
        .env
        requirements.txt
    /CELERY
        /conf
            celery_client.py
            settings.py
        /tasks
            tasks.py
        .env
        requirements.txt

```

## Installation guide:

1. Open a new Terminal

2. Clone the repository \
`git clone -b raj-task-2 https://github.com/ketulsimp/GMC-Assignment.git`

3. Run the commands \
`cd Task_2/Day-2-Task/FASTAPI` 

4. Create a virtual Environment and Run the following commands
``` 
    python3 -m venv venv 
    source venv/bin/activate
    pip install -r requirements.txt
```

5. Create and Configure the .env file
```
    MONGO_URI=
    BROKER_URI=
    BACKEND_URI=
```

6. Start the fastapi server \
`uvicorn app.main:app --reload`

7. Open another terminal and navigate to the Task_2 folder

8. Run the command \
`cd Day-2-Task/CELERY/`

9. Create a virtual Environment and Run the following commands
``` 
    python3 -m venv venv 
    source venv/bin/activate
    pip install -r requirements.txt
```

10. Create and Configure the .env file
```
    MONGO_URI=
    BROKER_URI=
    BACKEND_URI=
```

11. Start the celery instance \
`celery -A tasks.tasks worker --loglevel=info -Q new-queue`
