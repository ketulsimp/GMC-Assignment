from celery import Celery
from dotenv import load_dotenv
import os 


load_dotenv()

app = Celery(
        'app',
        broker=os.environ['REDIS_BROKER_URL'],
        backend=os.environ['REDIS_BACKEND_URL'],
        accept_content=['pickle','json'],
        task_serializer='pickle',
        result_serializer='pickle',
    )



app.conf.task_default_queue = "product_queue"
app.conf.task_default_routing_key = "product_queue"


