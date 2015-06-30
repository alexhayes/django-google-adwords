from __future__ import absolute_import

from datetime import date, datetime
from decimal import Decimal
import os

from django_google_adwords.models import ReportFile, Account, Campaign, AdGroup, \
    DailyAccountMetrics, DailyCampaignMetrics, DailyAdGroupMetrics, Ad, \
    DailyAdMetrics
from django.test.testcases import TestCase, TransactionTestCase


def _get_test_media_file_path(name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'media', name)


def _get_report_file(name):
    report_file = ReportFile.objects.create()  #: :type report_file: ReportFile
    report_file.save_path(_get_test_media_file_path(name))
    return report_file


class DjangoGoogleAdwordsTestCase(TransactionTestCase):
    fixtures = [
        'django_google_adwords.yaml'
    ]
    
    def test_account_update_from_initial(self):
        report_file = _get_report_file('account_report.gz')

        # Check that initial values are Null
        account = Account.objects.get(pk=1)
        self.assertEqual(account.account, None)
        self.assertEqual(account.currency, None)
        self.assertEqual(account.account_last_synced, None)

        # Run the Account report populate
        account.start_sync()
        account.sync_account(report_file=report_file)
        account.finish_account_sync()
        account.finish_sync()

        # Check that the Account fields have been updated
        account = Account.objects.get(pk=1)
        self.assertEqual(account.account, 'example.com.au')
        self.assertEqual(account.currency, 'AUD')

    def test_campaign_create(self):
        report_file = _get_report_file('campaign_report.gz')

        # Run the Campaign report populate
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_campaign(report_file=report_file)
        account.finish_campaign_sync()
        account.finish_sync()

        # Check that the Campaigns have been populated
        account = Account.objects.get(pk=1)
        campaigns = account.campaigns.all()
        self.assertEqual(campaigns.count(), 5)

        # Check campaign attributes populated correctly
        c1 = Campaign.objects.get(campaign_id=7679201)
        self.assertEqual(c1.account, account)
        self.assertEqual(c1.campaign, 'Campaign #1')
        self.assertEqual(c1.campaign_state, Campaign.STATE_PAUSED)
        self.assertEqual(c1.budget.amount, Decimal('10.0'))

        c2 = Campaign.objects.get(campaign_id=7679441)
        self.assertEqual(c2.account, account)
        self.assertEqual(c2.campaign, 'Campaign #2')
        self.assertEqual(c2.campaign_state, Campaign.STATE_PAUSED)
        self.assertEqual(c2.budget.amount, Decimal('3.0'))

        c3 = Campaign.objects.get(campaign_id=7679621)
        self.assertEqual(c3.account, account)
        self.assertEqual(c3.campaign, 'Campaign #3')
        self.assertEqual(c3.campaign_state, Campaign.STATE_PAUSED)
        self.assertEqual(c3.budget.amount, Decimal('4.0'))

        c4 = Campaign.objects.get(campaign_id=7756901)
        self.assertEqual(c4.account, account)
        self.assertEqual(c4.campaign, 'Campaign #4')
        self.assertEqual(c4.campaign_state, Campaign.STATE_REMOVED)
        self.assertEqual(c4.budget.amount, Decimal('15.0'))

        c5 = Campaign.objects.get(campaign_id=7783061)
        self.assertEqual(c5.account, account)
        self.assertEqual(c5.campaign, 'Campaign #5')
        self.assertEqual(c5.campaign_state, Campaign.STATE_PAUSED)
        self.assertEqual(c5.budget.amount, Decimal('8.0'))

    def test_campaign_update(self):
        # Run the Campaign report populate
        report_file = _get_report_file('campaign_report.gz')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_campaign(report_file=report_file)
        account.finish_campaign_sync()
        account.finish_sync()

        # Check campaign attributes populated correctly
        c = Campaign.objects.get(campaign_id=7679201)
        self.assertEqual(c.campaign, 'Campaign #1')
        self.assertEqual(c.campaign_state, Campaign.STATE_PAUSED)
        self.assertEqual(c.budget.amount, Decimal('10.0'))

        # Run the updated Campaign report populate
        report_file = _get_report_file('campaign_report_update.gz')
        account.start_sync()
        account.sync_campaign(report_file=report_file)
        account.finish_account_sync()
        account.finish_sync()

        # Check campaign attributes updated correctly
        uc = Campaign.objects.get(campaign_id=7679201)
        self.assertEqual(uc.campaign, 'Campaign #1')
        self.assertEqual(uc.campaign_state, Campaign.STATE_ENABLED)
        self.assertEqual(uc.budget.amount, Decimal('100.0'))

    def test_ad_group_create(self):
        report_file = _get_report_file('adgroup_report.gz')

        # Run the Ad Group report populate
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad_group(report_file=report_file)
        account.finish_ad_group_sync()
        account.finish_sync()

        # Check that the Ad Groups have been populated
        account = Account.objects.get(pk=1)
        ad_groups = AdGroup.objects.filter(campaign__account=account)
        self.assertEqual(ad_groups.count(), 5)

        # Check Ad Group attributes populated correctly
        ad_group = AdGroup.objects.get(ad_group_id=323809001)
        self.assertEqual(ad_group.campaign.campaign_id, 7679201)
        self.assertEqual(ad_group.ad_group, 'AdGroup #1')
        self.assertEqual(ad_group.ad_group_state, AdGroup.STATE_PAUSED)

    def test_ad_group_update(self):
        # Run the Ad Group report populate
        report_file = _get_report_file('adgroup_report.gz')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad_group(report_file=report_file)
        account.finish_ad_group_sync()
        account.finish_sync()

        # Run the Ad Group report populate to update rows
        report_file = _get_report_file('adgroup_report_update.gz')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad_group(report_file=report_file)
        account.finish_ad_group_sync()
        account.finish_sync()

        # Check Ad Group attributes updated correctly
        ad_group = AdGroup.objects.get(ad_group_id=323809001)
        self.assertEqual(ad_group.campaign.campaign_id, 7679201)
        self.assertEqual(ad_group.ad_group, 'AdGroup #1')
        self.assertEqual(ad_group.ad_group_state, AdGroup.STATE_ENABLED)

    def test_ad_create(self):
        # Run the Ad report populate
        report_file = _get_report_file('ad_report.gz')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad(report_file=report_file)
        account.finish_ad_sync()
        account.finish_sync()

        # Check that the Ads have been populated
        account = Account.objects.get(pk=1)
        ads = Ad.objects.filter(ad_group__campaign__account=account)
        self.assertEqual(ads.count(), 44)

        # Check Ad attributes populated correctly
        ad = Ad.objects.get(ad_id=40564055441)
        self.assertEqual(ad.ad_state, Ad.STATE_ENABLED)
        self.assertEqual(ad.ad_type, Ad.TYPE_TEXT_AD)
        self.assertEqual(ad.destination_url, 'http://example.net.au/Home.php')
        self.assertEqual(ad.display_url, 'example.net.au')
        self.assertEqual(ad.ad, 'Doncaster Real Estate')

        self.assertEqual(ad.description_line_1, 'Trusted by Victorian Home Owners.')
        self.assertEqual(ad.description_line_2, '90 Years Exp Request Free Appraisal')

    def test_ad_update(self):
        # Run the Ad report populate
        report_file = _get_report_file('ad_report.gz')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad(report_file=report_file)
        account.finish_ad_sync()
        account.finish_sync()

        # Run the Ad report populate update
        report_file = _get_report_file('ad_report_update.gz')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad(report_file=report_file)
        account.finish_ad_sync()
        account.finish_sync()

        # Check that the Ads have been updated and there are still only 9
        account = Account.objects.get(pk=1)
        ads = Ad.objects.filter(ad_group__campaign__account=account)
        self.assertEqual(ads.count(), 44)

        # Check Ad attributes updated correctly
        ad = Ad.objects.get(ad_id=40564055441)
        self.assertEqual(ad.ad_state, Ad.STATE_ENABLED)
        self.assertEqual(ad.ad_type, Ad.TYPE_TEXT_AD)
        self.assertEqual(ad.destination_url, 'http://example.net.au/Home2.php')
        self.assertEqual(ad.display_url, 'example.net.au/test')
        self.assertEqual(ad.ad, 'Doncaster Real Estate')
        self.assertEqual(ad.description_line_1, 'Trusted by Victorian Home Owners. FTW')
        self.assertEqual(ad.description_line_2, '90 Years Exp Request Free Appraisal FTW')

    def test_daily_account_metrics_create(self):
        report_file = _get_report_file('account_report.gz')

        # Run the Account report populate
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_account(report_file=report_file)
        account.finish_account_sync()
        account.finish_sync()

        # Check that the Daily Account Metrics have been populated
        account_metrics = DailyAccountMetrics.objects.filter(account=account)
        self.assertEqual(account_metrics.count(), 30)

        # Check the fields of one of them
        account_metric = DailyAccountMetrics.objects.get(account=account, device=DailyAccountMetrics.DEVICE_DESKTOP, day=date(2014, 7, 28))
        self.assertEqual(account_metric.avg_cpc.amount, Decimal('1.91'))
        self.assertEqual(account_metric.avg_cpm.amount, Decimal('1.85'))
        self.assertEqual(account_metric.avg_position, Decimal('1.0'))
        self.assertEqual(account_metric.clicks, 5)
        self.assertEqual(account_metric.content_lost_is_budget, Decimal('23.39'))
        self.assertEqual(account_metric.content_impr_share, Decimal('10.00'))
        self.assertEqual(account_metric.content_lost_is_rank, Decimal('73.41'))
        self.assertEqual(account_metric.click_conversion_rate, Decimal('0.0'))
        self.assertEqual(account_metric.conv_rate, Decimal('0.0'))
        self.assertEqual(account_metric.converted_clicks, 0)
        self.assertEqual(account_metric.converted_clicks, 0)
        self.assertEqual(account_metric.cost.amount, Decimal('9.57'))
        self.assertEqual(account_metric.cost_converted_click.amount, Decimal('0.00'))
        self.assertEqual(account_metric.cost_conv.amount, Decimal('0.00'))
        self.assertEqual(account_metric.cost_est_total_conv.amount, Decimal('0.00'))
        self.assertEqual(account_metric.ctr, Decimal('0.10'))
        self.assertEqual(account_metric.est_cross_device_conv, None)
        self.assertEqual(account_metric.est_total_conv_rate, Decimal('0.00'))
        self.assertEqual(account_metric.est_total_conv_value, Decimal('0.00'))
        self.assertEqual(account_metric.est_total_conv_value_click, Decimal('0.00'))
        self.assertEqual(account_metric.est_total_conv_value_cost, Decimal('0.00'))
        self.assertEqual(account_metric.est_total_conv, 0)
        self.assertEqual(account_metric.impressions, 5183)
        self.assertEqual(account_metric.invalid_click_rate, Decimal('0.00'))
        self.assertEqual(account_metric.invalid_clicks, 0)
        self.assertEqual(account_metric.search_lost_is_budget, Decimal('23.81'))
        self.assertEqual(account_metric.search_exact_match_is, Decimal('76.19'))
        self.assertEqual(account_metric.search_impr_share, Decimal('76.19'))
        self.assertEqual(account_metric.search_lost_is_rank, Decimal('0.00'))

    def test_daily_account_metrics_update(self):
        # Run the Account report populate
        report_file = _get_report_file('account_report.gz')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_account(report_file=report_file)
        account.finish_account_sync()
        account.finish_sync()

        # Run the Account report populate with data to update
        report_file = _get_report_file('account_report_update.gz')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_account(report_file=report_file)
        account.finish_account_sync()
        account.finish_sync()

        # Check that the Daily Account Metrics have been populated
        account_metrics = DailyAccountMetrics.objects.filter(account=account)
        self.assertEqual(account_metrics.count(), 30)

        # Check the fields of one of them to ensure the update occurred correctly
        account_metric = DailyAccountMetrics.objects.get(account=account, device=DailyAccountMetrics.DEVICE_DESKTOP, day=date(2014, 7, 28))
        self.assertEqual(account_metric.avg_cpc.amount, Decimal('1.81'))
        self.assertEqual(account_metric.avg_cpm.amount, Decimal('1.85'))
        self.assertEqual(account_metric.avg_position, Decimal('1.0'))
        self.assertEqual(account_metric.clicks, 5)
        self.assertEqual(account_metric.content_lost_is_budget, Decimal('23.39'))
        self.assertEqual(account_metric.content_impr_share, Decimal('10.00'))
        self.assertEqual(account_metric.content_lost_is_rank, Decimal('75.41'))
        self.assertEqual(account_metric.click_conversion_rate, Decimal('0.0'))
        self.assertEqual(account_metric.conv_rate, Decimal('0.0'))
        self.assertEqual(account_metric.converted_clicks, 0)
        self.assertEqual(account_metric.converted_clicks, 0)
        self.assertEqual(account_metric.cost.amount, Decimal('9.57'))
        self.assertEqual(account_metric.cost_converted_click.amount, Decimal('0.00'))
        self.assertEqual(account_metric.cost_conv.amount, Decimal('0.00'))
        self.assertEqual(account_metric.cost_est_total_conv.amount, Decimal('0.00'))
        self.assertEqual(account_metric.ctr, Decimal('0.10'))
        self.assertEqual(account_metric.est_cross_device_conv, None)
        self.assertEqual(account_metric.est_total_conv_rate, Decimal('0.00'))
        self.assertEqual(account_metric.est_total_conv_value, Decimal('0.00'))
        self.assertEqual(account_metric.est_total_conv_value_click, Decimal('0.00'))
        self.assertEqual(account_metric.est_total_conv_value_cost, Decimal('0.00'))
        self.assertEqual(account_metric.est_total_conv, 0)
        self.assertEqual(account_metric.impressions, 5183)
        self.assertEqual(account_metric.invalid_click_rate, Decimal('0.00'))
        self.assertEqual(account_metric.invalid_clicks, 0)
        self.assertEqual(account_metric.search_lost_is_budget, Decimal('23.81'))
        self.assertEqual(account_metric.search_exact_match_is, Decimal('76.19'))
        self.assertEqual(account_metric.search_impr_share, Decimal('76.19'))
        self.assertEqual(account_metric.search_lost_is_rank, Decimal('10.00'))

    def test_daily_campaign_metrics_create(self):
        # Run the Campaign report populate
        report_file = _get_report_file('campaign_report.gz')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_campaign(report_file=report_file)
        account.finish_campaign_sync()
        account.finish_sync()

        # Check campaign metrics were created
        campaign_metrics = DailyCampaignMetrics.objects.filter(campaign__account=account)
        self.assertEqual(campaign_metrics.count(), 15)

        # Check a row to ensure fields are correct
        campaign_metric = DailyCampaignMetrics.objects.get(campaign__campaign_id=7679201, day=date(2014, 8, 4))
        self.assertEqual(campaign_metric.avg_cpc.amount, Decimal('0.00'))
        self.assertEqual(campaign_metric.avg_cpm.amount, Decimal('0.00'))
        self.assertEqual(campaign_metric.avg_position, Decimal('0.00'))
        self.assertEqual(campaign_metric.bid_strategy_id, 0)
        self.assertEqual(campaign_metric.bid_strategy_name, '')
        self.assertEqual(campaign_metric.bid_strategy_type, 'cpc')
        self.assertEqual(campaign_metric.clicks, 0)
        self.assertEqual(campaign_metric.content_lost_is_budget, None)
        self.assertEqual(campaign_metric.content_impr_share, None)
        self.assertEqual(campaign_metric.content_lost_is_rank, None)
        self.assertEqual(campaign_metric.click_conversion_rate, Decimal('0.00'))
        self.assertEqual(campaign_metric.conv_rate, Decimal('0.00'))
        self.assertEqual(campaign_metric.converted_clicks, 0)
        self.assertEqual(campaign_metric.converted_clicks, 0)
        self.assertEqual(campaign_metric.cost.amount, Decimal('0.00'))
        self.assertEqual(campaign_metric.cost_converted_click.amount, Decimal('0.00'))
        self.assertEqual(campaign_metric.cost_conv.amount, Decimal('0.00'))
        self.assertEqual(campaign_metric.cost_est_total_conv.amount, Decimal('0.00'))
        self.assertEqual(campaign_metric.ctr, Decimal('0.00'))
        self.assertEqual(campaign_metric.est_cross_device_conv, None)
        self.assertEqual(campaign_metric.est_total_conv_rate, Decimal('0.00'))
        self.assertEqual(campaign_metric.est_total_conv, 0)
        self.assertEqual(campaign_metric.est_total_conv_value, Decimal('0.00'))
        self.assertEqual(campaign_metric.est_total_conv_value_click, Decimal('0.00'))
        self.assertEqual(campaign_metric.est_total_conv_value_cost, Decimal('0.00'))
        self.assertEqual(campaign_metric.impressions, 0)
        self.assertEqual(campaign_metric.invalid_click_rate, Decimal('0.00'))
        self.assertEqual(campaign_metric.invalid_clicks, 0)
        self.assertEqual(campaign_metric.search_lost_is_budget, None)
        self.assertEqual(campaign_metric.search_exact_match_is, None)
        self.assertEqual(campaign_metric.search_impr_share, None)
        self.assertEqual(campaign_metric.search_lost_is_rank, None)

    def test_daily_campaign_metrics_update(self):
        # Run the Campaign report populate
        report_file = _get_report_file('campaign_report.gz')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_campaign(report_file=report_file)
        account.finish_campaign_sync()
        account.finish_sync()

        # Run the Campaign report populate to update rows
        report_file = _get_report_file('campaign_report_update.gz')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_campaign(report_file=report_file)
        account.finish_campaign_sync()
        account.finish_sync()

        campaign_metrics = DailyCampaignMetrics.objects.filter(campaign__account=account)
        self.assertEqual(campaign_metrics.count(), 15)

        # Check a row to ensure fields are correct
        campaign_metric = DailyCampaignMetrics.objects.get(campaign__campaign_id=7679201, day=date(2014, 8, 4))
        self.assertEqual(campaign_metric.avg_cpc.amount, Decimal('1.00'))
        self.assertEqual(campaign_metric.avg_cpm.amount, Decimal('0.00'))
        self.assertEqual(campaign_metric.avg_position, Decimal('0.00'))
        self.assertEqual(campaign_metric.bid_strategy_id, 0)
        self.assertEqual(campaign_metric.bid_strategy_name, '')
        self.assertEqual(campaign_metric.bid_strategy_type, 'cpc')
        self.assertEqual(campaign_metric.clicks, 0)
        self.assertEqual(campaign_metric.content_lost_is_budget, None)
        self.assertEqual(campaign_metric.content_impr_share, None)
        self.assertEqual(campaign_metric.content_lost_is_rank, None)
        self.assertEqual(campaign_metric.click_conversion_rate, Decimal('0.00'))
        self.assertEqual(campaign_metric.conv_rate, Decimal('0.00'))
        self.assertEqual(campaign_metric.converted_clicks, 0)
        self.assertEqual(campaign_metric.converted_clicks, 0)
        self.assertEqual(campaign_metric.cost.amount, Decimal('0.00'))
        self.assertEqual(campaign_metric.cost_converted_click.amount, Decimal('0.00'))
        self.assertEqual(campaign_metric.cost_conv.amount, Decimal('0.00'))
        self.assertEqual(campaign_metric.cost_est_total_conv.amount, Decimal('0.00'))
        self.assertEqual(campaign_metric.ctr, Decimal('0.00'))
        self.assertEqual(campaign_metric.est_cross_device_conv, None)
        self.assertEqual(campaign_metric.est_total_conv_rate, Decimal('0.00'))
        self.assertEqual(campaign_metric.est_total_conv, 0)
        self.assertEqual(campaign_metric.est_total_conv_value, Decimal('0.00'))
        self.assertEqual(campaign_metric.est_total_conv_value_click, Decimal('0.00'))
        self.assertEqual(campaign_metric.est_total_conv_value_cost, Decimal('0.00'))
        self.assertEqual(campaign_metric.impressions, 50)
        self.assertEqual(campaign_metric.invalid_click_rate, Decimal('0.00'))
        self.assertEqual(campaign_metric.invalid_clicks, 0)
        self.assertEqual(campaign_metric.search_lost_is_budget, None)
        self.assertEqual(campaign_metric.search_exact_match_is, None)
        self.assertEqual(campaign_metric.search_impr_share, None)
        self.assertEqual(campaign_metric.search_lost_is_rank, None)

    def test_daily_ad_group_metrics_create(self):
        # Run the Ad Group report populate
        report_file = _get_report_file('adgroup_report.gz')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad_group(report_file=report_file)
        account.finish_ad_group_sync()
        account.finish_sync()

        # Check Ad Group metrics were created
        ad_group_metrics = DailyAdGroupMetrics.objects.filter(ad_group__campaign__account=account)
        self.assertEqual(ad_group_metrics.count(), 50)

        # Check a row to ensure fields are correct
        ad_group_metric = DailyAdGroupMetrics.objects.get(ad_group__ad_group_id=323809001, day=date(2014, 7, 28))

        self.assertEqual(ad_group_metric.max_cpa_converted_clicks, None)
        self.assertEqual(ad_group_metric.value_est_total_conv, Decimal('0.0'))
        self.assertEqual(ad_group_metric.bid_strategy_id, 0)
        self.assertEqual(ad_group_metric.bid_strategy_name, '')
        self.assertEqual(ad_group_metric.bid_strategy_type, DailyAdGroupMetrics.BID_STRATEGY_TYPE_MANUAL_CPC)
        self.assertEqual(ad_group_metric.content_impr_share, None)
        self.assertEqual(ad_group_metric.content_lost_is_rank, None)
        self.assertEqual(ad_group_metric.cost_est_total_conv.amount, Decimal('0'))
        self.assertEqual(ad_group_metric.est_cross_device_conv, None)
        self.assertEqual(ad_group_metric.est_total_conv_rate, Decimal('0.00'))
        self.assertEqual(ad_group_metric.est_total_conv_value, Decimal('0.0'))
        self.assertEqual(ad_group_metric.est_total_conv_value_click, Decimal('0.0'))
        self.assertEqual(ad_group_metric.est_total_conv_value_cost, Decimal('0.0'))
        self.assertEqual(ad_group_metric.est_total_conv, 0)
        self.assertEqual(ad_group_metric.search_exact_match_is, None)
        self.assertEqual(ad_group_metric.search_impr_share, None)
        self.assertEqual(ad_group_metric.search_lost_is_rank, None)
        self.assertEqual(ad_group_metric.value_converted_click, Decimal('0.0'))
        self.assertEqual(ad_group_metric.value_conv, Decimal('0.0'))
        self.assertEqual(ad_group_metric.view_through_conv, None)
        self.assertEqual(ad_group_metric.avg_cpc.amount, Decimal('0'))
        self.assertEqual(ad_group_metric.avg_cpm.amount, Decimal('0'))
        self.assertEqual(ad_group_metric.avg_position, Decimal('0.0'))
        self.assertEqual(ad_group_metric.clicks, 0)
        self.assertEqual(ad_group_metric.click_conversion_rate, Decimal('0.00'))
        self.assertEqual(ad_group_metric.conv_rate, Decimal('0.00'))
        self.assertEqual(ad_group_metric.converted_clicks, 0)
        self.assertEqual(ad_group_metric.converted_clicks, 0)
        self.assertEqual(ad_group_metric.cost.amount, Decimal('0.0'))
        self.assertEqual(ad_group_metric.cost_converted_click.amount, Decimal('0.0'))
        self.assertEqual(ad_group_metric.cost_conv.amount, Decimal('0'))
        self.assertEqual(ad_group_metric.ctr, Decimal('0.00'))
        self.assertEqual(ad_group_metric.impressions, 0)

    def test_daily_ad_group_metrics_update(self):
        # Run the Ad Group report populate
        report_file = _get_report_file('adgroup_report.gz')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad_group(report_file=report_file)
        account.finish_ad_group_sync()
        account.finish_sync()

        # Run the Ad Group report populate update
        report_file = _get_report_file('adgroup_report_update.gz')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad_group(report_file=report_file)
        account.finish_ad_group_sync()
        account.finish_sync()

        # Check Ad Group metrics were created
        ad_group_metrics = DailyAdGroupMetrics.objects.filter(ad_group__campaign__account=account)
        self.assertEqual(ad_group_metrics.count(), 50)

        # Check a row to ensure fields are correct
        ad_group_metric = DailyAdGroupMetrics.objects.get(ad_group__ad_group_id=323809001, day=date(2014, 7, 28))

        self.assertEqual(ad_group_metric.max_cpa_converted_clicks, None)
        self.assertEqual(ad_group_metric.value_est_total_conv, Decimal('0.0'))
        self.assertEqual(ad_group_metric.bid_strategy_id, 0)
        self.assertEqual(ad_group_metric.bid_strategy_name, '')
        self.assertEqual(ad_group_metric.bid_strategy_type, DailyAdGroupMetrics.BID_STRATEGY_TYPE_MANUAL_CPC)
        self.assertEqual(ad_group_metric.content_impr_share, None)
        self.assertEqual(ad_group_metric.content_lost_is_rank, None)
        self.assertEqual(ad_group_metric.cost_est_total_conv.amount, Decimal('0'))
        self.assertEqual(ad_group_metric.est_cross_device_conv, None)
        self.assertEqual(ad_group_metric.est_total_conv_rate, Decimal('0.00'))
        self.assertEqual(ad_group_metric.est_total_conv_value, Decimal('0.0'))
        self.assertEqual(ad_group_metric.est_total_conv_value_click, Decimal('0.0'))
        self.assertEqual(ad_group_metric.est_total_conv_value_cost, Decimal('0.0'))
        self.assertEqual(ad_group_metric.est_total_conv, 0)
        self.assertEqual(ad_group_metric.search_exact_match_is, None)
        self.assertEqual(ad_group_metric.search_impr_share, None)
        self.assertEqual(ad_group_metric.search_lost_is_rank, None)
        self.assertEqual(ad_group_metric.value_converted_click, Decimal('0.0'))
        self.assertEqual(ad_group_metric.value_conv, Decimal('0.0'))
        self.assertEqual(ad_group_metric.view_through_conv, None)
        self.assertEqual(ad_group_metric.avg_cpc.amount, Decimal('0'))
        self.assertEqual(ad_group_metric.avg_cpm.amount, Decimal('0'))
        self.assertEqual(ad_group_metric.avg_position, Decimal('0.0'))
        self.assertEqual(ad_group_metric.clicks, 0)
        self.assertEqual(ad_group_metric.click_conversion_rate, Decimal('0.00'))
        self.assertEqual(ad_group_metric.conv_rate, Decimal('0.00'))
        self.assertEqual(ad_group_metric.converted_clicks, 0)
        self.assertEqual(ad_group_metric.converted_clicks, 0)
        self.assertEqual(ad_group_metric.cost.amount, Decimal('0.0'))
        self.assertEqual(ad_group_metric.cost_converted_click.amount, Decimal('0.0'))
        self.assertEqual(ad_group_metric.cost_conv.amount, Decimal('0'))
        self.assertEqual(ad_group_metric.ctr, Decimal('0.00'))
        self.assertEqual(ad_group_metric.impressions, 100)


    def test_daily_ad_metrics_create(self):
        # Run the Ad report populate
        report_file = _get_report_file('ad_report.gz')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad(report_file=report_file)
        account.finish_ad_sync()
        account.finish_sync()

        # Check Ad Group metrics were created
        ad_metrics = DailyAdMetrics.objects.filter(ad__ad_group__campaign__account=account)
        self.assertEqual(ad_metrics.count(), 44)

        # Check a row to ensure fields are correct
        ad_metric = DailyAdMetrics.objects.get(ad__ad_id=40564055441, day=date(2014, 8, 6))

        self.assertEqual(ad_metric.avg_cpc.amount, Decimal('0.00'))
        self.assertEqual(ad_metric.avg_cpm.amount, Decimal('0.00'))
        self.assertEqual(ad_metric.avg_position, Decimal('1.2'))
        self.assertEqual(ad_metric.clicks, 0)
        self.assertEqual(ad_metric.click_conversion_rate, Decimal('0.00'))
        self.assertEqual(ad_metric.conv_rate, Decimal('0.00'))
        self.assertEqual(ad_metric.converted_clicks, 0)
        self.assertEqual(ad_metric.converted_clicks, 0)
        self.assertEqual(ad_metric.cost.amount, Decimal('0.00'))
        self.assertEqual(ad_metric.cost_converted_click.amount, Decimal('0.00'))
        self.assertEqual(ad_metric.cost_conv.amount, Decimal('0.00'))
        self.assertEqual(ad_metric.ctr, Decimal('0.00'))
        self.assertEqual(ad_metric.impressions, 20)
        self.assertEqual(ad_metric.value_converted_click, Decimal('0.00'))
        self.assertEqual(ad_metric.value_conv, Decimal('0.0'))
        self.assertEqual(ad_metric.view_through_conv, None)

    def test_daily_ad_metrics_update(self):
        # Run the Ad report populate
        report_file = _get_report_file('ad_report.gz')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad(report_file=report_file)
        account.finish_ad_sync()
        account.finish_sync()

        # Run the Ad report update
        report_file = _get_report_file('ad_report_update.gz')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad(report_file=report_file)
        account.finish_ad_sync()
        account.finish_sync()

        # Check Ad Group metrics were created and not duplicated
        ad_metrics = DailyAdMetrics.objects.filter(ad__ad_group__campaign__account=account)
        self.assertEqual(ad_metrics.count(), 44)

        # Check a row to ensure fields are correct
        ad_metric = DailyAdMetrics.objects.get(ad__ad_id=40564055441, day=date(2014, 8, 6))

        self.assertEqual(ad_metric.avg_cpc.amount, Decimal('1.00'))
        self.assertEqual(ad_metric.avg_cpm.amount, Decimal('1.00'))
        self.assertEqual(ad_metric.avg_position, Decimal('1.3'))
        self.assertEqual(ad_metric.clicks, 0)
        self.assertEqual(ad_metric.click_conversion_rate, Decimal('0.00'))
        self.assertEqual(ad_metric.conv_rate, Decimal('0.00'))
        self.assertEqual(ad_metric.converted_clicks, 0)
        self.assertEqual(ad_metric.converted_clicks, 0)
        self.assertEqual(ad_metric.cost.amount, Decimal('0.00'))
        self.assertEqual(ad_metric.cost_converted_click.amount, Decimal('0.00'))
        self.assertEqual(ad_metric.cost_conv.amount, Decimal('0.00'))
        self.assertEqual(ad_metric.ctr, Decimal('0.00'))
        self.assertEqual(ad_metric.impressions, 30)
        self.assertEqual(ad_metric.value_converted_click, Decimal('0.00'))
        self.assertEqual(ad_metric.value_conv, Decimal('0.0'))
        self.assertEqual(ad_metric.view_through_conv, None)

    def test_auto_now(self):
        account = Account.objects.create(account_id=1234)
        #: :type account: Account
        self.assertIsInstance(account.created, datetime)
        self.assertIsInstance(account.updated, datetime)
        created = account.created
        updated = account.updated
        account.account_id = 4321
        account.save()
        self.assertEqual(account.created, created)
        self.assertNotEqual(account.updated, updated)
