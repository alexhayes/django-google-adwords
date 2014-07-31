# Django Google Adwords

A Django app that provides retrieval and storage of data from the Google Adwords API.

## Requirements

- googleads==2.0.0
- xmltodict==0.9.0
- django-appconf==0.6
- celery==3.1.12

You can install these with the following;

```bash
pip install googleads==1.0.6
pip install xmltodict==0.9.0
pip install django-appconf==0.6
pip install celery==3.1.12
```

This README does not discuss the [configuration of celery](http://docs.celeryproject.org/en/latest/configuration.html) 
but note that if you will be using the `sync` methods (discussed below) they use chords, thus you need to ensure you have 
[CELERY_RESULT_BACKEND](http://docs.celeryproject.org/en/latest/configuration.html?highlight=celery_backend#celery-result-backend) set.

## Installation

```bash
pip install git+https://bitbucket.org/alexhayes/django-google-adwords.git
```

## Settings

### Required

You must place the following in your django settings file.

```python
GOOGLEADWORDS_CLIENT_ID = 'your-adwords-client-id'
GOOGLEADWORDS_CLIENT_SECRET = 'your-adwords-client-secret'
GOOGLEADWORDS_REFRESH_TOKEN = 'your-adwords-refresh-token'
GOOGLEADWORDS_DEVELOPER_TOKEN = 'your-adwords-developer-token'
GOOGLEADWORDS_CLIENT_CUSTOMER_ID = 'your-adwords-client-customer-id'
```

### Other Settings

Other settings can be found in `django_google_adwords.settings` and can be overridden by
putting them in your settings file appended with 'GOOGLEADWORDS_'.

For instance, if you want to process all retrieval of data with a different celery queue 
you can do so with;

```python
GOOGLEADWORDS_CELERY_QUEUE = 'my-celery-queue-name'
```

## Usage

### Storing local data

The provided models include methods to sync data from the Google Adwords API to the local models 
so that it can be queried at a later stage.

```python
account_id = [YOUR GOOGLE ADWORDS ACCOUNT ID]
account = Account.objects.create(account_id=account_id)
result = account.sync() # returns a celery AsyncResult
```

Depending on the amount of data contained with your Adwords account the above could take quite
some time to populate.

You can control what data is sync'd with the following settings:

```python
GOOGLEADWORDS_SYNC_ACCOUNT = True    # Sync account data
GOOGLEADWORDS_SYNC_CAMPAIGN = True   # Sync campaign data
GOOGLEADWORDS_SYNC_ADGROUP = True    # Sync adgroup data
GOOGLEADWORDS_SYNC_AD = False        # Sync ad data - note this can take a LOOOONNNNG time if you have lots of ads... 

GOOGLEADWORDS_NEW_ACCOUNT_ACCOUNT_SYNC_DAYS = 61
GOOGLEADWORDS_NEW_ACCOUNT_CAMPAIGN_SYNC_DAYS = 61
GOOGLEADWORDS_NEW_ACCOUNT_AD_GROUP_SYNC_DAYS = 31
GOOGLEADWORDS_NEW_ACCOUNT_AD_SYNC_DAYS = 3
GOOGLEADWORDS_EXISTING_ACCOUNT_SYNC_DAYS = 3
```

### Paged data

To use the API but not store data in the models you can page through yielded data with the following; 

```python
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
```

## Thanks

Thank-you to [roi.com.au](http://roi.com.au) for supporting this project.

## Authors

- Jeremy Storer <storerjeremy@gmail.com>
- Alex Hayes <alex@alution.com>