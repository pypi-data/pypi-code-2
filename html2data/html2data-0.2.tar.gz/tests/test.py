# encoding: utf-8
import os
from unittest import TestCase
from html2data import html2data

class TestHtml2Data(TestCase):
    def setUp(self):
        self.handler = html2data()
    
    def test_load_html2xml(self):
        html = """<!DOCTYPE html><html lang="en"><head>
                <meta charset="utf-8" />
                <title>Example Page</title>
                <link rel="stylesheet" href="css/main.css" type="text/css" />
            </head>
            <body>
                <h1><b>Title</b></h1>
                <div class="description">This is not a valid HTML
            </body>
        </html>
        """
        
        config = {
            'map': [
                ['header_title', u'//head/title/text()'],
                ['body_title', u'//h1/b/text()'],
                ['description', u'//div[@class="description"]/text()'],
            ]
        }

        expected_obj = {
            "header_title": "Example Page",
            "body_title": "Title",
            "description": "This is not a valid HTML"
        }
        
        received_obj = self.handler.load(html = html, config=config)
        self.assertEqual(expected_obj, received_obj)