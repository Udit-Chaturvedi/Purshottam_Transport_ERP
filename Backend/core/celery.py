import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

app = Celery('purshottam_erp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
