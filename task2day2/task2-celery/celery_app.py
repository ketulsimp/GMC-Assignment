from celery import Celery
import os

# backend = os.getenv('BACKEND')
# broker = os.getenv('BROKER')
c_task = Celery('c_task',
                broker='redis://localhost:6379/0',
                backend='redis://localhost:6379/0'
                )
# c_task = Celery('c_task',
#                 broker=str(backend),
#                 backend=str(broker)
#                 )

import celery_task