from googleads.adwords import AdWordsClient
from googleads.oauth2 import GoogleRefreshTokenClient
from googleads.errors import GoogleAdsError
from django.conf import settings
from time import sleep
import logging

logger = logging.getLogger(__name__)


def adwords_service(client_customer_id=None):
    """
    Get an instance of GoogleRefreshTokenClient with configuration as per defined settings
    and use that to create an instance of AdwordsClient.
    """
    if not client_customer_id:
        client_customer_id = settings.GOOGLEADWORDS_CLIENT_CUSTOMER_ID

    oauth2_client = GoogleRefreshTokenClient(
        client_id=settings.GOOGLEADWORDS_CLIENT_ID,
        client_secret=settings.GOOGLEADWORDS_CLIENT_SECRET,
        refresh_token=settings.GOOGLEADWORDS_REFRESH_TOKEN
    )

    return AdWordsClient(
        developer_token=settings.GOOGLEADWORDS_DEVELOPER_TOKEN,
        oauth2_client=oauth2_client,
        user_agent=settings.GOOGLEADWORDS_USER_AGENT,
        client_customer_id=client_customer_id
    )


def paged_request(service, selector={}, number_results=100, start_index=0, retry=True, number_pages=False):
    """
    Yields paged data as retrieved from the Adwords API.

    Alert Service Example:

    selector = {
        'query': {
            'clientSpec': 'ALL',
            'filterSpec': 'ALL',
            'types': ['ACCOUNT_BUDGET_BURN_RATE', 'ACCOUNT_BUDGET_ENDING',
                      'ACCOUNT_ON_TARGET', 'CAMPAIGN_ENDED', 'CAMPAIGN_ENDING',
                      'CREDIT_CARD_EXPIRING', 'DECLINED_PAYMENT',
                      'KEYWORD_BELOW_MIN_CPC', 'MANAGER_LINK_PENDING',
                      'MISSING_BANK_REFERENCE_NUMBER', 'PAYMENT_NOT_ENTERED',
                      'TV_ACCOUNT_BUDGET_ENDING', 'TV_ACCOUNT_ON_TARGET',
                      'TV_ZERO_DAILY_SPENDING_LIMIT', 'USER_INVITE_ACCEPTED',
                      'USER_INVITE_PENDING', 'ZERO_DAILY_SPENDING_LIMIT'],
            'severities': ['GREEN', 'YELLOW', 'RED'],
            'triggerTimeSpec': 'ALL_TIME'
        }
    }
    for (data, selector) in paged_request(service='AlertService', number_results=selector=selector):
        print data

    Targeting Ideas Service Example:

    {{{
    selector = {
        'searchParameters': [
            {
                'xsi_type': 'RelatedToQuerySearchParameter',
                'queries': ['seo', 'adwords', 'adwords seo']
            },
            {
                'xsi_type': 'LanguageSearchParameter',
                'languages': [{'id': '1000'}]
            },
            {
                'xsi_type': 'LocationSearchParameter',
                'locations': [{'id': '2036'}]
            },
        ],
        'ideaType': 'KEYWORD',
        'requestType': 'IDEAS',
        'requestedAttributeTypes': ['KEYWORD_TEXT', 'SEARCH_VOLUME'],
    }

    for (data, selector) in paged_request('TargetingIdeaService', selector):
        print data

    }}}

    @param service: A string representing the client service class, ie.. GetTargetingIdeaService
    @param selector: A dict of values used to specify the request to the API.
    @param number_results: Results per page.
    @param start_index: Offset to start results at.
    @yield data, selector
    """
    client = adwords_service()
    service = client.GetService(service, settings.GOOGLEADWORDS_CLIENT_VERSION)

    if 'paging' not in selector:
        selector['paging'] = {}
    if start_index is not None:
        selector['paging']['startIndex'] = str(start_index)
    if number_results is not None:
        selector['paging']['numberResults'] = str(number_results)

    more_pages = True
    page_number = 1

    while more_pages:
        try:
            response = service.get(selector)
            yield response.entries, selector

            # Now, get the next set of results
            start_index += number_results
            selector['paging']['startIndex'] = str(start_index)
            if number_pages:
                if number_pages >= page_number:
                    more_pages = False
            else:
                more_pages = start_index < int(response.totalNumEntries)

            page_number += 1

        except GoogleAdsError as e:
            if not retry or not hasattr(e, 'fault') or not hasattr(e.fault, 'detail') or not hasattr(e.fault.detail, 'ApiExceptionFault') or not hasattr(e.fault.detail.ApiExceptionFault, 'errors'):
                raise
            retryAfterSeconds = sum([int(fault.retryAfterSeconds) for fault in e.fault.detail.ApiExceptionFault.errors if getattr(fault, 'ApiError.Type') == 'RateExceededError'])
            if retryAfterSeconds > 0:
                # We've hit a RateExceededError, sleep for some period of time
                logger.info("Sleeping due to 'RateExceededError' for '%s' seconds." % retryAfterSeconds)
                sleep(retryAfterSeconds)
            else:
                # We haven't hit an error we care about, raise it.
                raise
