from __future__ import with_statement

import sys
import os

ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), '..'
    )
)
sys.path.append(ROOT)

import unittest
import html5witch

class HTML5WitchTestCase(unittest.TestCase):
    
    def expected_document(self, filename):
        expected = os.path.join(ROOT, 'tests',  'expected',  filename)
        with open(expected) as document:
            return document.read()
            
    def test_simple_document(self):
        doc = html5witch.Builder()
        with doc.html:
            with doc.head:
                doc.title('Title')
            with doc.body:
                doc.p('Hello World')
            with doc.form(action="/", method="post"):
                doc.input(None, type="input", name="my_input_field")
        self.assertEquals(
            str(doc), 
            self.expected_document('simple_document.html')
        )
        
    def test_script_elements(self):
        doc = html5witch.Builder()
        with doc.html:
            with doc.head:
                doc.script(None, 
                    src = 'http://example.org/js/foo.js',
                    type = 'text/javascript'
                )
                with doc.scripts as src:
                    src('http://example.org/js/bar.js', type='text/javascript')
                    src('http://example.org/js/baz.js', type='text/javascript')
        self.assertEquals(
            str(doc), 
            self.expected_document('script_elements.html')
        )

    def test_link_elements(self):
        doc = html5witch.Builder()
        with doc.html:
            with doc.head:
                doc.link(None, 
                    href = 'http://example.org/feed.xml',
                    rel = 'alternate', type = 'application/atom+xml'
                )
                with doc.links as href:
                    href('http://example.org/css/foo.css', rel='stylesheet')
                    href('http://example.org/css/bar.css', rel='stylesheet')
        self.assertEquals(
            str(doc), 
            self.expected_document('link_elements.html')
        )

if __name__ == '__main__':
    unittest.main()