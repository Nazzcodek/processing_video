from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'processing_video.settings')

app = Celery('processing_video')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
