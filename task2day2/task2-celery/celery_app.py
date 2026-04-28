from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

c_task = Celery('c_task',
               broker=os.getenv("BROKER"),
               backend=os.getenv("BACKEND")
                )

import celery_task