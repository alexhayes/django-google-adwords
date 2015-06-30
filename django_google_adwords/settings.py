from appconf.base import AppConf


class GoogleAdwordsConf(AppConf):
    # Authentication details - add to your settings file with prefix
    CLIENT_ID = ''
    CLIENT_SECRET = ''
    REFRESH_TOKEN = ''
    CLIENT_CUSTOMER_ID = ''
    DEVELOPER_TOKEN = ''

    SYNC_ACCOUNT = True
    SYNC_CAMPAIGN = False
    SYNC_ADGROUP = False
    SYNC_AD = False

    # Defaults - probably don't need to be changed
    CLIENT_VERSION = 'v201506'
    USER_AGENT = 'django-google-adwords'
    LOCK_TIMEOUT = 10 * 60  # 10 minutes
    LOCK_ID = "googleadwords-lock"
    LOCK_WAIT = 1

    # Days ago to start syncing the data from
    NEW_ACCOUNT_ACCOUNT_SYNC_DAYS = 150
    NEW_ACCOUNT_CAMPAIGN_SYNC_DAYS = 61
    NEW_ACCOUNT_ADGROUP_SYNC_DAYS = 31
    NEW_ACCOUNT_AD_SYNC_DAYS = 5

    EXISTING_ACCOUNT_SYNC_DAYS = 3
    EXISTING_CAMPAIGN_SYNC_DAYS = 3
    EXISTING_ADGROUP_SYNC_DAYS = 3
    EXISTING_AD_SYNC_DAYS = 3

    REPORT_FILE_ROOT = 'googleadwords-reportfile'
    REPORT_RETRIEVAL_CELERY_QUEUE = 'celery'
    DATA_IMPORT_CELERY_QUEUE = 'celery'
    HOUSEKEEPING_CELERY_QUEUE = 'celery'

    CELERY_TIMELIMIT = 60 * 60 * 3  # 3 HOURS
    CELERY_SOFTTIMELIMIT = CELERY_TIMELIMIT

    class Meta:
        prefix = 'GOOGLEADWORDS'
