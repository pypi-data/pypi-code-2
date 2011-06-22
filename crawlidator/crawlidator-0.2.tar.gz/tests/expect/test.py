#!/usr/bin/env python
import unittest
import crawlidator

class CrawlidatorTest(unittest.TestCase):
    def test_get_urls_from_sitemap(self):
        sitemap = open('fixtures/sitemap.xml')
        expected_urls = list(open('expect/test_get_urls_from_sitemap.1'))
        urls = crawlidator.get_urls_from_sitemap(sitemap)
        self.assert_(len(urls)>0, 'No urls found.')
        for url, expected in zip(urls, expected_urls):
            self.assertEqual(url, expected[:-1]) #strip newline

    def test_get_urls_from_sitemap_with_base(self):
        sitemap = open('fixtures/sitemap.xml')
        expected_urls = list(open('expect/test_get_urls_from_sitemap.2'))
        urls = crawlidator.get_urls_from_sitemap(sitemap, 'http://www.cwi.nl/')
        self.assert_(len(urls)>0, 'No urls found.')
        for url, expected in zip(urls, expected_urls):
            self.assertEqual(url, expected[:-1]) #strip newline

    def test_get_urls_from_sitemap_using_url(self):
        sitemap = 'http://www.cwi.nl/sitemap.xml'
        urls = crawlidator.get_urls_from_sitemap(sitemap)
        self.assert_(len(urls)>0, 'No urls found.')
        for url in urls:
            self.assert_(url.startswith('http://www.cwi.nl/'), 'Wrong base url')

    def test_get_urls_from_sitemap_since(self):
        sitemap = open('fixtures/sitemap.xml')
        expected_urls = map(lambda ln: ln[:-1], open('expect/test_get_urls_from_sitemap.3'))
        from datetime import datetime
        urls = crawlidator.get_urls_from_sitemap(sitemap, 
            baseurl='http://www.cwi.nl/',
            since=datetime(2008, 9, 4))
        self.assert_(len(urls)>0, 'No urls found.')
        self.failIf(len(urls) > len(expected_urls), 'Too many urls found')
        self.failIf(len(urls) < len(expected_urls), 'Too few urls found')
        self.assertEqual(urls, expected_urls, 'Found urls differ form expexted urls')

    def test_validate(self):
        page = open('fixtures/index.html')
        crawlidator.validate(page)
        page = open('fixtures/aboutCWI.html')
        self.assertRaises(crawlidator.ValidationError, crawlidator.validate, file=page)

    def test_w3c_url(self):
        url = u'http://www.cwi.nl/en/aboutCWI'
        w3curl = crawlidator.w3c_url(url)
        expect = 'http://validator.w3.org/check?verbose=1&uri=http%3A%2F%2Fwww.cwi.nl%2Fen%2FaboutCWI'
        self.assertEqual(w3curl, expect)

if __name__ == '__main__':
    unittest.main()
