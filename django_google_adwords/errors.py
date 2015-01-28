from django.core.exceptions import ValidationError as _ValidationError


class RateExceededError(Exception):

    def __init__(self, retry_after_seconds):
        self.retry_after_seconds = retry_after_seconds
        Exception.__init__(self, retry_after_seconds)


class InterceptedGoogleAdsError(Exception):

    def __init__(self, google_ads_error, account_id):
        self.google_ads_error = google_ads_error
        self.account_id = account_id
        Exception.__init__(self, google_ads_error, account_id)


class ValidationError(_ValidationError):

    def __init__(self, field_name, message):
        self.field_name = field_name
        print 'Field error', self.field_name, message
        _ValidationError.__init__(self, message)

    def __str__(self):
        if hasattr(self, 'error_dict'):
            return repr(self.message_dict)
        return '%s for field %s' % (repr(self.messages), self.field_name)

    def __repr__(self):
        return 'Field %s caused ValidationError(%s)' % (self.field_name, self)


class NoAccountCurrencyCodeError(Exception):
    """
    Raised when the AccountCurrencyCode is missing from the data retrieved from the API.

    This should only occur if you subclassed one of the models and defined get_selector without
    a AccountCurrencyCode.
    """
    pass


class AdwordsDataInconsistencyError(Exception):
    pass