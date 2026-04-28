from celery import Celery
from kombu import Queue
import os
from dotenv import load_dotenv

load_dotenv()

app = Celery(
        'app',
        broker=os.environ['REDIS_BROKER_URL'],
        backend=os.environ['REDIS_BACKEND_URL'],
        include=['tasks.product_tasks'],
        task_serializer='pickle',
        result_serializer='pickle',
        accept_content=['pickle','json']
    )

app.conf.task_default_exchange = 'tasks'
app.conf.task_default_routing_key = "product_queue"



app.conf.task_queues = (
    Queue('product_queue',routing_key='tasks.product_tasks'),
)
