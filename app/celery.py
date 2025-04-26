import os
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'natwest.settings')
app = Celery('natwest')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks() 

app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'
