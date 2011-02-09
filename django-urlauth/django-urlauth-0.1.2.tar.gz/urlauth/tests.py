from datetime import datetime, timedelta
import pickle
import cgi

from django.test import TestCase
from django.test.client import Client
from django.conf.urls.defaults import *
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
import django.dispatch

from urlauth.util import wrap_url, load_key, InvalidKey
from urlauth.models import AuthKey
from urlauth.signals import key_user_found, key_loaded

class UrlauthTestCase(TestCase):
    urls = 'urlauth.tests'
    test_url = '/urlauth_test_view/'
    
    # Helpers
    def setUp(self):
        """
        Create active and inactive users.
        """

        User.objects.all().delete()
        self.user = User.objects.create_user('user', 'user@host.com', 'pass')
        self.ban_user = User.objects.create_user('ban_user', 'ban_user@host.com',
                                                 'pass')
        self.ban_user.is_active = False
        self.ban_user.save()

    def process_url(self, url, **kwargs):
        """
        Add authkey to the ``url`` and then open that url with django test client.

        Returns:
            The ID of created ``AuthKey`` instance
        """

        url = wrap_url(url, **kwargs)
        path, args = url.split('?')[0], cgi.parse_qs(url.split('?')[1])
        self.client.get(url, args)
        return args[settings.URLAUTH_AUTHKEY_NAME][0]

    # Test cases

    def test_create_key(self):
        self.assertTrue(AuthKey.objects.create_key(uid=self.user.pk,
                                                   expired=datetime.now()))

    def test_wrap_url(self):
        expired = datetime.now()

        AuthKey.objects.all().delete()
        clean_url = 'http://ya.ru'
        url = wrap_url(clean_url, uid=self.user.pk, expired=expired)
        key = AuthKey.objects.get()
        self.assertEqual(url, '%s?%s=%s' % (clean_url,
                                            settings.URLAUTH_AUTHKEY_NAME, key.id))

        AuthKey.objects.all().delete()
        clean_url = 'http://ya.ru?foo=bar'
        url = wrap_url(clean_url, uid=self.user.pk, expired=expired)
        key = AuthKey.objects.get()
        self.assertEqual(url, '%s&%s=%s' % (clean_url,
                                            settings.URLAUTH_AUTHKEY_NAME, key.id))

    def test_validate_key(self):
        expired = datetime.now() - timedelta(seconds=1)
        key = AuthKey.objects.create_key(uid=self.user.pk, expired=expired, foo='bar')
        self.assertRaises(InvalidKey, lambda: load_key(key))

        expired = datetime.now() + timedelta(seconds=10)
        key = AuthKey.objects.create_key(uid=self.user.pk, expired=expired)
        self.assertTrue(load_key(key))

    def test_authentication(self): 
        expired = datetime.now() + timedelta(days=1)
        resp = self.client.get(self.test_url)

        # Guest is not authenticated
        self.client.logout()
        self.assertFalse('_auth_user_id' in self.client.session)

        ## Simple authorization
        self.client.logout()
        self.process_url(self.test_url, uid=self.user.pk, expired=expired)
        self.assertEqual(self.client.session['_auth_user_id'], self.user.pk)

        ## Baned user can't authorize
        self.client.logout()
        self.process_url(self.test_url, uid=self.ban_user.pk, expired=expired)
        self.assertFalse('_auth_user_id' in self.client.session)

        ## Expired auth key does not work
        self.client.logout()
        expired = datetime.now() - timedelta(seconds=1)
        self.process_url(self.test_url, uid=self.user.pk, expired=expired)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_signals(self):
        logs = []

        handler1 = lambda **k: logs.append('L')
        handler2 = lambda **k: logs.append('U')

        key_loaded.connect(handler1)
        key_user_found.connect(handler2)

        self.assertEqual(0, len(logs))
        self.client.logout()
        expired = datetime.now() + timedelta(days=1)
        self.process_url(self.test_url, uid=self.user.pk, expired=expired)
        self.assertEqual(2, len(logs))

    def test_onetime_feature(self):
        self.client.logout()
        expired = datetime.now() + timedelta(days=1)
        hash = self.process_url(self.test_url, uid=self.user.pk,
                                expired=expired)
        self.assertFalse(AuthKey.objects.filter(id=hash).count())

        self.client.logout()
        expired = datetime.now() + timedelta(days=1)
        hash = self.process_url(self.test_url, uid=self.user.pk,
                                expired=expired, onetime=False)
        self.assertTrue(AuthKey.objects.filter(id=hash).count())


def test_view(request):
    return HttpResponse('')

urlpatterns = patterns('',
    url('urlauth_test_view/', test_view, name='urlauth_test_view'),
)
