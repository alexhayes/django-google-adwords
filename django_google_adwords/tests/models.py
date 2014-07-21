from __future__ import absolute_import
from django.utils import unittest
import os
from django_google_adwords.models import ReportFile, Account, Campaign, AdGroup,\
    DailyAccountMetrics, DailyCampaignMetrics, DailyAdGroupMetrics, Ad,\
    DailyAdMetrics
from django_nose import FastFixtureTestCase
from datetime import datetime, date
from decimal import Decimal

def _get_test_media_file_path(name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'media', name)

def _get_report_file(name):
    report_file = ReportFile.objects.create() #: :type report_file: ReportFile
    report_file.save_path(_get_test_media_file_path(name))
    return report_file

class DjangoGoogleAdwordsTestCase(FastFixtureTestCase):
    fixtures = [
        'django_google_adwords.yaml' 
    ]
    
    def test_account_update_from_initial(self):
        report_file = _get_report_file('account_report.xml')
        
        # Check that initial values are Null
        account = Account.objects.get(pk=1)
        self.assertEqual(account.account, None)
        self.assertEqual(account.currency, None)
        self.assertEqual(account.last_synced, None)
        
        # Run the Account report populate
        account.start_sync()
        account.sync_account(report_file=report_file)
        account.finish_sync()
        
        # Check that the Account fields have been updated
        account = Account.objects.get(pk=1)
        self.assertEqual(account.account, 'example.com')
        self.assertEqual(account.currency, 'AUD')
        self.assertIsInstance(account.last_synced, datetime)
    
    def test_campaign_create(self):
        report_file = _get_report_file('campaign_report.xml')
        
        # Run the Campaign report populate
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_campaign(report_file=report_file)
        account.finish_sync()
        
        # Check that the Campaigns have been populated
        account = Account.objects.get(pk=1)
        campaigns = account.campaigns.all()
        self.assertEqual(campaigns.count(), 13)
        
        # Check campaign attributes populated correctly
        c1 = Campaign.objects.get(campaign_id=10000006)
        self.assertEqual(c1.account, account)
        self.assertEqual(c1.campaign, 'Campaign #5')
        self.assertEqual(c1.campaign_state, Campaign.STATE_PAUSED)
        self.assertEqual(c1.budget.amount, Decimal('33.0'))
    
        c2 = Campaign.objects.get(campaign_id=10000005)
        self.assertEqual(c2.account, account)
        self.assertEqual(c2.campaign, 'Ad Group #8')
        self.assertEqual(c2.campaign_state, Campaign.STATE_PAUSED)
        self.assertEqual(c2.budget.amount, Decimal('12.0'))
    
        c3 = Campaign.objects.get(campaign_id=10000004)
        self.assertEqual(c3.account, account)
        self.assertEqual(c3.campaign, 'Campaign #3')
        self.assertEqual(c3.campaign_state, Campaign.STATE_PAUSED)
        self.assertEqual(c3.budget.amount, Decimal('10.0'))
        
        c4 = Campaign.objects.get(campaign_id=10000003)
        self.assertEqual(c4.account, account)
        self.assertEqual(c4.campaign, 'Campaign #11')
        self.assertEqual(c4.campaign_state, Campaign.STATE_ACTIVE)
        self.assertEqual(c4.budget.amount, Decimal('100.0'))
        
        c5 = Campaign.objects.get(campaign_id=10000002)
        self.assertEqual(c5.account, account)
        self.assertEqual(c5.campaign, 'Campaign #13')
        self.assertEqual(c5.campaign_state, Campaign.STATE_PAUSED)
        self.assertEqual(c5.budget.amount, Decimal('17.5'))
        
        c6 = Campaign.objects.get(campaign_id=10000001)
        self.assertEqual(c6.account, account)
        self.assertEqual(c6.campaign, 'Campaign #10')
        self.assertEqual(c6.campaign_state, Campaign.STATE_PAUSED)
        self.assertEqual(c6.budget.amount, Decimal('30.0'))
        
        c7 = Campaign.objects.get(campaign_id=100000007)
        self.assertEqual(c7.account, account)
        self.assertEqual(c7.campaign, 'Campaign #12')
        self.assertEqual(c7.campaign_state, Campaign.STATE_PAUSED)
        self.assertEqual(c7.budget.amount, Decimal('5.0'))
        
        c8 = Campaign.objects.get(campaign_id=100000006)
        self.assertEqual(c8.account, account)
        self.assertEqual(c8.campaign, 'Campaign #9')
        self.assertEqual(c8.campaign_state, Campaign.STATE_PAUSED)
        self.assertEqual(c8.budget.amount, Decimal('8.0'))
        
        c9 = Campaign.objects.get(campaign_id=100000005)
        self.assertEqual(c9.account, account)
        self.assertEqual(c9.campaign, 'Campaign #4')
        self.assertEqual(c9.campaign_state, Campaign.STATE_PAUSED)
        self.assertEqual(c9.budget.amount, Decimal('20.0'))
        
        c10 = Campaign.objects.get(campaign_id=100000004)
        self.assertEqual(c10.account, account)
        self.assertEqual(c10.campaign, 'Campaign #1')
        self.assertEqual(c10.campaign_state, Campaign.STATE_PAUSED)
        self.assertEqual(c10.budget.amount, Decimal('20.0'))
        
        c11 = Campaign.objects.get(campaign_id=100000003)
        self.assertEqual(c11.account, account)
        self.assertEqual(c11.campaign, 'Campaign #8')
        self.assertEqual(c11.campaign_state, Campaign.STATE_ACTIVE)
        self.assertEqual(c11.budget.amount, Decimal('58.0'))
        
        c12 = Campaign.objects.get(campaign_id=100000002)
        self.assertEqual(c12.account, account)
        self.assertEqual(c12.campaign, 'Campaign #7')
        self.assertEqual(c12.campaign_state, Campaign.STATE_ACTIVE)
        self.assertEqual(c12.budget.amount, Decimal('105.0'))
        
        c13 = Campaign.objects.get(campaign_id=100000001)
        self.assertEqual(c13.account, account)
        self.assertEqual(c13.campaign, 'Campaign #2')
        self.assertEqual(c13.campaign_state, Campaign.STATE_DELETED)
        self.assertEqual(c13.budget.amount, Decimal('10.0'))
        
    def test_campaign_update(self):
        # Run the Campaign report populate
        report_file = _get_report_file('campaign_report.xml')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_campaign(report_file=report_file)
        account.finish_sync()
        
        # Check campaign attributes populated correctly
        c = Campaign.objects.get(campaign_id=10000006)
        self.assertEqual(c.campaign, 'Campaign #5')
        self.assertEqual(c.campaign_state, Campaign.STATE_PAUSED)
        self.assertEqual(c.budget.amount, Decimal('33.0'))
    
        # Run the updated Campaign report populate
        report_file = _get_report_file('campaign_report_update.xml')
        account.start_sync()
        account.sync_campaign(report_file=report_file)
        account.finish_sync()
        
        # Check campaign attributes updated correctly
        uc = Campaign.objects.get(campaign_id=10000006)
        self.assertEqual(uc.campaign, 'Campaign #6')
        self.assertEqual(uc.campaign_state, Campaign.STATE_ACTIVE)
        self.assertEqual(uc.budget.amount, Decimal('44.0'))
    
    def test_ad_group_create(self):
        report_file = _get_report_file('ad_group_report.xml')
          
        # Run the Ad Group report populate
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad_group(report_file=report_file)
        account.finish_sync()
          
        # Check that the Ad Groups have been populated
        account = Account.objects.get(pk=1)
        ad_groups = AdGroup.objects.filter(campaign__account=account)
        self.assertEqual(ad_groups.count(), 3)
          
        # Check Ad Group attributes populated correctly
        ad_group = AdGroup.objects.get(ad_group_id=1000000006)
        self.assertEqual(ad_group.campaign.campaign_id, 10000006)
        self.assertEqual(ad_group.ad_group, 'Ad Group #1')
        self.assertEqual(ad_group.ad_group_state, AdGroup.STATE_DELETED)
    
    def test_ad_group_update(self):
        # Run the Ad Group report populate
        report_file = _get_report_file('ad_group_report.xml')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad_group(report_file=report_file)
        account.finish_sync()
          
        # Run the Ad Group report populate to update rows
        report_file = _get_report_file('ad_group_report_update.xml')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad_group(report_file=report_file)
        account.finish_sync()
        
        # Check Ad Group attributes updated correctly
        ad_group = AdGroup.objects.get(ad_group_id=1000000006)
        self.assertEqual(ad_group.campaign.campaign_id, 10000006)
        self.assertEqual(ad_group.ad_group, 'Ad Group #2')
        self.assertEqual(ad_group.ad_group_state, AdGroup.STATE_ENABLED)
    
    def test_ad_create(self):
        # Run the Ad report populate
        report_file = _get_report_file('ad_report.xml')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad(report_file=report_file)
        account.finish_sync()
        
        # Check that the Ads have been populated
        account = Account.objects.get(pk=1)
        ads = Ad.objects.filter(ad_group__campaign__account=account)
        self.assertEqual(ads.count(), 8)
          
        # Check Ad attributes populated correctly
        ad = Ad.objects.get(ad_id=10000000003)
        self.assertEqual(ad.ad_state, Ad.STATE_ENABLED)
        self.assertEqual(ad.ad_type, Ad.TYPE_TEXT_AD)
        self.assertEqual(ad.destination_url, 'http://www.example.com/location-1/')
        self.assertEqual(ad.display_url, 'example.com/location-4/sub-1/')
        self.assertEqual(ad.ad, 'Ad Group #7')
        self.assertEqual(ad.description_line1, 'Lorem ipsum 2')
        self.assertEqual(ad.description_line2, 'Bacon ipsum 2')
    
    def test_ad_update(self):
        # Run the Ad report populate
        report_file = _get_report_file('ad_report.xml')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad(report_file=report_file)
        account.finish_sync()
        
        # Run the Ad report populate update
        report_file = _get_report_file('ad_report_update.xml')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad(report_file=report_file)
        account.finish_sync()
        
        # Check that the Ads have been updated and there are still only 9
        account = Account.objects.get(pk=1)
        ads = Ad.objects.filter(ad_group__campaign__account=account)
        self.assertEqual(ads.count(), 8)
          
        # Check Ad attributes updated correctly
        ad = Ad.objects.get(ad_id=10000000003)
        self.assertEqual(ad.ad_state, Ad.STATE_ENABLED)
        self.assertEqual(ad.ad_type, Ad.TYPE_TEXT_AD)
        self.assertEqual(ad.destination_url, 'http://www.example.com/location-2/')
        self.assertEqual(ad.display_url, 'example.com/location-4/sub-1/')
        self.assertEqual(ad.ad, 'Ad Group #7')
        self.assertEqual(ad.description_line1, 'Lorem ipsum 3')
        self.assertEqual(ad.description_line2, 'Bacon ipsum 3')
        
    def test_daily_account_metrics_create(self):
        report_file = _get_report_file('account_report.xml')

        # Run the Account report populate
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_account(report_file=report_file)
        account.finish_sync()
        
        # Check that the Daily Account Metrics have been populated
        account_metrics = DailyAccountMetrics.objects.filter(account=account)
        self.assertEqual(account_metrics.count(), 3)
        
        # Check the fields of one of them
        account_metric = DailyAccountMetrics.objects.get(account=account, device=DailyAccountMetrics.DEVICE_DESKTOP, day=date(2014,7,10))
        self.assertEqual(account_metric.avg_cpc.amount, Decimal('3.88'))
        self.assertEqual(account_metric.avg_cpm.amount, Decimal('48.44'))
        self.assertEqual(account_metric.avg_position, Decimal('1.6'))
        self.assertEqual(account_metric.clicks, 6)
        self.assertEqual(account_metric.content_lost_is_budget, None)
        self.assertEqual(account_metric.content_impr_share, Decimal('10.00'))
        self.assertEqual(account_metric.content_lost_is_rank, None)
        self.assertEqual(account_metric.click_conversion_rate, Decimal('33.33'))
        self.assertEqual(account_metric.conv_rate, Decimal('33.33'))
        self.assertEqual(account_metric.converted_clicks, 2)
        self.assertEqual(account_metric.conversions, 2)
        self.assertEqual(account_metric.cost.amount, Decimal('23.30'))
        self.assertEqual(account_metric.cost_converted_click.amount, Decimal('11.65'))
        self.assertEqual(account_metric.cost_conv.amount, Decimal('11.65'))
        self.assertEqual(account_metric.cost_est_total_conv.amount, Decimal('11.65'))
        self.assertEqual(account_metric.ctr, Decimal('1.25'))
        self.assertEqual(account_metric.est_cross_device_conv, None)
        self.assertEqual(account_metric.est_total_conv_rate, Decimal('33.33'))
        self.assertEqual(account_metric.est_total_conv_value, Decimal('2887.52'))
        self.assertEqual(account_metric.est_total_conv_value_click, Decimal('0.00'))
        self.assertEqual(account_metric.est_total_conv_value_cost, Decimal('0.00'))
        self.assertEqual(account_metric.est_total_conv, 2)
        self.assertEqual(account_metric.impressions, 481)
        self.assertEqual(account_metric.invalid_click_rate, Decimal('0.00'))
        self.assertEqual(account_metric.invalid_clicks, 0)
        self.assertEqual(account_metric.search_lost_is_budget, None)
        self.assertEqual(account_metric.search_exact_match_is, None)
        self.assertEqual(account_metric.search_impr_share, Decimal('10.00'))
        self.assertEqual(account_metric.search_lost_is_rank, None)
        
    def test_daily_account_metrics_update(self):
        # Run the Account report populate
        report_file = _get_report_file('account_report.xml')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_account(report_file=report_file)
        account.finish_sync()

        # Run the Account report populate with data to update
        report_file = _get_report_file('account_report_update.xml')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_account(report_file=report_file)
        account.finish_sync()
        
        # Check that the Daily Account Metrics have been populated
        account_metrics = DailyAccountMetrics.objects.filter(account=account)
        self.assertEqual(account_metrics.count(), 3)
        
        # Check the fields of one of them to ensure the update occurred correctly
        account_metric = DailyAccountMetrics.objects.get(account=account, device=DailyAccountMetrics.DEVICE_DESKTOP, day=date(2014,7,10))
        self.assertEqual(account_metric.avg_cpc.amount, Decimal('3.99'))
        self.assertEqual(account_metric.avg_cpm.amount, Decimal('48.44'))
        self.assertEqual(account_metric.avg_position, Decimal('1.60'))
        self.assertEqual(account_metric.clicks, 10)
        self.assertEqual(account_metric.content_lost_is_budget, Decimal('10.23'))
        self.assertEqual(account_metric.content_impr_share, None)
        self.assertEqual(account_metric.content_lost_is_rank, None)
        self.assertEqual(account_metric.click_conversion_rate, Decimal('33.33'))
        self.assertEqual(account_metric.conv_rate, Decimal('33.33'))
        self.assertEqual(account_metric.converted_clicks, 2)
        self.assertEqual(account_metric.conversions, 2)
        self.assertEqual(account_metric.cost.amount, Decimal('23.30'))
        self.assertEqual(account_metric.cost_converted_click.amount, Decimal('11.65'))
        self.assertEqual(account_metric.cost_conv.amount, Decimal('11.65'))
        self.assertEqual(account_metric.cost_est_total_conv.amount, Decimal('11.65'))
        self.assertEqual(account_metric.ctr, Decimal('1.25'))
        self.assertEqual(account_metric.est_cross_device_conv, None)
        self.assertEqual(account_metric.est_total_conv_rate, Decimal('33.33'))
        self.assertEqual(account_metric.est_total_conv_value, Decimal('1.10'))
        self.assertEqual(account_metric.est_total_conv_value_click, Decimal('0.00'))
        self.assertEqual(account_metric.est_total_conv_value_cost, Decimal('0.00'))
        self.assertEqual(account_metric.est_total_conv, 2)
        self.assertEqual(account_metric.impressions, 481)
        self.assertEqual(account_metric.invalid_click_rate, Decimal('0.00'))
        self.assertEqual(account_metric.invalid_clicks, 7)
        self.assertEqual(account_metric.search_lost_is_budget, None)
        self.assertEqual(account_metric.search_exact_match_is, None)
        self.assertEqual(account_metric.search_impr_share, None)
        self.assertEqual(account_metric.search_lost_is_rank, None)
    
    def test_daily_campaign_metrics_create(self):
        # Run the Campaign report populate
        report_file = _get_report_file('campaign_report.xml')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_campaign(report_file=report_file)
        account.finish_sync()
        
        # Check campaign metrics were created
        campaign_metrics = DailyCampaignMetrics.objects.filter(campaign__account=account)
        self.assertEqual(campaign_metrics.count(), 39)
        
        # Check a row to ensure fields are correct        
        campaign_metric = DailyCampaignMetrics.objects.get(campaign__campaign_id=100000002, device=DailyCampaignMetrics.DEVICE_HIGH_END_MOBILE, day=date(2014,7,10))
        self.assertEqual(campaign_metric.avg_cpc.amount, Decimal('3.37'))
        self.assertEqual(campaign_metric.avg_cpm.amount, Decimal('201.04'))
        self.assertEqual(campaign_metric.avg_position, Decimal('1.30'))
        self.assertEqual(campaign_metric.bid_strategy_id, 0)
        self.assertEqual(campaign_metric.bid_strategy_name, '')
        self.assertEqual(campaign_metric.bid_strategy_type, 'cpc')
        self.assertEqual(campaign_metric.clicks, 4)
        self.assertEqual(campaign_metric.content_lost_is_budget, None)
        self.assertEqual(campaign_metric.content_impr_share, None)
        self.assertEqual(campaign_metric.content_lost_is_rank, None)
        self.assertEqual(campaign_metric.click_conversion_rate, Decimal('0.00'))
        self.assertEqual(campaign_metric.conv_rate, Decimal('0.00'))
        self.assertEqual(campaign_metric.converted_clicks, 0)
        self.assertEqual(campaign_metric.conversions, 0)
        self.assertEqual(campaign_metric.cost.amount, Decimal('13.47'))
        self.assertEqual(campaign_metric.cost_converted_click, Decimal('0.00'))
        self.assertEqual(campaign_metric.cost_conv, Decimal('0.00'))
        self.assertEqual(campaign_metric.cost_est_total_conv, Decimal('0.00'))
        self.assertEqual(campaign_metric.ctr, Decimal('5.97'))
        self.assertEqual(campaign_metric.est_cross_device_conv, None)
        self.assertEqual(campaign_metric.est_total_conv_rate, Decimal('0.00'))
        self.assertEqual(campaign_metric.est_total_conv, 0)
        self.assertEqual(campaign_metric.est_total_conv_value, Decimal('0.00'))
        self.assertEqual(campaign_metric.est_total_conv_value_click, Decimal('0.00'))
        self.assertEqual(campaign_metric.est_total_conv_value_cost, Decimal('0.00'))
        self.assertEqual(campaign_metric.impressions, 67)
        self.assertEqual(campaign_metric.invalid_click_rate, Decimal('0.00'))
        self.assertEqual(campaign_metric.invalid_clicks, 0)
        self.assertEqual(campaign_metric.search_lost_is_budget, None)
        self.assertEqual(campaign_metric.search_exact_match_is, None)
        self.assertEqual(campaign_metric.search_impr_share, None)
        self.assertEqual(campaign_metric.search_lost_is_rank, None)
    
    def test_daily_campaign_metrics_update(self):
        # Run the Campaign report populate
        report_file = _get_report_file('campaign_report.xml')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_campaign(report_file=report_file)
        account.finish_sync()
        
        # Run the Campaign report populate to update rows
        report_file = _get_report_file('campaign_report_update.xml')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_campaign(report_file=report_file)
        account.finish_sync()
        
        # Check campaign metrics were created
        campaign_metrics = DailyCampaignMetrics.objects.filter(campaign__account=account)
        self.assertEqual(campaign_metrics.count(), 39)
        
        # Check a row to ensure fields are correct        
        campaign_metric = DailyCampaignMetrics.objects.get(campaign__campaign_id=100000002, device=DailyCampaignMetrics.DEVICE_HIGH_END_MOBILE, day=date(2014,7,10))
        self.assertEqual(campaign_metric.avg_cpc.amount, Decimal('3.37'))
        self.assertEqual(campaign_metric.avg_cpm.amount, Decimal('201.04'))
        self.assertEqual(campaign_metric.avg_position, Decimal('1.30'))
        self.assertEqual(campaign_metric.bid_strategy_id, 0)
        self.assertEqual(campaign_metric.bid_strategy_name, '')
        self.assertEqual(campaign_metric.bid_strategy_type, 'cpc')
        self.assertEqual(campaign_metric.clicks, 4)
        self.assertEqual(campaign_metric.content_lost_is_budget, None)
        self.assertEqual(campaign_metric.content_impr_share, None)
        self.assertEqual(campaign_metric.content_lost_is_rank, None)
        self.assertEqual(campaign_metric.click_conversion_rate, Decimal('0.00'))
        self.assertEqual(campaign_metric.conv_rate, Decimal('0.00'))
        self.assertEqual(campaign_metric.converted_clicks, 0)
        self.assertEqual(campaign_metric.conversions, 0)
        self.assertEqual(campaign_metric.cost.amount, Decimal('13.48'))
        self.assertEqual(campaign_metric.cost_converted_click, Decimal('0.00'))
        self.assertEqual(campaign_metric.cost_conv, Decimal('0.00'))
        self.assertEqual(campaign_metric.cost_est_total_conv, Decimal('0.00'))
        self.assertEqual(campaign_metric.ctr, Decimal('5.97'))
        self.assertEqual(campaign_metric.est_cross_device_conv, None)
        self.assertEqual(campaign_metric.est_total_conv_rate, Decimal('1.00'))
        self.assertEqual(campaign_metric.est_total_conv, 0)
        self.assertEqual(campaign_metric.est_total_conv_value, Decimal('0.00'))
        self.assertEqual(campaign_metric.est_total_conv_value_click, Decimal('0.00'))
        self.assertEqual(campaign_metric.est_total_conv_value_cost, Decimal('0.00'))
        self.assertEqual(campaign_metric.impressions, 67)
        self.assertEqual(campaign_metric.invalid_click_rate, Decimal('0.00'))
        self.assertEqual(campaign_metric.invalid_clicks, 7)
        self.assertEqual(campaign_metric.search_lost_is_budget, None)
        self.assertEqual(campaign_metric.search_exact_match_is, None)
        self.assertEqual(campaign_metric.search_impr_share, None)
        self.assertEqual(campaign_metric.search_lost_is_rank, None)
        
    def test_daily_ad_group_metrics_create(self):
        # Run the Ad Group report populate
        report_file = _get_report_file('ad_group_report.xml')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad_group(report_file=report_file)
        account.finish_sync()
        
        # Check Ad Group metrics were created
        ad_group_metrics = DailyAdGroupMetrics.objects.filter(ad_group__campaign__account=account)
        self.assertEqual(ad_group_metrics.count(), 9)
        
        # Check a row to ensure fields are correct
        ad_group_metric = DailyAdGroupMetrics.objects.get(ad_group__ad_group_id=1000000006, device=DailyAdGroupMetrics.DEVICE_DESKTOP, day=date(2014,7,13))
        
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
        self.assertEqual(ad_group_metric.view_through_conv, Decimal('0'))
        self.assertEqual(ad_group_metric.avg_cpc, Decimal('0'))
        self.assertEqual(ad_group_metric.avg_cpm, Decimal('0'))
        self.assertEqual(ad_group_metric.avg_position, Decimal('0.0'))
        self.assertEqual(ad_group_metric.clicks, 0)
        self.assertEqual(ad_group_metric.click_conversion_rate, Decimal('0.00'))
        self.assertEqual(ad_group_metric.conv_rate, Decimal('0.00'))
        self.assertEqual(ad_group_metric.converted_clicks, 0)
        self.assertEqual(ad_group_metric.conversions, 0)
        self.assertEqual(ad_group_metric.cost.amount, Decimal('0.0'))
        self.assertEqual(ad_group_metric.cost_converted_click, Decimal('0.0'))
        self.assertEqual(ad_group_metric.cost_conv, Decimal('0'))
        self.assertEqual(ad_group_metric.ctr, Decimal('0.00'))
        self.assertEqual(ad_group_metric.device, DailyAdGroupMetrics.DEVICE_DESKTOP)
        self.assertEqual(ad_group_metric.impressions, 0)
    
    def test_daily_ad_group_metrics_update(self):
        # Run the Ad Group report populate
        report_file = _get_report_file('ad_group_report.xml')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad_group(report_file=report_file)
        account.finish_sync()
        
        # Run the Ad Group report populate update
        report_file = _get_report_file('ad_group_report_update.xml')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad_group(report_file=report_file)
        account.finish_sync()
        
        # Check Ad Group metrics were created
        ad_group_metrics = DailyAdGroupMetrics.objects.filter(ad_group__campaign__account=account)
        self.assertEqual(ad_group_metrics.count(), 9)
        
        # Check a row to ensure fields are correct
        ad_group_metric = DailyAdGroupMetrics.objects.get(ad_group__ad_group_id=1000000006, device=DailyAdGroupMetrics.DEVICE_DESKTOP, day=date(2014,7,13))
        
        self.assertEqual(ad_group_metric.max_cpa_converted_clicks, None)
        self.assertEqual(ad_group_metric.value_est_total_conv, Decimal('0.0'))
        self.assertEqual(ad_group_metric.bid_strategy_id, 0)
        self.assertEqual(ad_group_metric.bid_strategy_name, '')
        self.assertEqual(ad_group_metric.bid_strategy_type, DailyAdGroupMetrics.BID_STRATEGY_TYPE_MANUAL_CPC)
        self.assertEqual(ad_group_metric.content_impr_share, None)
        self.assertEqual(ad_group_metric.content_lost_is_rank, None)
        self.assertEqual(ad_group_metric.cost_est_total_conv.amount, Decimal('0'))
        self.assertEqual(ad_group_metric.est_cross_device_conv, None)
        self.assertEqual(ad_group_metric.est_total_conv_rate, Decimal('2.22'))
        self.assertEqual(ad_group_metric.est_total_conv_value, Decimal('0.0'))
        self.assertEqual(ad_group_metric.est_total_conv_value_click, Decimal('0.0'))
        self.assertEqual(ad_group_metric.est_total_conv_value_cost, Decimal('0.0'))
        self.assertEqual(ad_group_metric.est_total_conv, 0)
        self.assertEqual(ad_group_metric.search_exact_match_is, None)
        self.assertEqual(ad_group_metric.search_impr_share, None)
        self.assertEqual(ad_group_metric.search_lost_is_rank, None)
        self.assertEqual(ad_group_metric.value_converted_click, Decimal('0.0'))
        self.assertEqual(ad_group_metric.value_conv, Decimal('0.0'))
        self.assertEqual(ad_group_metric.view_through_conv, Decimal('0'))
        self.assertEqual(ad_group_metric.avg_cpc.amount, Decimal('1.00'))
        self.assertEqual(ad_group_metric.avg_cpm, Decimal('0'))
        self.assertEqual(ad_group_metric.avg_position, Decimal('0.0'))
        self.assertEqual(ad_group_metric.clicks, 0)
        self.assertEqual(ad_group_metric.click_conversion_rate, Decimal('0.00'))
        self.assertEqual(ad_group_metric.conv_rate, Decimal('0.00'))
        self.assertEqual(ad_group_metric.converted_clicks, 0)
        self.assertEqual(ad_group_metric.conversions, 20)
        self.assertEqual(ad_group_metric.cost.amount, Decimal('20.43'))
        self.assertEqual(ad_group_metric.cost_converted_click, Decimal('0.0'))
        self.assertEqual(ad_group_metric.cost_conv, Decimal('0'))
        self.assertEqual(ad_group_metric.ctr, Decimal('0.00'))
        self.assertEqual(ad_group_metric.device, DailyAdGroupMetrics.DEVICE_DESKTOP)
        self.assertEqual(ad_group_metric.impressions, 20)
    
    def test_daily_ad_metrics_create(self):
        # Run the Ad report populate
        report_file = _get_report_file('ad_report.xml')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad(report_file=report_file)
        account.finish_sync()
        
        # Check Ad Group metrics were created
        ad_metrics = DailyAdMetrics.objects.filter(ad__ad_group__campaign__account=account)
        self.assertEqual(ad_metrics.count(), 10)
        
        # Check a row to ensure fields are correct
        ad_metric = DailyAdMetrics.objects.get(ad__ad_id=10000000003, device=DailyAdGroupMetrics.DEVICE_DESKTOP, day=date(2014,7,13))
        
        self.assertEqual(ad_metric.avg_cpc.amount, Decimal('0.00'))
        self.assertEqual(ad_metric.avg_cpm.amount, Decimal('0.00'))
        self.assertEqual(ad_metric.avg_position, Decimal('3.4'))
        self.assertEqual(ad_metric.clicks, 0)
        self.assertEqual(ad_metric.click_conversion_rate, Decimal('0.00'))
        self.assertEqual(ad_metric.conv_rate, Decimal('0.00'))
        self.assertEqual(ad_metric.converted_clicks, 0)
        self.assertEqual(ad_metric.conversions, 0)
        self.assertEqual(ad_metric.cost.amount, Decimal('0.00'))
        self.assertEqual(ad_metric.cost_converted_click, Decimal('0.00'))
        self.assertEqual(ad_metric.cost_conv, Decimal('0.00'))
        self.assertEqual(ad_metric.ctr, Decimal('0.00'))
        self.assertEqual(ad_metric.device, DailyAdMetrics.DEVICE_DESKTOP)
        self.assertEqual(ad_metric.impressions, 13)
        self.assertEqual(ad_metric.value_converted_click, Decimal('0.00'))
        self.assertEqual(ad_metric.value_conv, Decimal('0.0'))
        self.assertEqual(ad_metric.view_through_conv, 0)

    def test_daily_ad_metrics_update(self):
        # Run the Ad report populate
        report_file = _get_report_file('ad_report.xml')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad(report_file=report_file)
        account.finish_sync()
        
        # Run the Ad report update
        report_file = _get_report_file('ad_report_update.xml')
        account = Account.objects.get(pk=1)
        account.start_sync()
        account.sync_ad(report_file=report_file)
        account.finish_sync()
        
        # Check Ad Group metrics were created and not duplicated
        ad_metrics = DailyAdMetrics.objects.filter(ad__ad_group__campaign__account=account)
        self.assertEqual(ad_metrics.count(), 10)
        
        # Check a row to ensure fields are correct
        ad_metric = DailyAdMetrics.objects.get(ad__ad_id=10000000003, device=DailyAdGroupMetrics.DEVICE_DESKTOP, day=date(2014,7,13))
        
        self.assertEqual(ad_metric.avg_cpc.amount, Decimal('0.00'))
        self.assertEqual(ad_metric.avg_cpm.amount, Decimal('0.00'))
        self.assertEqual(ad_metric.avg_position, Decimal('3.4'))
        self.assertEqual(ad_metric.clicks, 10)
        self.assertEqual(ad_metric.click_conversion_rate, Decimal('0.00'))
        self.assertEqual(ad_metric.conv_rate, Decimal('0.00'))
        self.assertEqual(ad_metric.converted_clicks, 10)
        self.assertEqual(ad_metric.conversions, 10)
        self.assertEqual(ad_metric.cost.amount, Decimal('10.55'))
        self.assertEqual(ad_metric.cost_converted_click, Decimal('0.00'))
        self.assertEqual(ad_metric.cost_conv, Decimal('0.00'))
        self.assertEqual(ad_metric.ctr, Decimal('0.00'))
        self.assertEqual(ad_metric.device, DailyAdMetrics.DEVICE_DESKTOP)
        self.assertEqual(ad_metric.impressions, 13)
        self.assertEqual(ad_metric.value_converted_click, Decimal('0.00'))
        self.assertEqual(ad_metric.value_conv, Decimal('0.0'))
        self.assertEqual(ad_metric.view_through_conv, 0)
    
            