from contextlib import contextmanager
from datetime import date, timedelta
from decimal import Decimal
import errno
import gzip
import logging
import os
import re
import time

from celery.canvas import group
from celery.contrib.methods import task
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.files.base import File
from django.db import models
from django.db.models import Max
from django.db.models.aggregates import Sum, Min, Avg
from django.db.models.fields import FieldDoesNotExist, DecimalField
from django.db.models.query import QuerySet as _QuerySet
from django.db.models.signals import post_delete
from django.template.defaultfilters import truncatechars
from django_cereal.pickle import DJANGO_CEREAL_PICKLE
from django_google_adwords.errors import *
from django_google_adwords.helper import adwords_service
from django_google_adwords.lock import release_googleadwords_lock
from django_toolkit.celery.decorators import ensure_self
from django_toolkit.csv.unicode import UnicodeReader
from django_toolkit.db.models import QuerySetManager
from djmoney.models.fields import MoneyField
from googleads.errors import GoogleAdsError

from .lock import acquire_googleadwords_lock
from .settings import GoogleAdwordsConf  # import AppConf settings


logger = logging.getLogger(__name__)
locking_logger = logging.getLogger('%s.locker' % __name__)

remove_non_letters = re.compile('[^a-z|0-9|_]')


def attribute_to_field_name(attribute):
    return remove_non_letters.sub(r'', attribute.lower().replace(' ', '_')).replace('__', '_')


class PopulatingGoogleAdwordsQuerySet(_QuerySet):
    IGNORE_FIELDS = ['created', 'updated']

    def populate_model_from_dict(self, model, data, ignore_fields=[]):
        update_fields = []
        currency = None

        def to_field_name(key):
            return attribute_to_field_name(key)

        def clean(value, field):
            # If the adwords api returns "--" regardless of the field we want to return None
            if value == ' --':
                return None

            # If money divide by 1,000,000 to get dollars/cents
            elif isinstance(field, MoneyField):
                if int(value) > 0:
                    return Decimal(value) / 1000000
                return Decimal(value)

            # The adwords api returns "1.87%" or "< 10%" for percentage fields we need to remove the % < > signs
            elif isinstance(field, DecimalField):
                mapping = [('%', ''), ('<', ''), ('>', ''), (',', ''), (' ', '')]
                for k, v in mapping:
                    value = value.replace(k, v)
                return value

            # The api returns data in a way we can handle
            else:
                return value

        for key, _value in data.items():
            field_name = to_field_name(key)
            if field_name in self.IGNORE_FIELDS or field_name in ignore_fields:
                continue
            if field_name == 'currency':
                currency = _value
            try:
                field = model._meta.get_field(field_name)
            except FieldDoesNotExist:
                # Skip fields that dont exist in the model
                continue

            value = clean(_value, field)
            try:
                value = field.to_python(value)
            except DjangoValidationError as e:
                raise ValidationError(field_name, e.messages)

            if value != getattr(model, field_name):
                update_fields.append(field_name)
                setattr(model, field_name, value)

        # Now set all currency fields, do this outside the loop above incase someone redefines the field order
        for field_name in update_fields:
            field = model._meta.get_field(field_name)
            if isinstance(field, MoneyField):
                if currency is None:
                    raise NoAccountCurrencyCodeError("AccountCurrencyCode must be included in %s.get_selector" % model.__class__)
                currency_field_name = '%s_currency' % field_name
                update_fields.append(currency_field_name)
                setattr(model, currency_field_name, currency)

        return update_fields

    def _populate(self, data, ignore_fields=[], **kwargs):
        """
        Low level get or create model which then populates the model with data.

        :param data: A dict of data as retrieved from the Google Adwords API.
        :param **kwargs: Keyword args that are supplied to retrieve the model instance
                         and also to generate an instance if one does not exist.
        :return: models.Model
        """
        model_cls = self.model
        try:
            model = model_cls.objects.get(**kwargs)
        except model_cls.DoesNotExist:
            model = model_cls(**kwargs)
        update_fields = self.populate_model_from_dict(model, data, ignore_fields)
        if model.pk is None:
            model.save()
        else:
            model.save(update_fields=update_fields)
        return model


class Account(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_SYNC = 'sync'
    STATUS_INACTIVE = 'inactive'
    STATUS_CHOICES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_SYNC, 'Sync'),
        (STATUS_INACTIVE, 'Inactive'),
    )
    STATUS_CONSIDERED_ACTIVE = (STATUS_ACTIVE, STATUS_SYNC,)

    account_id = models.BigIntegerField(unique=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    account = models.CharField(max_length=255, blank=True, null=True, help_text='Account descriptive name')
    currency = models.CharField(max_length=255, blank=True, null=True, help_text='Account currency code')
    account_last_synced = models.DateField(blank=True, null=True)
    campaign_last_synced = models.DateField(blank=True, null=True)
    ad_group_last_synced = models.DateField(blank=True, null=True)
    ad_last_synced = models.DateField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = QuerySetManager()

    def __unicode__(self):
        return '%s' % (self.account_id)

    class QuerySet(PopulatingGoogleAdwordsQuerySet):

        def active(self):
            return Account.objects.filter(status=Account.STATUS_ACTIVE)

        def inactive(self):
            return Account.objects.filter(status=Account.STATUS_INACTIVE)

        def considered_active(self):
            return Account.objects.filter(status__in=Account.STATUS_CONSIDERED_ACTIVE)

        def populate(self, data, account):
            """
            A locking get_or_create - note only the account_id is used in the 'get'.
            """
            # Get a lock based upon the campaign id
            while not acquire_googleadwords_lock(Account, account.account_id):
                locking_logger.debug("Waiting for acquire_googleadwords_lock: %s:%s", Account.__name__, account.account_id)
                time.sleep(settings.GOOGLEADWORDS_LOCK_WAIT)

            try:
                locking_logger.debug("Success acquire_googleadwords_lock: %s:%s", Account.__name__, account.account_id)
                return self._populate(data,
                                      ignore_fields=['status', 'account_id', 'account_last_synced'],
                                      account_id=account.account_id)

            finally:
                locking_logger.debug("Releasing acquire_googleadwords_lock: %s:%s", Account.__name__, account.account_id)
                release_googleadwords_lock(Account, account.account_id)

    @task(name='Account.sync',
          queue=settings.GOOGLEADWORDS_HOUSEKEEPING_CELERY_QUEUE)
    def sync(self, start=None, force=False, sync_account=True, sync_campaign=False, sync_adgroup=False, sync_ad=False):
        """
        Sync all data from Google Adwords API for this account.

        Retrieve and populate the following reports from the Google Adwords API.

        - Account Performance Report
        - Campaign Performance Report
        - Ad Group Performance Report
        - Ad Performance Report
        """

        self.start_sync()
        tasks = []

        """
        Account
        """
        if sync_account:
            if not force and not self.account_last_synced:
                account_start = date.today() - timedelta(days=settings.GOOGLEADWORDS_NEW_ACCOUNT_ACCOUNT_SYNC_DAYS)
            elif not force and self.account_last_synced:
                account_start = self.account_last_synced - timedelta(days=settings.GOOGLEADWORDS_EXISTING_ACCOUNT_SYNC_DAYS)
            elif force and start:
                account_start = start
            tasks.append(self.create_report_file.si(Account.get_selector(start=account_start)) | self.sync_account.s(this=self) | self.finish_account_sync.si(this=self))

        """
        Campaign
        """
        if sync_campaign:
            if not force and not self.campaign_last_synced:
                campaign_start = date.today() - timedelta(days=settings.GOOGLEADWORDS_NEW_ACCOUNT_CAMPAIGN_SYNC_DAYS)
            elif not force and self.campaign_last_synced:
                campaign_start = self.campaign_last_synced - timedelta(days=settings.GOOGLEADWORDS_EXISTING_CAMPAIGN_SYNC_DAYS)
            elif force and start:
                campaign_start = start
            tasks.append(self.create_report_file.si(Campaign.get_selector(start=campaign_start)) | self.sync_campaign.s(this=self) | self.finish_campaign_sync.si(this=self))

        """
        Ad Group
        """
        if sync_adgroup:
            if not force and not self.ad_group_last_synced:
                ad_group_start = date.today() - timedelta(days=settings.GOOGLEADWORDS_NEW_ACCOUNT_ADGROUP_SYNC_DAYS)
            elif not force and self.ad_group_last_synced:
                ad_group_start = self.ad_group_last_synced - timedelta(days=settings.GOOGLEADWORDS_EXISTING_ADGROUP_SYNC_DAYS)
            elif force and start:
                ad_group_start = start
            tasks.append(self.create_report_file.si(AdGroup.get_selector(start=ad_group_start)) | self.sync_ad_group.s(this=self) | self.finish_ad_group_sync.si(this=self))

        """
        Ad
        """
        if sync_ad:
            if not force and not self.ad_last_synced:
                ad_start = date.today() - timedelta(days=settings.GOOGLEADWORDS_NEW_ACCOUNT_AD_SYNC_DAYS)
            elif not force and self.ad_last_synced:
                ad_start = self.ad_last_synced - timedelta(days=settings.GOOGLEADWORDS_EXISTING_AD_SYNC_DAYS)
            elif force and start:
                ad_start = start
            tasks.append(self.create_report_file.si(Ad.get_selector(start=ad_start)) | self.sync_ad.s(this=self) | self.finish_ad_sync.si(this=self))

        canvas = group(*tasks) | self.finish_sync.si(this=self)
        return canvas.apply_async()

    @task(name='Account.start_sync',
          queue=settings.GOOGLEADWORDS_HOUSEKEEPING_CELERY_QUEUE,
          serializer=DJANGO_CEREAL_PICKLE)
    def start_sync(self):
        self.status = self.STATUS_SYNC
        self.save(update_fields=['status'])

    @task(name='Account.finish_sync',
          queue=settings.GOOGLEADWORDS_HOUSEKEEPING_CELERY_QUEUE,
          serializer=DJANGO_CEREAL_PICKLE)
    @ensure_self
    def finish_sync(self):
        self.status = self.STATUS_ACTIVE
        self.save(update_fields=['updated', 'status'])

    @task(name='Account.finish_account_sync',
          queue=settings.GOOGLEADWORDS_HOUSEKEEPING_CELERY_QUEUE,
          serializer=DJANGO_CEREAL_PICKLE)
    @ensure_self
    def finish_account_sync(self):
        self.account_last_synced = None
        account_last_synced = DailyAccountMetrics.objects.filter(account=self).aggregate(Max('day'))
        if 'day__max' in account_last_synced:
            self.account_last_synced = account_last_synced['day__max']
        self.save(update_fields=['updated', 'account_last_synced'])

    @task(name='Account.finish_campaign_sync',
          queue=settings.GOOGLEADWORDS_HOUSEKEEPING_CELERY_QUEUE,
          serializer=DJANGO_CEREAL_PICKLE)
    @ensure_self
    def finish_campaign_sync(self):
        self.campaign_last_synced = None
        campaign_last_synced = DailyCampaignMetrics.objects.filter(campaign__account=self).aggregate(Max('day'))
        if 'day__max' in campaign_last_synced:
            self.campaign_last_synced = campaign_last_synced['day__max']
        self.save(update_fields=['updated', 'campaign_last_synced'])

    @task(name='Account.finish_ad_group_sync',
          queue=settings.GOOGLEADWORDS_HOUSEKEEPING_CELERY_QUEUE,
          serializer=DJANGO_CEREAL_PICKLE)
    @ensure_self
    def finish_ad_group_sync(self):
        self.ad_group_last_synced = None
        ad_group_last_synced = DailyAdGroupMetrics.objects.filter(ad_group__campaign__account=self).aggregate(Max('day'))
        if 'day__max' in ad_group_last_synced:
            self.ad_group_last_synced = ad_group_last_synced['day__max']
        self.save(update_fields=['updated', 'ad_group_last_synced'])

    @task(name='Account.finish_ad_sync',
          queue=settings.GOOGLEADWORDS_HOUSEKEEPING_CELERY_QUEUE,
          serializer=DJANGO_CEREAL_PICKLE)
    @ensure_self
    def finish_ad_sync(self):
        self.ad_last_synced = None
        ad_last_synced = DailyAdMetrics.objects.filter(ad__ad_group__campaign__account=self).aggregate(Max('day'))
        if 'day__max' in ad_last_synced:
            self.ad_last_synced = ad_last_synced['day__max']
        self.save(update_fields=['updated', 'ad_last_synced'])

    @task(name='Account.create_report_file',
          queue=settings.GOOGLEADWORDS_REPORT_RETRIEVAL_CELERY_QUEUE,
          serializer=DJANGO_CEREAL_PICKLE)
    def create_report_file(self, report_definition):
        """
        Create a ReportFile that contains the Google Adwords data as specified by report_definition.
        """
        try:
            return ReportFile.objects.request(report_definition=report_definition,
                                              client_customer_id=self.account_id)
        except RateExceededError as exc:
            logger.info("Caught RateExceededError for account '%s' - retrying in '%s' seconds.", self.pk, exc.retry_after_seconds)
            raise self.get_account_data.retry(exc, countdown=exc.retry_after_seconds)
        except GoogleAdsError as exc:
            raise InterceptedGoogleAdsError(exc, account_id=self.account_id)

    @task(name='Account.sync_account',
          queue=settings.GOOGLEADWORDS_DATA_IMPORT_CELERY_QUEUE,
          time_limit=settings.GOOGLEADWORDS_CELERY_TIMELIMIT,
          soft_time_limit=settings.GOOGLEADWORDS_CELERY_SOFTTIMELIMIT,
          serializer=DJANGO_CEREAL_PICKLE)
    @ensure_self
    def sync_account(self, report_file):
        """
        Sync the account data report.

        :param report_file: ReportFile
        """
        try:
            for row in report_file.dehydrate():
                account = Account.objects.populate(row, self)
                DailyAccountMetrics.objects.populate(row, account=account)

        except KeyError:
            logger.info("Caught KeyError syncing account '%s', report_file '%s' - Report doesn't have expected rows", self.pk, report_file.pk)
            raise

    @task(name='Account.sync_campaign',
          queue=settings.GOOGLEADWORDS_DATA_IMPORT_CELERY_QUEUE,
          time_limit=settings.GOOGLEADWORDS_CELERY_TIMELIMIT,
          soft_time_limit=settings.GOOGLEADWORDS_CELERY_SOFTTIMELIMIT,
          serializer=DJANGO_CEREAL_PICKLE)
    @ensure_self
    def sync_campaign(self, report_file):
        """
        Sync the campaign data report.

        :param report_file: ReportFile
        """
        try:
            for row in report_file.dehydrate():
                account = Account.objects.populate(row, self)
                campaign = Campaign.objects.populate(row, account=account)
                DailyCampaignMetrics.objects.populate(row, campaign=campaign)

        except KeyError:
            logger.info("Caught KeyError syncing campaign for account '%s', report_file '%s' - Report doesn't have expected rows", self.pk, report_file.pk)
            raise

    @task(name='Account.sync_ad_group',
          queue=settings.GOOGLEADWORDS_DATA_IMPORT_CELERY_QUEUE,
          time_limit=settings.GOOGLEADWORDS_CELERY_TIMELIMIT,
          soft_time_limit=settings.GOOGLEADWORDS_CELERY_SOFTTIMELIMIT,
          serializer=DJANGO_CEREAL_PICKLE)
    @ensure_self
    def sync_ad_group(self, report_file):
        """
        Sync the ad group data report.

        :param report_file: ReportFile
        """
        try:
            for row in report_file.dehydrate():
                account = Account.objects.populate(row, self)
                campaign = Campaign.objects.populate(row, account=account)
                ad_group = AdGroup.objects.populate(row, campaign=campaign)
                DailyAdGroupMetrics.objects.populate(row, ad_group=ad_group)

        except KeyError:
            logger.info("Caught KeyError syncing ad group for account '%s', report_file '%s' - Report doesn't have expected rows", self.pk, report_file.pk)
            raise

    @task(name='Account.sync_ad', queue=settings.GOOGLEADWORDS_DATA_IMPORT_CELERY_QUEUE, time_limit=settings.GOOGLEADWORDS_CELERY_TIMELIMIT, soft_time_limit=settings.GOOGLEADWORDS_CELERY_SOFTTIMELIMIT, serializer=DJANGO_CEREAL_PICKLE)
    @ensure_self
    def sync_ad(self, report_file):
        """
        Sync the ad data report.

        :param report_file: ReportFile
        """
        try:
            for row in report_file.dehydrate():
                account = Account.objects.populate(row, self)
                campaign = Campaign.objects.populate(row, account=account)
                ad_group = AdGroup.objects.populate(row, campaign=campaign)
                ad = Ad.objects.populate(row, ad_group=ad_group)
                DailyAdMetrics.objects.populate(row, ad=ad)

        except KeyError:
            logger.info("Caught KeyError syncing ad for account '%s', report_file '%s' - Report doesn't have expected rows", self.pk, report_file.pk)
            raise

    @staticmethod
    def get_selector(start=None, finish=None):
        """
        Returns the selector to pass to the api to get the data.
        """
        if not start:
            start = date.today() - timedelta(days=settings.GOOGLEADWORDS_EXISTING_ACCOUNT_SYNC_DAYS)
        if not finish:
            finish = date.today() - timedelta(days=1)

        report_definition = {
            'reportName': 'Account Performance Report',
            'dateRangeType': 'CUSTOM_DATE',
            'reportType': 'ACCOUNT_PERFORMANCE_REPORT',
            'downloadFormat': 'GZIPPED_CSV',
            'selector': {
                'fields': [
                    'AccountCurrencyCode',
                    'AccountDescriptiveName',
                    'AverageCpc',
                    'AverageCpm',
                    'AveragePosition',
                    'Clicks',
                    'ContentBudgetLostImpressionShare',
                    'ContentImpressionShare',
                    'ContentRankLostImpressionShare',
                    'ClickConversionRate',
                    'ConversionRateManyPerClick',
                    'ConversionValue',
                    'ConvertedClicks',
                    'ConversionsManyPerClick',
                    'Cost',
                    'CostPerConvertedClick',
                    'CostPerConversionManyPerClick',
                    'CostPerEstimatedTotalConversion',
                    'Ctr',
                    'Device',
                    'EstimatedCrossDeviceConversions',
                    'EstimatedTotalConversionRate',
                    'EstimatedTotalConversionValue',
                    'EstimatedTotalConversionValuePerClick',
                    'EstimatedTotalConversionValuePerCost',
                    'EstimatedTotalConversions',
                    'Impressions',
                    'InvalidClickRate',
                    'InvalidClicks',
                    'SearchBudgetLostImpressionShare',
                    'SearchExactMatchImpressionShare',
                    'SearchImpressionShare',
                    'SearchRankLostImpressionShare',
                    'Date',
                ],
                'dateRange': {
                    'min': start.strftime("%Y%m%d"),
                    'max': finish.strftime("%Y%m%d")
                },
            },
            'includeZeroImpressions': 'true'
        }

        return report_definition

    def spend(self, start, finish):
        """
        @param start: the start date the the data is for.
        @param finish: the finish date you want the data for.
        """
        account_first_synced = DailyAccountMetrics.objects.filter(account=self).aggregate(Min('day'))
        first_synced_date = None
        if 'day__min' in account_first_synced:
            first_synced_date = account_first_synced['day__min']

        if not self.account_last_synced or self.account_last_synced < finish or not first_synced_date or first_synced_date > start:
            raise AdwordsDataInconsistencyError('Google Adwords Account %s does not have correct amount of data to calculate the spend between "%s" and "%s"' % (
                self,
                start,
                finish,
            ))

        cost = self.metrics.filter(day__gte=start, day__lte=finish).aggregate(Sum('cost'))['cost__sum']

        if cost is None:
            return 0
        else:
            return cost

    def is_synced(self, start, finish):
        raise NotImplementedError("Account.is_synced() is not implemented.")
        pass
#         return DailyAdMetrics.objects.account(self).is_synced(start, finish) and \
#             asdf.objects.account(self).contains_data(start, finish) and \
#             asdf.objects.account(self).contains_data(start, finish)

    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    @property
    def ad_groups(self):
        """
        Helper to return associated Ad Groups.
        """
        return AdGroup.objects.filter(campaign__account=self)

    @property
    def ads(self):
        """
        Helper to return associated Ads.
        """
        return Ad.objects.filter(ad_group__campaign__account=self)


class Alert(models.Model):
    TYPE_ACCOUNT_ON_TARGET = 'ACCOUNT_ON_TARGET'
    TYPE_DECLINED_PAYMENT = 'DECLINED_PAYMENT'
    TYPE_CREDIT_CARD_EXPIRING = 'CREDIT_CARD_EXPIRING'
    TYPE_ACCOUNT_BUDGET_ENDING = 'ACCOUNT_BUDGET_ENDING'
    TYPE_CAMPAIGN_ENDING = 'CAMPAIGN_ENDING'
    TYPE_PAYMENT_NOT_ENTERED = 'PAYMENT_NOT_ENTERED'
    TYPE_MISSING_BANK_REFERENCE_NUMBER = 'MISSING_BANK_REFERENCE_NUMBER'
    TYPE_CAMPAIGN_ENDED = 'CAMPAIGN_ENDED'
    TYPE_ACCOUNT_BUDGET_BURN_RATE = 'ACCOUNT_BUDGET_BURN_RATE'
    TYPE_USER_INVITE_PENDING = 'USER_INVITE_PENDING'
    TYPE_USER_INVITE_ACCEPTED = 'USER_INVITE_ACCEPTED'
    TYPE_MANAGER_LINK_PENDING = 'MANAGER_LINK_PENDING'
    TYPE_ZERO_DAILY_SPENDING_LIMIT = 'ZERO_DAILY_SPENDING_LIMIT'
    TYPE_TV_ACCOUNT_ON_TARGET = 'TV_ACCOUNT_ON_TARGET'
    TYPE_TV_ACCOUNT_BUDGET_ENDING = 'TV_ACCOUNT_BUDGET_ENDING'
    TYPE_TV_ZERO_DAILY_SPENDING_LIMIT = 'TV_ZERO_DAILY_SPENDING_LIMIT'
    TYPE_UNKNOWN = 'UNKNOWN'
    TYPE_CHOICES = (
        (TYPE_ACCOUNT_ON_TARGET, 'Account On Target'),
        (TYPE_DECLINED_PAYMENT, 'Declined Payment'),
        (TYPE_CREDIT_CARD_EXPIRING, 'Credit Card Expiring'),
        (TYPE_ACCOUNT_BUDGET_ENDING, 'Account Budget Ending'),
        (TYPE_CAMPAIGN_ENDING, 'Campaign Ending'),
        (TYPE_PAYMENT_NOT_ENTERED, 'Payment Not Entered'),
        (TYPE_MISSING_BANK_REFERENCE_NUMBER, 'Missing Bank Reference Number'),
        (TYPE_CAMPAIGN_ENDED, 'Campaign Ended'),
        (TYPE_ACCOUNT_BUDGET_BURN_RATE, 'Account Budget Burn Rate'),
        (TYPE_USER_INVITE_PENDING, 'User Invite Pending'),
        (TYPE_USER_INVITE_ACCEPTED, 'User Invite Accepted'),
        (TYPE_MANAGER_LINK_PENDING, 'Manager Link Pending'),
        (TYPE_ZERO_DAILY_SPENDING_LIMIT, 'Zero Daily Spending Limit'),
        (TYPE_TV_ACCOUNT_ON_TARGET, 'TV Account On Target'),
        (TYPE_TV_ACCOUNT_BUDGET_ENDING, 'TV Account Budget Ending'),
        (TYPE_TV_ZERO_DAILY_SPENDING_LIMIT, 'TV Zero Daily Spending Limit'),
        (TYPE_UNKNOWN, 'Unknown')
    )

    SEVERITY_GREEN = 'GREEN'
    SEVERITY_YELLOW = 'YELLOW'
    SEVERITY_RED = 'RED'
    SEVERITY_UNKNOWN = 'UNKNOWN'
    SEVERITY_CHOICES = (
        (SEVERITY_GREEN, 'Green'),
        (SEVERITY_YELLOW, 'Yellow'),
        (SEVERITY_RED, 'Red'),
        (SEVERITY_UNKNOWN, 'Unknown'),
    )

    account = models.ForeignKey('django_google_adwords.Account', related_name='alerts')
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    severity = models.CharField(max_length=100, choices=SEVERITY_CHOICES)
    occurred = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = QuerySetManager()

    class QuerySet(_QuerySet):
        pass

    def __unicode__(self):
        return '%s' % (self.get_type_display())


class DailyAccountMetrics(models.Model):
    DEVICE_UNKNOWN = 'Other'
    DEVICE_DESKTOP = 'Computers'
    DEVICE_HIGH_END_MOBILE = 'Mobile devices with full browsers'
    DEVICE_TABLET = 'Tablets with full browsers'
    DEVICE_CHOICES = (
        (DEVICE_UNKNOWN, DEVICE_UNKNOWN),
        (DEVICE_DESKTOP, DEVICE_DESKTOP),
        (DEVICE_HIGH_END_MOBILE, DEVICE_HIGH_END_MOBILE),
        (DEVICE_TABLET, DEVICE_TABLET)
    )

    account = models.ForeignKey('django_google_adwords.Account', related_name='metrics')
    avg_cpc = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Avg. CPC', null=True, blank=True)
    avg_cpm = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Avg. CPM', null=True, blank=True)
    avg_position = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Avg. position')
    clicks = models.IntegerField(help_text='Clicks', null=True, blank=True)
    click_conversion_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Click conversion rate')
    conv_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Conv. rate')
    converted_clicks = models.BigIntegerField(help_text='Converted clicks', null=True, blank=True)
    total_conv_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Total conv. value')
    conversions = models.BigIntegerField(help_text='Conversions', null=True, blank=True)
    cost = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Cost', null=True, blank=True)
    cost_converted_click = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Cost / converted click', null=True, blank=True)
    cost_conv = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Cost / conv.', null=True, blank=True)
    ctr = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='CTR')
    device = models.CharField(max_length=255, choices=DEVICE_CHOICES, help_text='Device')
    impressions = models.BigIntegerField(help_text='Impressions', null=True, blank=True)
    day = models.DateField(help_text='When this metric occurred')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    content_impr_share = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Content Impr. share')
    content_lost_is_rank = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Content Lost IS (rank)')
    cost_est_total_conv = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Cost / est. total conv.', null=True, blank=True)
    est_cross_device_conv = models.BigIntegerField(help_text='Est. cross-device conv.', null=True, blank=True)
    est_total_conv_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Est. total conv. rate')
    est_total_conv_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Est. total conv. value')
    est_total_conv_value_click = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Est. total conv. value / click')
    est_total_conv_value_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Est. total conv. value / cost')
    est_total_conv = models.BigIntegerField(help_text='Est. total conv.', null=True, blank=True)
    search_exact_match_is = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Search Exact match IS')
    search_impr_share = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Search Impr. share')
    search_lost_is_rank = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Search Lost IS (rank)')
    content_lost_is_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Content Lost IS (budget)')
    invalid_click_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Invalid click rate')
    invalid_clicks = models.BigIntegerField(help_text='Invalid clicks', null=True, blank=True)
    search_lost_is_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Search Lost IS (budget)')

    objects = QuerySetManager()

    def __unicode__(self):
        return '%s' % (self.day)

    class QuerySet(PopulatingGoogleAdwordsQuerySet):

        def populate(self, data, account):
            device = data.get('Device')
            day = data.get('Day')
            identifier = '%s-%s-%s' % (account.pk, device, day)

            while not acquire_googleadwords_lock(DailyAccountMetrics, identifier):
                locking_logger.debug("Waiting for acquire_googleadwords_lock: %s:%s", DailyAccountMetrics.__name__, identifier)
                time.sleep(settings.GOOGLEADWORDS_LOCK_WAIT)

            try:
                locking_logger.debug("Success acquire_googleadwords_lock: %s:%s", DailyAccountMetrics.__name__, identifier)
                return self._populate(data,
                                      ignore_fields=['account', 'account_id'],
                                      device=device,
                                      day=day,
                                      account=account)

            finally:
                locking_logger.debug("Releasing acquire_googleadwords_lock: %s:%s", DailyAccountMetrics.__name__, identifier)
                release_googleadwords_lock(DailyAccountMetrics, identifier)

        def desktop(self):
            return self.filter(device=DailyAccountMetrics.DEVICE_DESKTOP)

        def mobile(self):
            return self.filter(device=DailyAccountMetrics.DEVICE_HIGH_END_MOBILE)

        def tablet(self):
            return self.filter(device=DailyAccountMetrics.DEVICE_TABLET)

        def within_period(self, start, finish):
            return self.filter(day__gte=start, day__lte=finish)

        def total_impressions_for_period(self, start, finish):
            return self.within_period(start, finish).aggregate(Sum('impressions'))

        def daily_impressions_for_period(self, start, finish, order_by='day'):
            return self.within_period(start, finish).order_by(order_by).values('day').annotate(impressions=Sum('impressions'))

        def total_clicks_for_period(self, start, finish):
            return self.within_period(start, finish).aggregate(Sum('clicks'))

        def daily_clicks_for_period(self, start, finish, order_by='day'):
            return self.within_period(start, finish).order_by(order_by).values('day').annotate(clicks=Sum('clicks'))

        def total_cost_for_period(self, start, finish):
            return self.within_period(start, finish).aggregate(Sum('cost'))

        def daily_cost_for_period(self, start, finish, order_by='day'):
            return self.within_period(start, finish).order_by(order_by).values('day').annotate(cost=Sum('cost'))

        def average_ctr_for_period(self, start, finish):
            return self.within_period(start, finish).aggregate(Avg('ctr'))

        def daily_average_ctr_for_period(self, start, finish, order_by='day'):
            return self.within_period(start, finish).order_by(order_by).values('day').annotate(ctr=Avg('ctr'))

        def average_cpc_for_period(self, start, finish):
            return self.within_period(start, finish).aggregate(Avg('avg_cpc'))

        def daily_average_cpc_for_period(self, start, finish, order_by='day'):
            return self.within_period(start, finish).order_by(order_by).values('day').annotate(cpc=Avg('avg_cpc'))

        def total_conversions_for_period(self, start, finish):
            return self.within_period(start, finish).aggregate(Sum('conversions'))

        def daily_conversions_for_period(self, start, finish, order_by='day'):
            return self.within_period(start, finish).order_by(order_by).values('day').annotate(conversions=Sum('conversions'))

        def average_click_conversion_rate_for_period(self, start, finish):
            return self.within_period(start, finish).aggregate(Avg('click_conversion_rate'))

        def daily_average_click_conversion_rate_for_period(self, start, finish, order_by='day'):
            return self.within_period(start, finish).order_by(order_by).values('day').annotate(click_conversion_rate=Avg('click_conversion_rate'))

        def average_cost_conv_for_period(self, start, finish):
            return self.within_period(start, finish).aggregate(Avg('cost_conv'))

        def daily_average_cost_conv_for_period(self, start, finish, order_by='day'):
            return self.within_period(start, finish).order_by(order_by).values('day').annotate(cost_conv=Avg('cost_conv'))

        def average_search_lost_impression_share_budget(self, start, finish):
            return self.within_period(start, finish).aggregate(Avg('search_lost_is_budget'))

        def device_average_click_conversion_rate_for_period(self, start, finish):
            return self.within_period(start, finish).values('device').annotate(click_conversion_rate=Avg('click_conversion_rate'))

        def is_synced(self, start, finish):
            raise NotImplementedError("DailyAccountMetrics.QuerySet.is_synced() is not implemented.")
            pass
#             account_first_synced = DailyAccountMetrics.objects.filter(account=self).aggregate(Min('day'))
#             first_synced_date = None
#             if account_first_synced.has_key('day__min'):
#                 first_synced_date = account_first_synced['day__min']
#
#             if not self.last_synced or (self.last_synced - timedelta(days=1)) < finish or not first_synced_date or first_synced_date > start:


class Campaign(models.Model):
    STATE_ENABLED = 'enabled'
    STATE_PAUSED = 'paused'
    STATE_REMOVED = 'removed'
    STATE_CHOICES = (
        (STATE_ENABLED, 'Enabled'),
        (STATE_PAUSED, 'Paused'),
        (STATE_REMOVED, 'Removed')
    )

    account = models.ForeignKey('django_google_adwords.Account', related_name='campaigns')
    campaign_id = models.BigIntegerField(unique=True)
    campaign = models.CharField(max_length=255, help_text='Campaign name')
    campaign_state = models.CharField(max_length=20, choices=STATE_CHOICES)
    budget = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Budget', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = QuerySetManager()

    def __unicode__(self):
        return '%s' % (self.campaign)

    class QuerySet(PopulatingGoogleAdwordsQuerySet):

        def populate(self, data, account):
            """
            A locking get_or_create - note only the campaign_id is used in the 'get'.
            """
            campaign_id = int(data.get('Campaign ID'))

            # Get a lock based upon the campaign id
            while not acquire_googleadwords_lock(Campaign, campaign_id):
                locking_logger.debug("Waiting for acquire_googleadwords_lock: %s:%s", Campaign.__name__, campaign_id)
                time.sleep(settings.GOOGLEADWORDS_LOCK_WAIT)

            try:
                locking_logger.debug("Success acquire_googleadwords_lock: %s:%s", Campaign.__name__, campaign_id)
                return self._populate(data,
                                      ignore_fields=['account', 'account_id'],
                                      campaign_id=campaign_id,
                                      account=account)

            finally:
                locking_logger.debug("Releasing acquire_googleadwords_lock: %s:%s", Campaign.__name__, campaign_id)
                release_googleadwords_lock(Campaign, campaign_id)

        def enabled(self):
            return self.filter(campaign_state=Campaign.STATE_ENABLED)

        def paused(self):
            return self.filter(campaign_state=Campaign.STATE_PAUSED)

        def removed(self):
            return self.filter(campaign_state=Campaign.STATE_REMOVED)

    @staticmethod
    def get_selector(start=None, finish=None):
        """
        Returns the selector to pass to the api to get the data.
        """
        if not start:
            start = date.today() - timedelta(days=6)
        if not finish:
            finish = date.today() - timedelta(days=1)

        report_definition = {
            'reportName': 'Campaign Performance Report',
            'dateRangeType': 'CUSTOM_DATE',
            'reportType': 'CAMPAIGN_PERFORMANCE_REPORT',
            'downloadFormat': 'GZIPPED_CSV',
            'selector': {
                'fields': ['AccountCurrencyCode',
                           'AccountDescriptiveName',
                           'Amount',
                           'AverageCpc',
                           'AverageCpm',
                           'AveragePosition',
                           'BiddingStrategyId',
                           'BiddingStrategyName',
                           'BiddingStrategyType',
                           'CampaignId',
                           'CampaignName',
                           'CampaignStatus',
                           'Clicks',
                           'ContentBudgetLostImpressionShare',
                           'ContentImpressionShare',
                           'ContentImpressionShare',
                           'ContentRankLostImpressionShare',
                           'ContentRankLostImpressionShare',
                           'ClickConversionRate',
                           'ConversionRateManyPerClick',
                           'ConversionValue',
                           'ConvertedClicks',
                           'ConversionsManyPerClick',
                           'Cost',
                           'CostPerConvertedClick',
                           'CostPerConversionManyPerClick',
                           'CostPerEstimatedTotalConversion',
                           'CostPerEstimatedTotalConversion',
                           'Ctr',
                           'EstimatedCrossDeviceConversions',
                           'EstimatedCrossDeviceConversions',
                           'EstimatedTotalConversionRate',
                           'EstimatedTotalConversionRate',
                           'EstimatedTotalConversions',
                           'EstimatedTotalConversions',
                           'EstimatedTotalConversionValue',
                           'EstimatedTotalConversionValue',
                           'EstimatedTotalConversionValuePerClick',
                           'EstimatedTotalConversionValuePerClick',
                           'EstimatedTotalConversionValuePerCost',
                           'EstimatedTotalConversionValuePerCost',
                           'Impressions',
                           'InvalidClickRate',
                           'InvalidClicks',
                           'SearchBudgetLostImpressionShare',
                           'SearchExactMatchImpressionShare',
                           'SearchExactMatchImpressionShare',
                           'SearchImpressionShare',
                           'SearchImpressionShare',
                           'SearchRankLostImpressionShare',
                           'SearchRankLostImpressionShare',
                           'Date'],
                'dateRange': {'min': start.strftime("%Y%m%d"),
                              'max': finish.strftime("%Y%m%d")},
            },
            'includeZeroImpressions': 'true'
        }

        return report_definition

    @property
    def ads(self):
        """
        Helper to return associated Ads.
        """
        return Ad.objects.filter(ad_group__campaign=self)


class DailyCampaignMetrics(models.Model):
    BID_STRATEGY_TYPE_BUDGET_OPTIMIZER = 'auto'
    BID_STRATEGY_TYPE_CONVERSION_OPTIMIZER = 'max/target cpa'
    BID_STRATEGY_TYPE_MANUAL_CPC = 'cpc'
    BID_STRATEGY_TYPE_MANUAL_CPM = 'cpm'
    BID_STRATEGY_TYPE_PAGE_ONE_PROMOTED = 'Target search page location'
    BID_STRATEGY_TYPE_PERCENT_CPA = 'max cpa percent'
    BID_STRATEGY_TYPE_TARGET_SPEND = 'Maximize clicks'
    BID_STRATEGY_TYPE_ENHANCED_CPC = 'Enhanced CPC'
    BID_STRATEGY_TYPE_TARGET_CPA = 'Target CPA'
    BID_STRATEGY_TYPE_TARGET_ROAS = 'Target ROAS'
    BID_STRATEGY_TYPE_NONE = 'None'
    BID_STRATEGY_TYPE_UNKNOWN = 'unknown'
    BID_STRATEGY_TYPE_CHOICES = (
        (BID_STRATEGY_TYPE_BUDGET_OPTIMIZER, 'Budget Optimizer'),
        (BID_STRATEGY_TYPE_CONVERSION_OPTIMIZER, 'Conversion Optimizer'),
        (BID_STRATEGY_TYPE_MANUAL_CPC, 'Manual CPC'),
        (BID_STRATEGY_TYPE_MANUAL_CPM, 'Manual CPM'),
        (BID_STRATEGY_TYPE_PAGE_ONE_PROMOTED, 'Page One Promoted'),
        (BID_STRATEGY_TYPE_PERCENT_CPA, 'Percent CPA'),
        (BID_STRATEGY_TYPE_TARGET_SPEND, 'Target Spend'),
        (BID_STRATEGY_TYPE_ENHANCED_CPC, 'Enhanced CPC'),
        (BID_STRATEGY_TYPE_TARGET_CPA, 'Target CPA'),
        (BID_STRATEGY_TYPE_TARGET_ROAS, 'Target ROAS'),
        (BID_STRATEGY_TYPE_NONE, 'None'),
        (BID_STRATEGY_TYPE_UNKNOWN, 'Unknown')
    )

    campaign = models.ForeignKey('django_google_adwords.Campaign', related_name='metrics')
    avg_cpc = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Avg. CPC', null=True, blank=True)
    avg_cpm = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Avg. CPM', null=True, blank=True)
    avg_position = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Avg. position')
    clicks = models.IntegerField(help_text='Clicks', null=True, blank=True)
    click_conversion_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Click conversion rate')
    conv_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Conv. rate')
    converted_clicks = models.BigIntegerField(help_text='Converted clicks', null=True, blank=True)
    total_conv_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Total conv. value')
    conversions = models.BigIntegerField(help_text='Conversions', null=True, blank=True)
    cost = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Cost', null=True, blank=True)
    cost_converted_click = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Cost / converted click', null=True, blank=True)
    cost_conv = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Cost / conv.', null=True, blank=True)
    ctr = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='CTR')
    impressions = models.BigIntegerField(help_text='Impressions', null=True, blank=True)
    day = models.DateField(help_text='When this metric occurred')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    content_impr_share = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Content Impr. share')
    content_lost_is_rank = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Content Lost IS (rank)')
    cost_est_total_conv = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Cost / est. total conv.', null=True, blank=True)
    est_cross_device_conv = models.BigIntegerField(help_text='Est. cross-device conv.', null=True, blank=True)
    est_total_conv_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Est. total conv. rate')
    est_total_conv_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Est. total conv. value')
    est_total_conv_value_click = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Est. total conv. value / click')
    est_total_conv_value_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Est. total conv. value / cost')
    est_total_conv = models.BigIntegerField(help_text='Est. total conv.', null=True, blank=True)
    search_exact_match_is = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Search Exact match IS')
    search_impr_share = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Search Impr. share')
    search_lost_is_rank = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Search Lost IS (rank)')
    bid_strategy_id = models.BigIntegerField(help_text='Bid Strategy ID', null=True, blank=True)
    bid_strategy_name = models.CharField(max_length=255, null=True, blank=True)
    bid_strategy_type = models.CharField(max_length=40, choices=BID_STRATEGY_TYPE_CHOICES, help_text='Bid Strategy Type', null=True, blank=True)
    content_lost_is_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Content Lost IS (budget)')
    invalid_click_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Invalid click rate')
    invalid_clicks = models.BigIntegerField(help_text='Invalid clicks', null=True, blank=True)
    search_lost_is_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Search Lost IS (budget)')
    value_converted_click = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Value / converted click')
    value_conv = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Value / conv.')
    view_through_conv = models.BigIntegerField(help_text='View-through conv.', null=True, blank=True)

    objects = QuerySetManager()

    def __unicode__(self):
        return '%s' % (self.day)

    class QuerySet(PopulatingGoogleAdwordsQuerySet):

        def populate(self, data, campaign):
            year, month, day = [int(i) for i in data.get('Day').split('-')]
            day = date(year, month, day)
            identifier = '%s-%s' % (campaign.pk, day)

            while not acquire_googleadwords_lock(DailyCampaignMetrics, identifier):
                locking_logger.debug("Waiting for acquire_googleadwords_lock: %s:%s", DailyCampaignMetrics.__name__, identifier)
                time.sleep(settings.GOOGLEADWORDS_LOCK_WAIT)

            try:
                locking_logger.debug("Success acquire_googleadwords_lock: %s:%s", DailyCampaignMetrics.__name__, identifier)
                return self._populate(data,
                                      ignore_fields=['campaign', 'campaign_id'],
                                      day=day,
                                      campaign=campaign)

            finally:
                locking_logger.debug("Releasing acquire_googleadwords_lock: %s:%s", DailyCampaignMetrics.__name__, identifier)
                release_googleadwords_lock(DailyCampaignMetrics, identifier)

        def within_period(self, start, finish):
            return self.filter(day__gte=start, day__lte=finish)

        def total_clicks_for_period(self, start, finish):
            return self.within_period(start, finish).aggregate(Sum('clicks'))

        def total_clicks(self):
            return self.aggregate(Sum('clicks'))


class AdGroup(models.Model):
    STATE_ENABLED = 'enabled'
    STATE_PAUSED = 'paused'
    STATE_REMOVED = 'removed'
    STATE_CHOICES = (
        (STATE_ENABLED, 'Enabled'),
        (STATE_PAUSED, 'Paused'),
        (STATE_REMOVED, 'Removed')
    )

    campaign = models.ForeignKey('django_google_adwords.Campaign', related_name='ad_groups')
    ad_group_id = models.BigIntegerField(unique=True)
    ad_group = models.CharField(max_length=255, help_text='Ad group name', null=True, blank=True)
    ad_group_state = models.CharField(max_length=20, choices=STATE_CHOICES, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = QuerySetManager()

    def __unicode__(self):
        return '%s' % (self.ad_group)

    class QuerySet(PopulatingGoogleAdwordsQuerySet):

        def populate(self, data, campaign):
            """
            A locking get_or_create - note only the ad_group_id is used in the 'get'.
            """
            ad_group_id = int(data.get('Ad group ID'))

            # Get a lock based upon the ad_group_id
            while not acquire_googleadwords_lock(AdGroup, ad_group_id):
                locking_logger.debug("Waiting for acquire_googleadwords_lock: %s:%s", AdGroup.__name__, ad_group_id)
                time.sleep(settings.GOOGLEADWORDS_LOCK_WAIT)

            try:
                locking_logger.debug("Success acquire_googleadwords_lock: %s:%s", AdGroup.__name__, ad_group_id)
                return self._populate(data,
                                      ignore_fields=['campaign', 'campaign_id'],
                                      ad_group_id=ad_group_id,
                                      campaign=campaign)

            finally:
                locking_logger.debug("Releasing acquire_googleadwords_lock: %s:%s", AdGroup.__name__, ad_group_id)
                release_googleadwords_lock(AdGroup, ad_group_id)

        def top_by_clicks(self, start, finish):
            return self.filter(metrics__day__gte=start, metrics__day__lte=finish) \
                .annotate(clicks=Sum('metrics__clicks'),
                          impressions=Sum('metrics__impressions'),
                          ctr=Avg('metrics__ctr'),
                          cost=Sum('metrics__cost'),
                          avg_position=Avg('metrics__avg_position')) \
                .order_by('-clicks')

        def top_by_conversion_rate(self, start, finish):
            return self.filter(metrics__day__gte=start, metrics__day__lte=finish) \
                       .annotate(conversions=Sum('metrics__conversions'),
                                 conv_rate=Avg('metrics__conv_rate'),
                                 cost_conv=Avg('metrics__cost_conv'),
                                 impressions=Sum('metrics__impressions'),
                                 clicks=Sum('metrics__clicks'),
                                 cost=Sum('metrics__cost'),
                                 ctr=Avg('metrics__ctr'),
                                 avg_cpc=Avg('metrics__avg_cpc')) \
                       .order_by('-conversions')

        def account(self, account):
            return self.filter(campaign__account=account)

        def enabled(self):
            return self.filter(ad_group_state=AdGroup.STATE_ENABLED)

        def paused(self):
            return self.filter(ad_group_state=AdGroup.STATE_PAUSED)

        def removed(self):
            return self.filter(ad_group_state=AdGroup.STATE_REMOVED)

    @staticmethod
    def get_selector(start=None, finish=None):
        """
        Returns the selector to pass to the api to get the data.
        """
        if not start:
            start = date.today() - timedelta(days=6)
        if not finish:
            finish = date.today() - timedelta(days=1)

        report_definition = {
            'reportName': 'Ad Group Performance Report',
            'dateRangeType': 'CUSTOM_DATE',
            'reportType': 'ADGROUP_PERFORMANCE_REPORT',
            'downloadFormat': 'GZIPPED_CSV',
            'selector': {
                'fields': ['AccountCurrencyCode',
                           'AccountDescriptiveName',
                           'AdGroupId',
                           'AdGroupName',
                           'AdGroupStatus',
                           'CampaignId',
                           'CampaignName',
                           'CampaignStatus',
                           'TargetCpa',
                           'ValuePerEstimatedTotalConversion',
                           'BiddingStrategyId',
                           'BiddingStrategyName',
                           'BiddingStrategyType',
                           'ContentImpressionShare',
                           'ContentRankLostImpressionShare',
                           'CostPerEstimatedTotalConversion',
                           'EstimatedCrossDeviceConversions',
                           'EstimatedTotalConversionRate',
                           'EstimatedTotalConversionValue',
                           'EstimatedTotalConversionValuePerClick',
                           'EstimatedTotalConversionValuePerCost',
                           'EstimatedTotalConversions',
                           'SearchExactMatchImpressionShare',
                           'SearchImpressionShare',
                           'SearchRankLostImpressionShare',
                           'ValuePerConvertedClick',
                           'ValuePerConversionManyPerClick',
                           'ViewThroughConversions',
                           'AverageCpc',
                           'AverageCpm',
                           'AveragePosition',
                           'Clicks',
                           'ClickConversionRate',
                           'ConversionRateManyPerClick',
                           'ConversionValue',
                           'ConvertedClicks',
                           'ConversionsManyPerClick',
                           'Cost',
                           'CostPerConvertedClick',
                           'CostPerConversionManyPerClick',
                           'Ctr',
                           'Impressions',
                           'Date'],
                'dateRange': {'min': start.strftime("%Y%m%d"),
                              'max': finish.strftime("%Y%m%d")},
            },
            'includeZeroImpressions': 'true'
        }

        return report_definition


class DailyAdGroupMetrics(models.Model):
    BID_STRATEGY_TYPE_BUDGET_OPTIMIZER = 'auto'
    BID_STRATEGY_TYPE_CONVERSION_OPTIMIZER = 'max/target cpa'
    BID_STRATEGY_TYPE_MANUAL_CPC = 'cpc'
    BID_STRATEGY_TYPE_MANUAL_CPM = 'cpm'
    BID_STRATEGY_TYPE_PAGE_ONE_PROMOTED = 'Target search page location'
    BID_STRATEGY_TYPE_PERCENT_CPA = 'max cpa percent'
    BID_STRATEGY_TYPE_TARGET_SPEND = 'Maximize clicks'
    BID_STRATEGY_TYPE_ENHANCED_CPC = 'Enhanced CPC'
    BID_STRATEGY_TYPE_TARGET_CPA = 'Target CPA'
    BID_STRATEGY_TYPE_TARGET_ROAS = 'Target ROAS'
    BID_STRATEGY_TYPE_NONE = 'None'
    BID_STRATEGY_TYPE_UNKNOWN = 'unknown'
    BID_STRATEGY_TYPE_CHOICES = (
        (BID_STRATEGY_TYPE_BUDGET_OPTIMIZER, 'Budget Optimizer'),
        (BID_STRATEGY_TYPE_CONVERSION_OPTIMIZER, 'Conversion Optimizer'),
        (BID_STRATEGY_TYPE_MANUAL_CPC, 'Manual CPC'),
        (BID_STRATEGY_TYPE_MANUAL_CPM, 'Manual CPM'),
        (BID_STRATEGY_TYPE_PAGE_ONE_PROMOTED, 'Page One Promoted'),
        (BID_STRATEGY_TYPE_PERCENT_CPA, 'Percent CPA'),
        (BID_STRATEGY_TYPE_TARGET_SPEND, 'Target Spend'),
        (BID_STRATEGY_TYPE_ENHANCED_CPC, 'Enhanced CPC'),
        (BID_STRATEGY_TYPE_TARGET_CPA, 'Target CPA'),
        (BID_STRATEGY_TYPE_TARGET_ROAS, 'Target ROAS'),
        (BID_STRATEGY_TYPE_NONE, 'None'),
        (BID_STRATEGY_TYPE_UNKNOWN, 'Unknown')
    )

    ad_group = models.ForeignKey('django_google_adwords.AdGroup', related_name='metrics')
    avg_cpc = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Avg. CPC', null=True, blank=True)
    avg_cpm = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Avg. CPM', null=True, blank=True)
    avg_position = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Avg. position')
    clicks = models.IntegerField(help_text='Clicks', null=True, blank=True)
    click_conversion_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Click conversion rate')
    conv_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Conv. rate')
    converted_clicks = models.BigIntegerField(help_text='Converted clicks', null=True, blank=True)
    total_conv_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Total conv. value')
    conversions = models.BigIntegerField(help_text='Conversions', null=True, blank=True)
    cost = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Cost', null=True, blank=True)
    cost_converted_click = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Cost / converted click', null=True, blank=True)
    cost_conv = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Cost / conv.', null=True, blank=True)
    ctr = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='CTR')
    impressions = models.BigIntegerField(help_text='Impressions', null=True, blank=True)
    day = models.DateField(help_text='When this metric occurred')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    content_impr_share = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Content Impr. share')
    content_lost_is_rank = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Content Lost IS (rank)')
    cost_est_total_conv = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Cost / est. total conv.', null=True, blank=True)
    est_cross_device_conv = models.BigIntegerField(help_text='Est. cross-device conv.', null=True, blank=True)
    est_total_conv_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Est. total conv. rate')
    est_total_conv_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Est. total conv. value')
    est_total_conv_value_click = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Est. total conv. value / click')
    est_total_conv_value_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Est. total conv. value / cost')
    est_total_conv = models.BigIntegerField(help_text='Est. total conv.', null=True, blank=True)
    search_exact_match_is = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Search Exact match IS')
    search_impr_share = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Search Impr. share')
    search_lost_is_rank = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Search Lost IS (rank)')
    bid_strategy_id = models.BigIntegerField(help_text='Bid Strategy ID', null=True, blank=True)
    bid_strategy_name = models.CharField(max_length=255, null=True, blank=True)
    bid_strategy_type = models.CharField(max_length=40, choices=BID_STRATEGY_TYPE_CHOICES, help_text='Bid Strategy Type', null=True, blank=True)
    max_cpa_converted_clicks = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Max. CPA (converted clicks)', null=True, blank=True)
    value_est_total_conv = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Value / est. total conv.')
    value_converted_click = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Value / converted click')
    value_conv = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Value / conv.')
    view_through_conv = models.BigIntegerField(help_text='View-through conv.', null=True, blank=True)

    objects = QuerySetManager()

    def __unicode__(self):
        return '%s' % (self.day)

    class QuerySet(PopulatingGoogleAdwordsQuerySet):

        def populate(self, data, ad_group):
            day = data.get('Day')
            identifier = '%s-%s' % (ad_group.pk, day)

            while not acquire_googleadwords_lock(DailyAdGroupMetrics, identifier):
                locking_logger.debug("Waiting for acquire_googleadwords_lock: %s:%s", DailyAdGroupMetrics.__name__, identifier)
                time.sleep(settings.GOOGLEADWORDS_LOCK_WAIT)

            try:
                locking_logger.debug("Success acquire_googleadwords_lock: %s:%s", DailyAdGroupMetrics.__name__, identifier)
                return self._populate(data,
                                      ignore_fields=['ad_group', 'ad_group_id'],
                                      day=day,
                                      ad_group=ad_group)

            finally:
                locking_logger.debug("Releasing acquire_googleadwords_lock: %s:%s", DailyAdGroupMetrics.__name__, identifier)
                release_googleadwords_lock(DailyAdGroupMetrics, identifier)

        def within_period(self, start, finish):
            return self.filter(day__gte=start, day__lte=finish)

        def total_clicks_for_period(self, start, finish):
            return self.within_period(start, finish).aggregate(Sum('clicks'))

        def total_clicks(self):
            return self.aggregate(Sum('clicks'))


class Ad(models.Model):
    STATE_ENABLED = 'enabled'
    STATE_PAUSED = 'paused'
    STATE_REMOVED = 'removed'
    STATE_CHOICES = (
        (STATE_ENABLED, 'Enabled'),
        (STATE_PAUSED, 'Paused'),
        (STATE_REMOVED, 'Removed')
    )

    TYPE_DEPRECATED_AD = 'Other'
    TYPE_IMAGE_AD = 'Image ad'
    TYPE_MOBILE_AD = 'Mobile ad'
    TYPE_PRODUCT_AD = 'Product listing ad'
    TYPE_TEMPLATE_AD = 'Display ad'
    TYPE_TEXT_AD = 'Text ad'
    TYPE_THIRD_PARTY_REDIRECT_AD = 'Third party ad'
    TYPE_DYNAMIC_SEARCH_AD = 'Dynamic search ad'
    TYPE_CHOICES = (
        (TYPE_DEPRECATED_AD, 'Other'),
        (TYPE_IMAGE_AD, 'Image Ad'),
        (TYPE_MOBILE_AD, 'Mobile Ad'),
        (TYPE_PRODUCT_AD, 'Product Listing Ad'),
        (TYPE_TEMPLATE_AD, 'Display Ad'),
        (TYPE_TEXT_AD, 'Text Ad'),
        (TYPE_THIRD_PARTY_REDIRECT_AD, 'Third Party Ad'),
        (TYPE_DYNAMIC_SEARCH_AD, 'Dynamic Search Ad')
    )

    APPROVAL_STATUS_APPROVED = 'approved'
    APPROVAL_STATUS_APPROVED_NON_FAMILY = 'approved (non family)'
    APPROVAL_STATUS_APPROVED_ADULT = 'approved (adult)'
    APPROVAL_STATUS_PENDING_REVIEW = 'pending review'
    APPROVAL_STATUS_DISAPPROVED = 'disapproved'
    APPROVAL_STATUS_CHOICES = (
        (APPROVAL_STATUS_APPROVED, 'Approved'),
        (APPROVAL_STATUS_APPROVED_NON_FAMILY, 'Approved (Non Family)'),
        (APPROVAL_STATUS_APPROVED_ADULT, 'Approved (Adult)'),
        (APPROVAL_STATUS_PENDING_REVIEW, 'Pending Review'),
        (APPROVAL_STATUS_DISAPPROVED, 'Disapproved')
    )

    ad_group = models.ForeignKey('django_google_adwords.AdGroup', related_name='ads')
    ad_id = models.BigIntegerField(help_text='Googles Ad ID')
    ad_state = models.CharField(max_length=20, choices=STATE_CHOICES, null=True, blank=True)
    ad_type = models.CharField(max_length=20, choices=TYPE_CHOICES, null=True, blank=True)
    ad_approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, null=True, blank=True)
    destination_url = models.TextField(help_text='Destination URL', null=True, blank=True)
    display_url = models.TextField(help_text='Display URL', null=True, blank=True)
    ad = models.TextField(help_text='Ad/Headline', null=True, blank=True)
    description_line_1 = models.TextField(help_text='Description line 1', null=True, blank=True)
    description_line_2 = models.TextField(help_text='Description line 2', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = QuerySetManager()

    def __unicode__(self):
        return '%s' % truncatechars(self.ad, 24)

    class QuerySet(PopulatingGoogleAdwordsQuerySet):

        def populate(self, data, ad_group):
            """
            A locking get_or_create - note only the ad_id is used in the 'get'.
            """
            ad_id = int(data.get('Ad ID'))

            # Get a lock based upon the campaign id
            while not acquire_googleadwords_lock(Ad, ad_id):
                locking_logger.debug("Waiting for acquire_googleadwords_lock: %s:%s", Ad.__name__, ad_id)
                time.sleep(settings.GOOGLEADWORDS_LOCK_WAIT)

            try:
                locking_logger.debug("Success acquire_googleadwords_lock: %s:%s", Ad.__name__, ad_id)
                return self._populate(data,
                                      ignore_fields=['ad_group', 'ad_group_id'],
                                      ad_id=ad_id,
                                      ad_group=ad_group)

            finally:
                locking_logger.debug("Releasing acquire_googleadwords_lock: %s:%s", Ad.__name__, ad_id)
                release_googleadwords_lock(Ad, ad_id)

        def top_by_clicks(self, start, finish):
            return self.filter(metrics__day__gte=start, metrics__day__lte=finish) \
                       .annotate(clicks=Sum('metrics__clicks'),
                                 impressions=Sum('metrics__impressions'),
                                 ctr=Avg('metrics__ctr'),
                                 cost=Sum('metrics__cost'),
                                 avg_position=Avg('metrics__avg_position')) \
                       .order_by('-clicks')

        def top_by_conversion_rate(self, start, finish):
            return self.filter(metrics__day__gte=start, metrics__day__lte=finish) \
                       .annotate(conversions=Sum('metrics__conversions'),
                                 conv_rate=Avg('metrics__conv_rate'),
                                 cost_conv=Avg('metrics__cost_conv'),
                                 impressions=Sum('metrics__impressions'),
                                 clicks=Sum('metrics__clicks'),
                                 cost=Sum('metrics__cost'),
                                 ctr=Avg('metrics__ctr'),
                                 avg_cpc=Avg('metrics__avg_cpc')) \
                       .order_by('-conversions')

        def account(self, account):
            return self.filter(ad_group__campaign__account=account)

        def enabled(self):
            return self.filter(ad_state=Ad.STATE_ENABLED)

        def paused(self):
            return self.filter(ad_state=Ad.STATE_PAUSED)

        def removed(self):
            return self.filter(ad_state=Ad.STATE_REMOVED)

        def text(self):
            return self.filter(ad_type=Ad.TYPE_TEXT_AD)

    @staticmethod
    def get_selector(start=None, finish=None):
        """
        Returns the selector to pass to the api to get the data.
        """
        if not start:
            start = date.today() - timedelta(days=6)
        if not finish:
            finish = date.today() - timedelta(days=1)

        report_definition = {
            'reportName': 'Ad Performance Report',
            'dateRangeType': 'CUSTOM_DATE',
            'reportType': 'AD_PERFORMANCE_REPORT',
            'downloadFormat': 'GZIPPED_CSV',
            'selector': {
                'fields': ['AccountCurrencyCode',
                           'AccountDescriptiveName',
                           'AdGroupId',
                           'AdGroupName',
                           'AdGroupStatus',
                           'AdType',
                           'AverageCpc',
                           'AverageCpm',
                           'AveragePosition',
                           'CampaignId',
                           'CampaignName',
                           'CampaignStatus',
                           'Clicks',
                           'ClickConversionRate',
                           'ConversionRateManyPerClick',
                           'ConversionValue',
                           'ConvertedClicks',
                           'ConversionsManyPerClick',
                           'Cost',
                           'CostPerConvertedClick',
                           'CostPerConversionManyPerClick',
                           'CreativeApprovalStatus',
                           'CreativeDestinationUrl',
                           'Ctr',
                           'Description1',
                           'Description2',
                           'DisplayUrl',
                           'Headline',
                           'Id',
                           'Impressions',
                           'Status',
                           'ValuePerConvertedClick',
                           'ValuePerConversionManyPerClick',
                           'ViewThroughConversions',
                           'Date'],
                'dateRange': {'min': start.strftime("%Y%m%d"),
                              'max': finish.strftime("%Y%m%d")},
            },
            'includeZeroImpressions': 'true'
        }

        return report_definition


class DailyAdMetrics(models.Model):
    ad = models.ForeignKey('django_google_adwords.Ad', related_name='metrics')
    avg_cpc = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Avg. CPC', null=True, blank=True)
    avg_cpm = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Avg. CPM', null=True, blank=True)
    avg_position = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Avg. position')
    clicks = models.IntegerField(help_text='Clicks', null=True, blank=True)
    click_conversion_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Click conversion rate')
    conv_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Conv. rate')
    converted_clicks = models.BigIntegerField(help_text='Converted clicks', null=True, blank=True)
    total_conv_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Total conv. value')
    conversions = models.BigIntegerField(help_text='Conversions', null=True, blank=True)
    cost = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Cost', null=True, blank=True)
    cost_converted_click = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Cost / converted click', null=True, blank=True)
    cost_conv = MoneyField(max_digits=12, decimal_places=2, default=0, help_text='Cost / conv.', null=True, blank=True)
    ctr = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='CTR')
    impressions = models.BigIntegerField(help_text='Impressions', null=True, blank=True)
    day = models.DateField(help_text='When this metric occurred')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    value_converted_click = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Value / converted click')
    value_conv = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Value / conv.')
    view_through_conv = models.BigIntegerField(help_text='View-through conv.', null=True, blank=True)

    objects = QuerySetManager()

    def __unicode__(self):
        return '%s' % self.day

    class QuerySet(PopulatingGoogleAdwordsQuerySet):

        def populate(self, data, ad):
            day = data.get('Day')
            identifier = '%s-%s' % (ad.pk, day)

            while not acquire_googleadwords_lock(DailyAdMetrics, identifier):
                locking_logger.debug("Waiting for acquire_googleadwords_lock: %s:%s", DailyAdMetrics.__name__, identifier)
                time.sleep(settings.GOOGLEADWORDS_LOCK_WAIT)

            try:
                locking_logger.debug("Success acquire_googleadwords_lock: %s:%s", DailyAdMetrics.__name__, identifier)
                return self._populate(data,
                                      ignore_fields=['ad', 'ad_id'],
                                      day=day,
                                      ad=ad)

            finally:
                locking_logger.debug("Releasing acquire_googleadwords_lock: %s:%s", DailyAdMetrics.__name__, identifier)
                release_googleadwords_lock(DailyAdMetrics, identifier)


def reportfile_file_upload_to(instance, filename):
    filename = "%s%s" % (instance.pk, os.path.splitext(filename)[1])
    today = date.today()
    return os.path.join(settings.GOOGLEADWORDS_REPORT_FILE_ROOT,
                        today.strftime("%Y"),
                        today.strftime("%m"),
                        today.strftime("%d"),
                        filename)


class ReportFile(models.Model):
    file = models.FileField(max_length=255, upload_to=reportfile_file_upload_to, null=True, blank=True)
    processed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    objects = QuerySetManager()

    def __unicode__(self):
        return '%s' % self.file

    class QuerySet(_QuerySet):
        def request(self, report_definition, client_customer_id):
            """
            Fields and report types can be found here https://developers.google.com/adwords/api/docs/appendix/reports

            client_customer_id='591-877-6172'

            report_definition = {
                'reportName': 'Account Performance Report',
                'dateRangeType': 'CUSTOM_DATE',
                'reportType': 'ACCOUNT_PERFORMANCE_REPORT',
                'downloadFormat': 'GZIPPED_CSV',
                'selector': {
                    'fields': ['AverageCpc',
                               'Clicks',
                               'Impressions',
                               'Cost',
                               'ConvertedClicks',
                               'Date'],
                    'dateRange': {
                        'min': '20140501',
                        'max': '20140601'
                    },
                },
                # Enable to get rows with zero impressions.
                'includeZeroImpressions': 'false'
            }

            Example usage of return data

            for metric, value in r['report']['table']['row'].iteritems():
                print metric, value

            @param report_definition: A dict of values used to specify a report to get from the API.
            @param client_customer_id: A string containing the Adwords Customer Client ID.
            @return OrderedDict containing report
            """
            client = adwords_service(client_customer_id)
            report_downloader = client.GetReportDownloader(version=settings.GOOGLEADWORDS_CLIENT_VERSION)

            try:
                report_file = ReportFile.objects.create()
                with report_file.file_manager('%s.gz' % report_file.pk) as f:
                    report_downloader.DownloadReport(report_definition, output=f)
                return report_file
            except GoogleAdsError as e:
                report_file.delete()  # cleanup
                if not hasattr(e, 'fault') or not hasattr(e.fault, 'detail') or not hasattr(e.fault.detail, 'ApiExceptionFault') or not hasattr(e.fault.detail.ApiExceptionFault, 'errors'):
                    # If they aren't telling us to retryAfterSeconds - raise
                    raise
                retryAfterSeconds = sum([int(fault.retryAfterSeconds) for fault in e.fault.detail.ApiExceptionFault.errors if getattr(fault, 'ApiError.Type') == 'RateExceededError'])
                if retryAfterSeconds > 0:
                    # We've hit a RateExceededError - raise
                    raise RateExceededError(retryAfterSeconds)
                else:
                    # We haven't hit an error we care about, raise it.
                    raise

    @contextmanager
    def file_manager(self, filename):
        """
        Yields a temporary file like object which is then saved.

        This can be used to safely write to the file attribute and ensure that
        upon an error the file is removed (ie.. there is cleanup).
        """
        self.file.name = reportfile_file_upload_to(self, filename)
        # Ensure directory exists
        path = os.path.dirname(self.file.path)
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

        # Write to file
        with open(self.file.path, mode='wb') as f:
            yield f
            self.save()

    def save_path(self, path):
        """
        Save a path to the file attribute.
        """
        self.file.save(os.path.basename(path), File(open(path, 'rb')))

    def save_file(self, f):
        """
        Save a file like object to the file attribute.
        """
        self.file.save(os.path.basename(f.name), File(f))

    def dehydrate(self):
        """
        Yield each row in the report as a dict.
        """
        name = None
        fields = None
        with gzip.open(self.file.path, 'rt') as csv_file:
            csv_reader = UnicodeReader(csv_file)
            for row in csv_reader:
                if name is None:
                    name = row
                elif fields is None:
                    fields = row
                # @hack - dirty but it will work for now!
                elif row[0] != 'Total':
                    yield dict(zip(fields, row))


def receiver_delete_reportfile(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)
post_delete.connect(receiver_delete_reportfile, ReportFile)
