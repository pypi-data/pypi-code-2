#:coding=utf-8:

from urlparse import urlsplit, urlunsplit

from django.core import exceptions
from django.utils.importlib import import_module
from django.test import TestCase as DjangoTestCase
from django.http import HttpRequest, HttpResponse, QueryDict
from django.conf import settings as django_settings

from beproud.django.ssl.conf import settings

AVAILABLE_SETTINGS = ['SSL_REQUEST_HEADER',]

class BaseTestCase(object):
    SSL_REQUEST_HEADER = None
    MIDDLEWARE_CLASSES = (
        'beproud.django.ssl.middleware.SSLRedirectMiddleware',
    )

    def setUp(self):
        self._old_MIDDLEWARE_CLASSES = django_settings.MIDDLEWARE_CLASSES
        if self.MIDDLEWARE_CLASSES is not None:
            django_settings.MIDDLEWARE_CLASSES = self.MIDDLEWARE_CLASSES

        for setting_name in AVAILABLE_SETTINGS:
            setting_value = getattr(self, setting_name, None)
            if setting_value:
                setattr(self, "_old_"+setting_name, getattr(settings, setting_name, None))
                setattr(settings, setting_name, setting_value)

    def tearDown(self):
        if self.MIDDLEWARE_CLASSES != self._old_MIDDLEWARE_CLASSES:
            django_settings.MIDDLEWARE_CLASSES = self._old_MIDDLEWARE_CLASSES
 
        for setting_name in AVAILABLE_SETTINGS:
            old_setting_value = getattr(self, "_old_"+setting_name, None)
            if old_setting_value is None:
                if hasattr(settings, setting_name):
                    delattr(settings, setting_name)
            else:
                setattr(settings, setting_name, old_setting_value)

    def assertRedirects(self, response, expected_url, status_code=302,
                        target_status_code=200, host=None, msg_prefix=''):
        """Asserts that a response redirected to a specific URL, and that the
        redirect URL can be loaded.

        Note that assertRedirects won't work for external links since it uses
        TestClient to do a request.
        """
        if msg_prefix:
            msg_prefix += ": "

        if hasattr(response, 'redirect_chain'):
            # The request was a followed redirect
            self.failUnless(len(response.redirect_chain) > 0,
                msg_prefix + "Response didn't redirect as expected: Response"
                " code was %d (expected %d)" %
                    (response.status_code, status_code))

            self.assertEqual(response.redirect_chain[0][1], status_code,
                msg_prefix + "Initial response didn't redirect as expected:"
                " Response code was %d (expected %d)" %
                    (response.redirect_chain[0][1], status_code))

            url, status_code = response.redirect_chain[-1]

            self.assertEqual(response.status_code, target_status_code,
                msg_prefix + "Response didn't redirect as expected: Final"
                " Response code was %d (expected %d)" %
                    (response.status_code, target_status_code))

        else:
            # Not a followed redirect
            self.assertEqual(response.status_code, status_code,
                msg_prefix + "Response didn't redirect as expected: Response"
                " code was %d (expected %d)" %
                    (response.status_code, status_code))

            url = response['Location']
            scheme, netloc, path, query, fragment = urlsplit(url)

            redirect_response = self.get(urlunsplit((scheme, netloc, path, None, None)), QueryDict(query))

            # Get the redirection page, using the same client that was used
            # to obtain the original response.
            self.assertEqual(redirect_response.status_code, target_status_code,
                msg_prefix + "Couldn't retrieve redirection page '%s':"
                " response code was %d (expected %d)" %
                    (path, redirect_response.status_code, target_status_code))

        e_scheme, e_netloc, e_path, e_query, e_fragment = urlsplit(expected_url)
        if not (e_scheme or e_netloc):
            expected_url = urlunsplit(('http', host or 'testserver', e_path,
                e_query, e_fragment))

        self.assertEqual(url, expected_url,
            msg_prefix + "Response redirected to '%s', expected '%s'" %
                (url, expected_url))

    def request(self, path, method='GET', https=False, headers={}):
        if https or urlsplit(path)[0] == 'https':
            headers = headers.copy()
            headers.update({'SERVER_PORT': '443'})
        return getattr(self.client, method.lower())(path, **headers)
    def get(self, path, https=False, headers={}):
        return self.request(path, https=https, headers=headers)
    def post(self, path, https=False, headers={}):
        return self.request(path, method='POST', https=https, headers=headers)

class SSLRedirectTests(object):

    def test_http_no_redirect(self):
        response = self.get("/some/other/url")
        self.assertContains(response, "Spam and Eggs")

    def test_http_redirect(self):
        response = self.get("/sslurl/someurl")
        self.assertRedirects(response, "https://testserver/sslurl/someurl")

    def test_https_no_redirect(self):
        response = self.get("/sslurl/someurl", https=True)
        self.assertContains(response, "Spam and Eggs")

    def test_https_redirect(self):
        response = self.get("/some/other/url", https=True)
        self.assertRedirects(response, "http://testserver/some/other/url")

class SSLDecoratorTests(object):

    def test_http_redirect(self):
        response = self.get("/decorated/ssl/view")
        self.assertRedirects(response, "https://testserver/decorated/ssl/view")

    def test_https_redirect(self):
        response = self.get("/decorated/ssl/view", https=True)
        self.assertContains(response, "Spam and Eggs")

class UseSSLTests(object):
    def setUp(self):
        self._old_USE_SSL = settings.USE_SSL
        settings.USE_SSL = False

    def tearDown(self):
        settings.USE_SSL = self._old_USE_SSL 

    def test_use_ssl_decorator(self):
        response = self.get("/decorated/ssl/view")
        self.assertContains(response, "Spam and Eggs")

        response = self.get("/decorated/ssl/view", https=True)
        self.assertContains(response, "Spam and Eggs")
         
    def test_use_ssl_middleware(self):
        response = self.get("/sslurl/someurl")
        self.assertContains(response, "Spam and Eggs")

    def test_https_redirect(self):
        response = self.get("/sslurl/someurl", https=True)
        self.assertContains(response, "Spam and Eggs")

class FlatpageTests(object):
    def setUp(self):
        super(FlatpageTests,self).setUp()
        import os
        from django.contrib.flatpages.models import FlatPage
        from django.contrib.sites.models import Site

        self._old_TEMPLATE_DIRS = django_settings.TEMPLATE_DIRS
        django_settings.TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),)
        django_settings.MIDDLEWARE_CLASSES += (
            'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
        )
        fp = FlatPage.objects.create(
            url='/flatpage/',
            title='Non-secure Flatpage',
            content='Non-secure Flatpage',
            enable_comments=False,
            template_name='flatpage.html',
            registration_required=False,
        )
        fp.sites.add(Site.objects.get_current())
        fp = FlatPage.objects.create(
            url='/sslurl/flatpage/',
            title='Secure Flatpage',
            content='Secure Flatpage',
            enable_comments=False,
            template_name='flatpage.html',
            registration_required=False,
        )
        fp.sites.add(Site.objects.get_current())

    def tearDown(self):
        super(FlatpageTests,self).tearDown()
        django_settings.TEMPLATE_DIRS = self._old_TEMPLATE_DIRS

    def test_http_flatpage_http(self):
        self.assertContains(self.get('/flatpage/'), 'Non-secure Flatpage')

    def test_http_flatpage_https(self):
        self.assertRedirects(
            self.get('/flatpage/', https=True),
            'http://testserver/flatpage/',
        )

    def test_https_flatpage_http(self):
        self.assertRedirects(
            self.get('/sslurl/flatpage/'),
            'https://testserver/sslurl/flatpage/',
        )

    def test_https_flatpage_https(self):
        self.assertContains(    
            self.get('/sslurl/flatpage/', https=True),
            'Secure Flatpage',
        )
