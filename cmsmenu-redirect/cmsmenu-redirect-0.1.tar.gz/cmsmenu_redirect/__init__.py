from django.conf import settings

if 'cmsmenu_redirect' in settings.INSTALLED_APPS:
    assert 'django.contrib.redirects' in settings.INSTALLED_APPS

