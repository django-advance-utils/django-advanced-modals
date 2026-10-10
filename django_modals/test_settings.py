"""The least Django needs to run ``django_modals``' own tests.

    django-admin test django_modals.tests --settings=django_modals.test_settings --pythonpath=.

The examples project is not used: it pulls in celery, datatables and the rest of the demo stack,
none of which these tests have anything to do with.

crispy-forms 2 moved its template packs out into their own packages, so ``crispy_bootstrap4`` is
an installed app when it is installed. Under crispy-forms 1.x it is not there, and the pack comes
from crispy_forms itself.
"""

from importlib.util import find_spec

SECRET_KEY = 'django-modals-tests'
DEBUG = False
USE_TZ = True

ROOT_URLCONF = 'django_modals.test_settings'
urlpatterns = []

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'crispy_forms',
    *(['crispy_bootstrap4'] if find_spec('crispy_bootstrap4') else []),
]

CRISPY_ALLOWED_TEMPLATE_PACKS = ('bootstrap4',)
CRISPY_TEMPLATE_PACK = 'bootstrap4'

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': []},
    }
]
