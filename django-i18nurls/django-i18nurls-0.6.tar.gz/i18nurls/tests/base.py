import os

from django.core.urlresolvers import clear_url_caches
from django.conf import settings
from django.test import TestCase
from django.utils.translation import activate


class BaseTestCase(TestCase):
    
    def _update_setting(self, key, value):
        if not key in self.old_settings:
            self.old_settings[key] = getattr(settings, key)
        setattr(settings, key, value)
    
    def setUp(self):
        clear_url_caches()
        
        self.old_settings = {}
        
        self._update_setting('DEBUG', True)
        self._update_setting('TEMPLATE_DEBUG', True)
        
        self._update_setting('ROOT_URLCONF',
            'i18nurls.tests.urls'
        )
        
        self._update_setting('MIDDLEWARE_CLASSES', (
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'i18nurls.middleware.LocaleMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ))
        
        self._update_setting('LANGUAGES', (
            ('nl', 'Dutch'),
            ('en', 'English'),
        ))
    
    def tearDown(self):
        for key in self.old_settings:
            setattr(settings, key, self.old_settings[key])
