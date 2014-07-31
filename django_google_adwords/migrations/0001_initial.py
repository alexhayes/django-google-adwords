# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Account'
        db.create_table(u'django_google_adwords_account', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account_id', self.gf('django.db.models.fields.BigIntegerField')(unique=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='active', max_length=32)),
            ('account', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('account_last_synced', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('campaign_last_synced', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('ad_group_last_synced', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('ad_last_synced', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'django_google_adwords', ['Account'])

        # Adding model 'Alert'
        db.create_table(u'django_google_adwords_alert', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='alerts', to=orm['django_google_adwords.Account'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('severity', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('occurred', self.gf('django.db.models.fields.DateTimeField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'django_google_adwords', ['Alert'])

        # Adding model 'DailyAccountMetrics'
        db.create_table(u'django_google_adwords_dailyaccountmetrics', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='metrics', to=orm['django_google_adwords.Account'])),
            ('avg_cpc_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('avg_cpc', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('avg_cpm_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('avg_cpm', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('avg_position', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('clicks', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('click_conversion_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('conv_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('converted_clicks', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('total_conv_value', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('conversions', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('cost_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('cost', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('cost_converted_click_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('cost_converted_click', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('cost_conv_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('cost_conv', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('ctr', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('device', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('impressions', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('day', self.gf('django.db.models.fields.DateField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('content_impr_share', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('content_lost_is_rank', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('cost_est_total_conv_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('cost_est_total_conv', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('est_cross_device_conv', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('est_total_conv_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('est_total_conv_value', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('est_total_conv_value_click', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('est_total_conv_value_cost', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('est_total_conv', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('search_exact_match_is', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('search_impr_share', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('search_lost_is_rank', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('content_lost_is_budget', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('invalid_click_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('invalid_clicks', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('search_lost_is_budget', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
        ))
        db.send_create_signal(u'django_google_adwords', ['DailyAccountMetrics'])

        # Adding model 'Campaign'
        db.create_table(u'django_google_adwords_campaign', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='campaigns', to=orm['django_google_adwords.Account'])),
            ('campaign_id', self.gf('django.db.models.fields.BigIntegerField')(unique=True)),
            ('campaign', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('campaign_state', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('budget_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('budget', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'django_google_adwords', ['Campaign'])

        # Adding model 'DailyCampaignMetrics'
        db.create_table(u'django_google_adwords_dailycampaignmetrics', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('campaign', self.gf('django.db.models.fields.related.ForeignKey')(related_name='metrics', to=orm['django_google_adwords.Campaign'])),
            ('avg_cpc_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('avg_cpc', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('avg_cpm_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('avg_cpm', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('avg_position', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('clicks', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('click_conversion_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('conv_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('converted_clicks', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('total_conv_value', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('conversions', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('cost_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('cost', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('cost_converted_click_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('cost_converted_click', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('cost_conv_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('cost_conv', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('ctr', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('impressions', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('day', self.gf('django.db.models.fields.DateField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('content_impr_share', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('content_lost_is_rank', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('cost_est_total_conv_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('cost_est_total_conv', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('est_cross_device_conv', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('est_total_conv_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('est_total_conv_value', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('est_total_conv_value_click', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('est_total_conv_value_cost', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('est_total_conv', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('search_exact_match_is', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('search_impr_share', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('search_lost_is_rank', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('bid_strategy_id', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('bid_strategy_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('bid_strategy_type', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('content_lost_is_budget', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('invalid_click_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('invalid_clicks', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('search_lost_is_budget', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('value_converted_click', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('value_conv', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('view_through_conv', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'django_google_adwords', ['DailyCampaignMetrics'])

        # Adding model 'AdGroup'
        db.create_table(u'django_google_adwords_adgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('campaign', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ad_groups', to=orm['django_google_adwords.Campaign'])),
            ('ad_group_id', self.gf('django.db.models.fields.BigIntegerField')(unique=True)),
            ('ad_group', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('ad_group_state', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'django_google_adwords', ['AdGroup'])

        # Adding model 'DailyAdGroupMetrics'
        db.create_table(u'django_google_adwords_dailyadgroupmetrics', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ad_group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='metrics', to=orm['django_google_adwords.AdGroup'])),
            ('avg_cpc_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('avg_cpc', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('avg_cpm_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('avg_cpm', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('avg_position', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('clicks', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('click_conversion_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('conv_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('converted_clicks', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('total_conv_value', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('conversions', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('cost_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('cost', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('cost_converted_click_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('cost_converted_click', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('cost_conv_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('cost_conv', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('ctr', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('impressions', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('day', self.gf('django.db.models.fields.DateField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('content_impr_share', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('content_lost_is_rank', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('cost_est_total_conv_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('cost_est_total_conv', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('est_cross_device_conv', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('est_total_conv_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('est_total_conv_value', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('est_total_conv_value_click', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('est_total_conv_value_cost', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('est_total_conv', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('search_exact_match_is', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('search_impr_share', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('search_lost_is_rank', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('bid_strategy_id', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('bid_strategy_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('bid_strategy_type', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('max_cpa_converted_clicks_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('max_cpa_converted_clicks', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('value_est_total_conv', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('value_converted_click', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('value_conv', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('view_through_conv', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'django_google_adwords', ['DailyAdGroupMetrics'])

        # Adding model 'Ad'
        db.create_table(u'django_google_adwords_ad', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ad_group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ads', to=orm['django_google_adwords.AdGroup'])),
            ('ad_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('ad_state', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('ad_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('destination_url', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('display_url', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ad', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description_line1', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description_line2', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'django_google_adwords', ['Ad'])

        # Adding model 'DailyAdMetrics'
        db.create_table(u'django_google_adwords_dailyadmetrics', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ad', self.gf('django.db.models.fields.related.ForeignKey')(related_name='metrics', to=orm['django_google_adwords.Ad'])),
            ('avg_cpc_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('avg_cpc', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('avg_cpm_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('avg_cpm', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('avg_position', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('clicks', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('click_conversion_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('conv_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('converted_clicks', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('total_conv_value', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('conversions', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('cost_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('cost', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('cost_converted_click_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('cost_converted_click', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('cost_conv_currency', self.gf('money.contrib.django.models.fields.CurrencyField')(default='AUD', max_length=3)),
            ('cost_conv', self.gf('money.contrib.django.models.fields.MoneyField')(decimal_places=2, default=0, no_currency_field=True, max_digits=12, blank=True, null=True)),
            ('ctr', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('impressions', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('day', self.gf('django.db.models.fields.DateField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('value_converted_click', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('value_conv', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('view_through_conv', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'django_google_adwords', ['DailyAdMetrics'])

        # Adding model 'ReportFile'
        db.create_table(u'django_google_adwords_reportfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=255, null=True, blank=True)),
            ('processed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'django_google_adwords', ['ReportFile'])


    def backwards(self, orm):
        # Deleting model 'Account'
        db.delete_table(u'django_google_adwords_account')

        # Deleting model 'Alert'
        db.delete_table(u'django_google_adwords_alert')

        # Deleting model 'DailyAccountMetrics'
        db.delete_table(u'django_google_adwords_dailyaccountmetrics')

        # Deleting model 'Campaign'
        db.delete_table(u'django_google_adwords_campaign')

        # Deleting model 'DailyCampaignMetrics'
        db.delete_table(u'django_google_adwords_dailycampaignmetrics')

        # Deleting model 'AdGroup'
        db.delete_table(u'django_google_adwords_adgroup')

        # Deleting model 'DailyAdGroupMetrics'
        db.delete_table(u'django_google_adwords_dailyadgroupmetrics')

        # Deleting model 'Ad'
        db.delete_table(u'django_google_adwords_ad')

        # Deleting model 'DailyAdMetrics'
        db.delete_table(u'django_google_adwords_dailyadmetrics')

        # Deleting model 'ReportFile'
        db.delete_table(u'django_google_adwords_reportfile')


    models = {
        u'django_google_adwords.account': {
            'Meta': {'object_name': 'Account'},
            'account': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'account_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'}),
            'account_last_synced': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'ad_group_last_synced': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'ad_last_synced': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'campaign_last_synced': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '32'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'django_google_adwords.ad': {
            'Meta': {'object_name': 'Ad'},
            'ad': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ad_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ads'", 'to': u"orm['django_google_adwords.AdGroup']"}),
            'ad_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'ad_state': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'ad_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description_line1': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_line2': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'destination_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'django_google_adwords.adgroup': {
            'Meta': {'object_name': 'AdGroup'},
            'ad_group': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'ad_group_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'}),
            'ad_group_state': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ad_groups'", 'to': u"orm['django_google_adwords.Campaign']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'django_google_adwords.alert': {
            'Meta': {'object_name': 'Alert'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'alerts'", 'to': u"orm['django_google_adwords.Account']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'occurred': ('django.db.models.fields.DateTimeField', [], {}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'django_google_adwords.campaign': {
            'Meta': {'object_name': 'Campaign'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'campaigns'", 'to': u"orm['django_google_adwords.Account']"}),
            'budget': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'budget_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'campaign': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'campaign_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'}),
            'campaign_state': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'django_google_adwords.dailyaccountmetrics': {
            'Meta': {'object_name': 'DailyAccountMetrics'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metrics'", 'to': u"orm['django_google_adwords.Account']"}),
            'avg_cpc': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'avg_cpc_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'avg_cpm': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'avg_cpm_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'avg_position': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'click_conversion_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'clicks': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_impr_share': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'content_lost_is_budget': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'content_lost_is_rank': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'conv_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'conversions': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'converted_clicks': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cost': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'cost_conv': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'cost_conv_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'cost_converted_click': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'cost_converted_click_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'cost_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'cost_est_total_conv': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'cost_est_total_conv_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'ctr': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'day': ('django.db.models.fields.DateField', [], {}),
            'device': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'est_cross_device_conv': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'est_total_conv': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'est_total_conv_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'est_total_conv_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'est_total_conv_value_click': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'est_total_conv_value_cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impressions': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'invalid_click_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'invalid_clicks': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'search_exact_match_is': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'search_impr_share': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'search_lost_is_budget': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'search_lost_is_rank': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'total_conv_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'django_google_adwords.dailyadgroupmetrics': {
            'Meta': {'object_name': 'DailyAdGroupMetrics'},
            'ad_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metrics'", 'to': u"orm['django_google_adwords.AdGroup']"}),
            'avg_cpc': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'avg_cpc_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'avg_cpm': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'avg_cpm_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'avg_position': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'bid_strategy_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bid_strategy_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'bid_strategy_type': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'click_conversion_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'clicks': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_impr_share': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'content_lost_is_rank': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'conv_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'conversions': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'converted_clicks': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cost': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'cost_conv': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'cost_conv_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'cost_converted_click': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'cost_converted_click_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'cost_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'cost_est_total_conv': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'cost_est_total_conv_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'ctr': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'day': ('django.db.models.fields.DateField', [], {}),
            'est_cross_device_conv': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'est_total_conv': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'est_total_conv_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'est_total_conv_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'est_total_conv_value_click': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'est_total_conv_value_cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impressions': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_cpa_converted_clicks': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'max_cpa_converted_clicks_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'search_exact_match_is': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'search_impr_share': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'search_lost_is_rank': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'total_conv_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'value_conv': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'value_converted_click': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'value_est_total_conv': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'view_through_conv': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'django_google_adwords.dailyadmetrics': {
            'Meta': {'object_name': 'DailyAdMetrics'},
            'ad': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metrics'", 'to': u"orm['django_google_adwords.Ad']"}),
            'avg_cpc': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'avg_cpc_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'avg_cpm': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'avg_cpm_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'avg_position': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'click_conversion_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'clicks': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'conv_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'conversions': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'converted_clicks': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cost': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'cost_conv': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'cost_conv_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'cost_converted_click': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'cost_converted_click_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'cost_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'ctr': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'day': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impressions': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'total_conv_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'value_conv': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'value_converted_click': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'view_through_conv': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'django_google_adwords.dailycampaignmetrics': {
            'Meta': {'object_name': 'DailyCampaignMetrics'},
            'avg_cpc': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'avg_cpc_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'avg_cpm': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'avg_cpm_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'avg_position': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'bid_strategy_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bid_strategy_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'bid_strategy_type': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metrics'", 'to': u"orm['django_google_adwords.Campaign']"}),
            'click_conversion_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'clicks': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_impr_share': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'content_lost_is_budget': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'content_lost_is_rank': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'conv_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'conversions': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'converted_clicks': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cost': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'cost_conv': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'cost_conv_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'cost_converted_click': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'cost_converted_click_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'cost_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'cost_est_total_conv': ('money.contrib.django.models.fields.MoneyField', [], {'decimal_places': '2', 'default': '0', 'no_currency_field': 'True', 'max_digits': '12', 'blank': 'True', 'null': 'True'}),
            'cost_est_total_conv_currency': ('money.contrib.django.models.fields.CurrencyField', [], {'default': "'AUD'", 'max_length': '3'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'ctr': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'day': ('django.db.models.fields.DateField', [], {}),
            'est_cross_device_conv': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'est_total_conv': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'est_total_conv_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'est_total_conv_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'est_total_conv_value_click': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'est_total_conv_value_cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impressions': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'invalid_click_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'invalid_clicks': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'search_exact_match_is': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'search_impr_share': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'search_lost_is_budget': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'search_lost_is_rank': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'total_conv_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'value_conv': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'value_converted_click': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'view_through_conv': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'django_google_adwords.reportfile': {
            'Meta': {'object_name': 'ReportFile'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['django_google_adwords']