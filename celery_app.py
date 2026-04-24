from celery import Celery

app = Celery(
        'app',
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/1',
        include=['tasks.product_tasks'],
        task_serializer='pickle',
        result_serializer='pickle',
        accept_content=['pickle','json']
    )

