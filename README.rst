=====================
django-google-adwords
=====================

Django modelling and helpers for the Google Adwords API.


Installation
============

You can install django-google-adwords either via the Python Package Index (PyPI)
or from bitbucket.

To install using pip;

.. code-block:: bash

    pip install django-google-adwords

From github;

.. code-block:: bash

    pip install git+https://bitbucket.org/alexhayes/django-google-adwords.git


Settings
========

Required
--------

You must place the following in your django settings file.

.. code-block:: python

	GOOGLEADWORDS_CLIENT_ID = 'your-adwords-client-id'
	GOOGLEADWORDS_CLIENT_SECRET = 'your-adwords-client-secret'
	GOOGLEADWORDS_REFRESH_TOKEN = 'your-adwords-refresh-token'
	GOOGLEADWORDS_DEVELOPER_TOKEN = 'your-adwords-developer-token'
	GOOGLEADWORDS_CLIENT_CUSTOMER_ID = 'your-adwords-client-customer-id'

If you don't know these values already you'll probably want to read the Google Adwords `OAuth 2.0 Authentication`_
documentation.

.. _`OAuth 2.0 Authentication`: https://developers.google.com/adwords/api/docs/guides/authentication


Other Settings
--------------

Other settings can be found in :code:`django_google_adwords.settings` and can be overridden by
putting them in your settings file prepended with :code:`GOOGLEADWORDS_`.


Celery
------

`Celery`_ installation and configuration is somewhat out of the scope of this 
document but in order to sync Google Adwords data into models you will need a
working Celery.

Essentially the syncing of data is a two step process, as follows;

1. Reports are downloaded from Adwords using the Celery queue specified in the 
setting :code:`GOOGLEADWORDS_REPORT_RETRIEVAL_CELERY_QUEUE`.
2. Downloaded reports are processed using the Celery queue specified in the 
setting :code:`GOOGLEADWORDS_DATA_IMPORT_CELERY_QUEUE`.  

By default the above two settings, along with :code:`GOOGLEADWORDS_HOUSEKEEPING_CELERY_QUEUE`
are set to :code:`celery` however you may want to spilt these up with different
workers, as follows;

.. code-block:: python

	GOOGLEADWORDS_REPORT_RETRIEVAL_CELERY_QUEUE = 'adwords_retrieval'
	GOOGLEADWORDS_DATA_IMPORT_CELERY_QUEUE = 'adwords_import'
	GOOGLEADWORDS_HOUSEKEEPING_CELERY_QUEUE = 'adwords_housekeeping'

With the above you could run the following workers;

.. code-block:: python

	celery worker --app myapp --queues adwords_retrieval &
    celery worker --app myapp --queues adwords_import &
    celery worker --app myapp --queues adwords_housekeeping &


.. _`Celery`: http://www.celeryproject.org


Usage
=====

Storing local data
------------------

The provided models include methods to sync data from the Google Adwords API to the local models 
so that it can be queried at a later stage.

.. code-block:: python

	account_id = [YOUR GOOGLE ADWORDS ACCOUNT ID]
	account = Account.objects.create(account_id=account_id)
	result = account.sync() # returns a celery AsyncResult

Depending on the amount of data contained with your Adwords account the above could take quite
some time to populate! Advice is to monitor the celery task.

You can control what data is sync'd with the following settings:

.. code-block:: python

	GOOGLEADWORDS_SYNC_ACCOUNT = True    # Sync account data
	GOOGLEADWORDS_SYNC_CAMPAIGN = True   # Sync campaign data
	GOOGLEADWORDS_SYNC_ADGROUP = True    # Sync adgroup data
	GOOGLEADWORDS_SYNC_AD = False        # Sync ad data - note this can take a LOOOONNNNG time if you have lots of ads... 
	
	GOOGLEADWORDS_NEW_ACCOUNT_ACCOUNT_SYNC_DAYS = 61
	GOOGLEADWORDS_NEW_ACCOUNT_CAMPAIGN_SYNC_DAYS = 61
	GOOGLEADWORDS_NEW_ACCOUNT_AD_GROUP_SYNC_DAYS = 31
	GOOGLEADWORDS_NEW_ACCOUNT_AD_SYNC_DAYS = 3
	GOOGLEADWORDS_EXISTING_ACCOUNT_SYNC_DAYS = 3


Paged data
----------

To use the API but not store data in the models you can page through yielded data with the following; 

.. code-block:: python

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


Google Adwords API Versions
===========================

The intention is to keep in sync with the latest available Google Adwords API 
versions.

To do this it's highly possible we'll need to break backwards compatibility as
the API often does!

Currently we support `v201409`_ however this will `sunset on 14 July 2015`_.

Support for `v201502`_ will be added very soon but note there will be a number
of `backwards compatibility changes`_ that will most likely break your code.

.. _`v201409`: http://googleadsdeveloper.blogspot.com.au/2014/10/announcing-v201409-of-adwords-api.html
.. _`sunset on 14 July 2015`: https://developers.google.com/adwords/api/docs/sunset-dates
.. _`v201502`: http://googleadsdeveloper.blogspot.com.au/2015/03/announcing-v201502-of-adwords-api.html
.. _`backwards compatibility changes`: https://developers.google.com/adwords/api/docs/guides/migration/v201502


Backwards Incompatibility Changes
=================================

v0.6.0
------

- Changed setting :code:`GOOGLEADWORDS_START_FINISH_CELERY_QUEUE` to :code:`GOOGLEADWORDS_HOUSEKEEPING_CELERY_QUEUE`.
- Removed :code:`Alert.sync_alerts()`, :code:`Alert.get_selector()` and task :code:`sync_alerts` as the services that these functions call have been discontinued in the Google API. The :code:`Alert` model remains in place so that existing alerts can be accessed if required.

v0.4.0
------

- Now using Django 1.7 migrations.
- Switched from money to djmoney (which itself uses py-moneyed).


Contributing
============

You are encouraged to contribute - please fork and submit pull requests. To get
a development environment up you should be able to do the following;

.. code-block:: bash

	git clone https://bitbucket.org/alexhayes/django-google-adwords.git
	cd django-google-adwords
	pip instal -r requirements/default.txt
	pip instal -r requirements/test.txt
	./runtests.py

And to run the full test suite, you can then run;

.. code-block:: bash

	tox

Note tox tests for Python 2.7, 3.3, 3.4 and PyPy for Django 1.7 and 1.8. 
You'll need to consolute the docs for installation of these Python versions
on your OS, on Ubuntu you can do the following;

.. code-block:: bash

	sudo apt-get install python-software-properties
	sudo add-apt-repository ppa:fkrull/deadsnakes
	sudo apt-get update
	sudo apt-get install python2.7 python2.7-dev
	sudo apt-get install python3.3 python3.3-dev
	sudo apt-get install python3.4 python3.4-dev
	sudo apt-get install pypy pypy-dev

Note that :code:`django-nose` issue `#133`_ and `#197`_ cause issues with some 
tests thus the reason for `alexhayes/django-nose`_ being used in the 
:code:`requirements/test.py` and :code:`requirements/test3.py`.

.. _`#133`: https://github.com/django-nose/django-nose/issues/133
.. _`#197`: https://github.com/django-nose/django-nose/issues/197
.. _`alexhayes/django-nose`: https://github.com/alexhayes/django-nose  


Thanks
======

Thank-you to `roi.com.au`_ for supporting this project.

.. _`roi.com.au`: http://roi.com.au


Authors
=======

- Jeremy Storer <storerjeremy@gmail.com>
- Alex Hayes <alex@alution.com>
