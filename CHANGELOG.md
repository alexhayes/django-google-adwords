# Release 0.6.2 - Thu Jun 25 14:48:36 AEST 2015

- Fixed issue with the finish_*_sync celery tasks not chaining as expected.

# Release 0.6.1 - Thu Jun 25 13:49:10 AEST 2015

- Updated README
- Fixed links to django-nose issues.

# Release 0.6.0 - Thu Jun 25 12:05:09 AEST 2015

- Added tox support with tests for Python 2.7, 3.3, 3.4 and PyPy.
- Updated README.md to README.rst in preparation for pypi support.
- Added runtests.py script to run tests inside app.
- Moved repository from bitbucket to github.
- Removed random printing.
- PEP8 support (mostly...).
- Fixed issue that could occur with locking on memcache.
- Now using django-cereal for more efficient communication over the wire in Celery.
- Changed setting `GOOGLEADWORDS_START_FINISH_CELERY_QUEUE` to `GOOGLEADWORDS_HOUSEKEEPING_CELERY_QUEUE`.
- Removed `Alert.sync_alerts()`, `Alert.get_selector()` and task `sync_alerts` as the services that these functions call have been discontinued in the Google API. The :code:`Alert` model remains in place so that existing alerts can be accessed if required.

# Release 0.5.0 - Thu May 21 12:27:05 AEST 2015

- Modified cache based locking mechanisms to improve speed.

# Release 0.4.2 - Thu Mar 19 15:41:22 AEDT 2015

- Ensured Account.QuerySet methods return data ordered by day.
- Added helper methods on Account for ad_groups and ads and Campaign for ads.

# Release 0.4.1 - Mon Mar  2 08:42:34 AEDT 2015

- Changed to use latest version of api

# Release 0.4.0 - Wed Jan 28 15:25:00 AEDT 2015

- Django 1.7 support
- Now using django-money instead of python-money (which looks to be no longer supported and doesn't work in Django 1.7 - thanks t3kn0s).
- Exception AdwordsDataInconsistency is now AdwordsDataInconsistencyError
- Currency is no longer a default on each model Money field, it's now derived from the returned data
- New settings GOOGLEADWORDS_CELERY_TIMELIMIT and GOOGLEADWORDS_CELERY_SOFTTIMELIMIT
- Updated README with requirements and installation instructions
- PEP8
- Replaced the use of the 'money' module with 'djmoney' since the python-money module hasn't been updated for >3 years. Replaced the hard-coded currency with a variable

# Release 0.3.4 - Mon Aug 18 11:06:19 EST 2014

- Added some querysets

# Release 0.3.3 - Wed Aug 13 08:45:18 EST 2014

- Added Ad approval status field to model

# Release 0.3.2 - Thu Aug  7 11:34:15 EST 2014

- Changed some field names, changed tests to use gz files

# Release 0.3.1 - Fri Aug  1 13:55:09 EST 2014

- Changed top ads adgroup by conversion
- Added custom sync tasks

# Release 0.3.0 - Thu Jul 31 15:21:22 EST 2014

- Bug fix
- Added more queryset filters
- Changed report downloaded to use csv.gz
- Added queryset helpers to AdGroup
- Changed sync celery queue.
- 'account_metrics' getter now 'metrics' to follow convention.
- Added 'with_period' queryset
- Removed get_ from queryset filters
- Refs #1769: Added get data queryset methods
- Updated to use googleads 2.0.0
- Made some changes, error handling, model changes
- Refactored a bit of stuff and added more last synced dates for different aspects

# Release 0.2.0 - Mon Jul 28 14:23:35 EST 2014

- Support for Google Adwords v201402

# Release 0.1.0 - Mon Jul 21 10:55:51 EST 2014

- Initial release

