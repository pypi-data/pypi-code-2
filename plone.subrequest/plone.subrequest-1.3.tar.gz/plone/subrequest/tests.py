import manuel.doctest
import manuel.testcase
import manuel.testing
import unittest2 as unittest

from plone.subrequest import subrequest
from plone.subrequest.testing import INTEGRATION_TESTING, FUNCTIONAL_TESTING
from plone.testing import z2
from zope.globalrequest import getRequest
from zope.site.hooks import getSite

def traverse(url):
    request = getRequest()
    traversed = request.traverse(url)
    request.processInputs()
    request['PATH_INFO'] = url
    return request


class FunctionalTests(unittest.TestCase):
    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.browser = z2.Browser(self.layer['app'])

    def test_absolute(self):
        self.browser.open('http://nohost/folder1/@@url')
        self.assertEqual(self.browser.contents, 'http://nohost/folder1')

    def test_virtual_hosting(self):
        parts = ('folder1', 'folder1A/@@url')
        expect = 'folder1A'
        url = "http://nohost/VirtualHostBase/http/example.org:80/%s/VirtualHostRoot/_vh_fizz/_vh_buzz/_vh_fizzbuzz/%s" % parts
        expect_url = 'http://example.org/fizz/buzz/fizzbuzz/%s' % expect
        self.browser.open(url)
        self.assertEqual(self.browser.contents, expect_url)

    def test_virtual_hosting_relative(self):
        parts = ('folder1', 'folder1A?url=folder1Ai/@@url')
        expect = 'folder1A/folder1Ai'
        url = "http://nohost/VirtualHostBase/http/example.org:80/%s/VirtualHostRoot/_vh_fizz/_vh_buzz/_vh_fizzbuzz/%s" % parts
        expect_url = 'http://example.org/fizz/buzz/fizzbuzz/%s' % expect
        self.browser.open(url)
        self.assertEqual(self.browser.contents, expect_url)

    def test_virtual_hosting_absolute(self):
        parts = ('folder1', 'folder1A?url=/folder1B/@@url')
        expect = 'folder1B'
        url = "http://nohost/VirtualHostBase/http/example.org:80/%s/VirtualHostRoot/_vh_fizz/_vh_buzz/_vh_fizzbuzz/%s" % parts
        expect_url = 'http://example.org/fizz/buzz/fizzbuzz/%s' % expect
        self.browser.open(url)
        self.assertEqual(self.browser.contents, expect_url)   


class IntegrationTests(unittest.TestCase):
    layer = INTEGRATION_TESTING

    def test_absolute(self):
        response = subrequest('/folder1/@@url')
        self.assertEqual(response.body, 'http://nohost/folder1')

    def test_absolute_query(self):
        response = subrequest('/folder1/folder1A?url=/folder2/folder2A/@@url')
        self.assertEqual(response.body, 'http://nohost/folder2/folder2A')

    def test_relative(self):
        response = subrequest('/folder1?url=folder1B/@@url')
        # /folder1 resolves to /folder1/@@test
        self.assertEqual(response.body, 'http://nohost/folder1/folder1B')

    def test_root(self):
        response = subrequest('/')
        self.assertEqual(response.body, 'Root: http://nohost')

    def test_virtual_hosting(self):
        url = "/VirtualHostBase/http/example.org:80/%s/VirtualHostRoot/_vh_fizz/_vh_buzz/_vh_fizzbuzz/%s" % ('folder1', 'folder1A/@@url')
        response = subrequest(url)
        self.assertEqual(response.body, 'http://example.org/fizz/buzz/fizzbuzz/folder1A')

    def test_virtual_hosting_relative(self):
        url = "/VirtualHostBase/http/example.org:80/%s/VirtualHostRoot/_vh_fizz/_vh_buzz/_vh_fizzbuzz/%s" % ('folder1', 'folder1A?url=folder1B/@@url')
        response = subrequest(url)
        self.assertEqual(response.body, 'http://example.org/fizz/buzz/fizzbuzz/folder1B')

    def test_not_found(self):
        response = subrequest('/notfound')
        self.assertEqual(response.status, 404)

    def test_virtual_host_root(self):
        parts = ('folder1', 'folder1A/@@url')
        url = "/VirtualHostBase/http/example.org:80/%s/VirtualHostRoot/_vh_fizz/_vh_buzz/_vh_fizzbuzz/%s" % parts
        traverse(url)
        response = subrequest('/folder1B/@@url')
        self.assertEqual(response.body, 'http://example.org/fizz/buzz/fizzbuzz/folder1B')

    def test_virtual_host_root_with_root(self):
        parts = ('folder1', 'folder1A/@@url')
        url = "/VirtualHostBase/http/example.org:80/%s/VirtualHostRoot/_vh_fizz/_vh_buzz/_vh_fizzbuzz/%s" % parts
        traverse(url)
        app = self.layer['app']
        response = subrequest('/folder1Ai/@@url', root=app.folder1.folder1A)
        self.assertEqual(response.body, 'http://example.org/fizz/buzz/fizzbuzz/folder1A/folder1Ai')

    def test_virtual_host_space(self):
        parts = ('folder2', 'folder2A/folder2Ai space/@@url')
        url = "/VirtualHostBase/http/example.org:80/%s/VirtualHostRoot/%s" % parts
        traverse(url)
        app = self.layer['app']
        response = subrequest('/folder2A/@@url', root=app.folder2)
        self.assertEqual(response.body, 'http://example.org/folder2A')

    def test_subrequest_root(self):
        app = self.layer['app']
        response = subrequest('/folder1Ai/@@url', root=app.folder1.folder1A)
        self.assertEqual(response.body, 'http://nohost/folder1/folder1A/folder1Ai')

    def test_site(self):
        app = self.layer['app']
        traverse('/folder1')
        site_url1 = getSite().absolute_url()
        response = subrequest('/folder2/@@url')
        self.assertEqual(response.status, 200)
        site_url2 = getSite().absolute_url()
        self.assertEqual(site_url1, site_url2)

def test_suite():
    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    m = manuel.doctest.Manuel()
    m += manuel.testcase.MarkerManuel()
    doctests = manuel.testing.TestSuite(m, '../../README.txt', globs=dict(subrequest=subrequest, traverse=traverse))
    # Set the layer on the manuel doctests for now
    for test in doctests:
        test.layer = INTEGRATION_TESTING
        test.globs['layer'] = INTEGRATION_TESTING
    suite.addTest(doctests)
    return suite
