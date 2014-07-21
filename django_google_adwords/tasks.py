from __future__ import absolute_import
from django.conf import settings
from django_google_adwords.models import Account, Alert
from celery.app import shared_task

@shared_task(queue=settings.GOOGLEADWORDS_CELERY_QUEUE)
def sync_accounts():
    for account in Account.objects.active():
        account.sync()
        
@shared_task(queue=settings.GOOGLEADWORDS_CELERY_QUEUE)
def sync_alerts():
    Alert.sync_alerts.apply_async()