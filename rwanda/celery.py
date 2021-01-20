from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
# set the default Django settings module for the 'celery' program.
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rwanda.settings')

app = Celery('rwanda')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(hour=8, minute=30),
                             service_purchases_deadline_reminder_task.s())


@app.task
def service_purchases_deadline_reminder_task():
    from rwanda.purchase.models import ServicePurchase
    from django.utils import timezone
    from datetime import timedelta
    from rwanda.account.mails import send_service_purchase_deadline_reminder
    from rwanda.administration.utils import param_reminder_service_purchase_deadline_lte

    days = param_reminder_service_purchase_deadline_lte()
    for purchase in ServicePurchase.objects.filter(status=ServicePurchase.STATUS_ACCEPTED,
                                                   deadline_at__lte=timezone.now() + timedelta(days)):
        send_service_purchase_deadline_reminder(purchase)
    return True


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
