from __future__ import absolute_import
from django.conf import settings
from django_google_adwords.models import Account, Alert
from celery.app import shared_task
from celery.canvas import chain


@shared_task(queue=settings.GOOGLEADWORDS_HOUSEKEEPING_CELERY_QUEUE)
def sync_all():
    for account in Account.objects.considered_active():
        account.sync(sync_account=True, sync_campaign=True, sync_adgroup=True, sync_ad=True)


@shared_task(queue=settings.GOOGLEADWORDS_HOUSEKEEPING_CELERY_QUEUE)
def sync_chain():
    tasks = []
    if settings.GOOGLEADWORDS_SYNC_ACCOUNT:
        tasks.append(sync_accounts.si())
    if settings.GOOGLEADWORDS_SYNC_CAMPAIGN:
        tasks.append(sync_campaigns.si())
    if settings.GOOGLEADWORDS_SYNC_ADGROUP:
        tasks.append(sync_adgroups.si())
    if settings.GOOGLEADWORDS_SYNC_AD:
        tasks.append(sync_ads.si())

    chain(*tasks).apply_async()


@shared_task(queue=settings.GOOGLEADWORDS_HOUSEKEEPING_CELERY_QUEUE)
def sync_accounts():
    for account in Account.objects.considered_active():
        account.sync(sync_account=True, sync_campaign=False, sync_adgroup=False, sync_ad=False)


@shared_task(queue=settings.GOOGLEADWORDS_HOUSEKEEPING_CELERY_QUEUE)
def sync_campaigns():
    for account in Account.objects.considered_active():
        account.sync(sync_account=False, sync_campaign=True, sync_adgroup=False, sync_ad=False)


@shared_task(queue=settings.GOOGLEADWORDS_HOUSEKEEPING_CELERY_QUEUE)
def sync_adgroups():
    for account in Account.objects.considered_active():
        account.sync(sync_account=False, sync_campaign=False, sync_adgroup=True, sync_ad=False)


@shared_task(queue=settings.GOOGLEADWORDS_HOUSEKEEPING_CELERY_QUEUE)
def sync_ads():
    for account in Account.objects.considered_active():
        account.sync(sync_account=False, sync_campaign=False, sync_adgroup=False, sync_ad=True)
