from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
import eventlet
eventlet.monkey_patch()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reneapp.settings')
app = Celery('APP_RENE-Celery', backend='redis', broker='redis://localhost:6379')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
