# -*- coding: utf-8 -*-
import sys
import new
import unittest
from django.db.models import loading
from django.core.management import call_command
from django.test import TestCase

import django_cachepurge
from django_cachepurge import middleware

# from . import testing models # only python 2.5+
from django_cachepurge.tests import testingmodels

class CachePurgeTestCase(TestCase):

    urls = 'django_cachepurge.tests.urls'

    def _pre_setup(self):
        # register tests models
        # we'll fake an app named 'cachepurge_test_app'
        module = new.module('cachepurge_test_app')
        module.__file__ = __file__ # somewhere django looks at __file__. Feed it.
        module.models = testingmodels
        testingmodels.__name__ = 'cachepurge_test_app.models'
        sys.modules['cachepurge_test_app'] = module

        # register fake app in django and create DB models
        from django.conf import settings
        settings.INSTALLED_APPS += ('cachepurge_test_app',)
        loading.load_app('cachepurge_test_app')
        call_command('syncdb', verbosity=0, interactive=False)

        return super(CachePurgeTestCase, self)._pre_setup()

    def setUp(self):
        super(CachePurgeTestCase, self).setUp()
        django_cachepurge.clear_urls()

        # patch middleware pruneAsync to catch url calls
        self._original_pruneAsync = middleware.pruneAsync
        self._pruned_urls = []
        middleware.pruneAsync = self.addPrunedUrl

    def tearDown(self):
        # restore patched method
        middleware.pruneAsync = self._original_pruneAsync
        super(CachePurgeTestCase, self).tearDown()

    def addPrunedUrl(self, url):
        self._pruned_urls.append(url)

    def clearPrunedUrls(self):
        self._pruned_urls = []

    @property
    def pruned_urls(self):
        return sorted(self._pruned_urls)

    def test_urls_accumulator(self):
        self.assertEquals(django_cachepurge.get_urls(), set())

        # add 1 url
        django_cachepurge.add_purge_url('/some/url')
        self.assertEquals(django_cachepurge.get_urls(), set(('/some/url',)))

        # add url twice
        django_cachepurge.add_purge_url('/some/url')
        self.assertEquals(django_cachepurge.get_urls(), set(('/some/url',)))

        # clear
        django_cachepurge.clear_urls()
        self.assertEquals(django_cachepurge.get_urls(), set())

    def test_signals(self):

        self.assertEquals(django_cachepurge.get_urls(), set())

        # create
        content = testingmodels.UrlModel(title=u'model with url')
        content.save()
        self.assertEquals(sorted(django_cachepurge.get_urls()),
                          ['/content/1', '/some/related/url'])

        # edit
        django_cachepurge.clear_urls()
        content.title = u'edited title'
        self.assertEquals(django_cachepurge.get_urls(), set())
        content.save()
        self.assertEquals(sorted(django_cachepurge.get_urls()),
                          ['/content/1', '/some/related/url'])

        # delete
        django_cachepurge.clear_urls()
        content.delete()
        self.assertEquals(sorted(django_cachepurge.get_urls()),
                          ['/content/1', '/some/related/url'])

    def test_no_url_model_signals(self):
        self.assertEquals(django_cachepurge.get_urls(), set())

        # create
        content = testingmodels.NoUrlModel(title=u'model without url')
        content.save()
        self.assertEquals(django_cachepurge.get_urls(), set())

        content.title = u'edited title'
        content.save()
        self.assertEquals(django_cachepurge.get_urls(), set())

        content.delete()
        self.assertEquals(django_cachepurge.get_urls(), set())

    def test_purge_url_only_model_signals(self):
        self.assertEquals(django_cachepurge.get_urls(), set())
        # create
        content = testingmodels.OnlyPurgeUrls(title=u'model with purge url only')
        content.save()
        self.assertEquals(sorted(django_cachepurge.get_urls()),
                          ['/some/other/url'])

        # edit
        django_cachepurge.clear_urls()
        content.title = u'edited title'
        self.assertEquals(django_cachepurge.get_urls(), set())
        content.save()
        self.assertEquals(sorted(django_cachepurge.get_urls()),
                          ['/some/other/url'])

        # delete
        django_cachepurge.clear_urls()
        content.delete()
        self.assertEquals(sorted(django_cachepurge.get_urls()),
                          ['/some/other/url'])

    def test_middleware(self):
        content = testingmodels.UrlModel(title=u'model with url')
        content.save()
        django_cachepurge.clear_urls()
        self.client.post('/content/1/edit', {'title': u'edited by web request'})
        self.assertEquals(self.pruned_urls,
                          ['http://127.0.0.1:3128/content/1',
                           'http://127.0.0.1:3128/some/related/url'])

    def test_middleware_with_two_caches(self):

        original_urls = middleware.CACHE_URLS
        middleware.CACHE_URLS = ('http://127.0.0.1:3128',
                                 'http://localhost:8888')
        content = testingmodels.UrlModel(title=u'model with url')
        content.save()
        django_cachepurge.clear_urls()
        self.client.post('/content/1/edit', {'title': u'edited by web request'})

        self.assertEquals(self.pruned_urls,
                          ['http://127.0.0.1:3128/content/1',
                           'http://127.0.0.1:3128/some/related/url',
                           'http://localhost:8888/content/1',
                           'http://localhost:8888/some/related/url'])
        # restore value
        middleware.CACHE_URLS = original_urls

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CachePurgeTestCase))
    return suite
