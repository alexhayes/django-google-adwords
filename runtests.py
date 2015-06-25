#!/usr/bin/env python
import sys

import django
from django.conf import settings
from django.core.management import execute_from_command_line
import os
import shutil


if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.admin',
            'django.contrib.sessions',
            'django_nose',
            'django_google_adwords',
        ],
        # Django replaces this, but it still wants it. *shrugs*
        DATABASE_ENGINE='django.db.backends.sqlite3',
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        LOGGING = {
            'version': 1,
            'disable_existing_loggers': False,
            'loggers': {
                'django.db.backends.schema': {
                    'propagate': False,
                    'level': 'WARNING',
                },
                'django_google_adwords.models.locker': {
                    'propagate': False,
                    'level': 'WARNING',
                },
            }
        },
        MEDIA_ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__), 'django_google_adwords', 'tests', 'media')),
        GOOGLEADWORDS_REPORT_FILE_ROOT='dga-test-reports',
        MIDDLEWARE_CLASSES={},
        TEST_RUNNER='django_nose.NoseTestSuiteRunner',
        NOSE_ARGS=['--logging-clear-handlers',
                   # Coverage - turn on with NOSE_WITH_COVERAGE=1
                   '--cover-html',
                   '--cover-package=django_google_adwords',
                   '--cover-erase',
                   '--with-fixture-bundling',
                   # Nose Progressive
                   '--with-progressive',
                   ]
    )


def runtests():
    test_args = sys.argv[1:] if len(sys.argv[1:]) > 0 else ['django_google_adwords.tests']
    test_args.append('--with-fixture-bundling')
    argv = sys.argv[:1] + ['test'] + test_args
    execute_from_command_line(argv)
    # Cleanup any files created, don't do in tear down in case MEDIA_ROOT is misconfigured
    path = os.path.join(settings.MEDIA_ROOT, settings.GOOGLEADWORDS_REPORT_FILE_ROOT)
    if os.path.exists(path):
        shutil.rmtree(path)


if __name__ == '__main__':
    runtests()
