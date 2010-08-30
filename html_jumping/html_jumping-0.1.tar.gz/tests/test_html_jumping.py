# encoding: utf-8
import os
from unittest import TestCase
from html_jumping import html_jumping
from lxml import etree
from StringIO import StringIO

class test_html_jumping(TestCase):
    def setUp(self):
        self.handler = html_jumping()
    
    def test_get_html_jumping(self):      
        config = {
            'route': [
                ['http://pypi.python.org/pypi', 'GET' ],
                ['http://pypi.python.org/pypi', 'GET', {
                    'term': 'html_jumping',
                    ':action': 'search',
                    'submit': 'search'
                    
                }]
            ]
        }        
        received_header, received_content = self.handler.get(config)
        parser = etree.HTMLParser()
        tree   = etree.parse(StringIO(received_content), parser)
        
        h1_title = tree.xpath('//div[@class="section"]/h1/text()')[0]
        self.assertEqual("Index of Packages Matching 'html_jumping'", h1_title)