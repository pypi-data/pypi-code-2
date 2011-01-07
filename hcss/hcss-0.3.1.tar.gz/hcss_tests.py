from __future__ import with_statement

import sys
import os
import unittest
import hcss

def hcss_test(func):
    def test_wrapper(self):
        test_name = func.__name__[5:].replace('_', '-')
        hcss_parser = hcss.HCSSParser()
        with open('examples/%s/%s.hcss' % (test_name, test_name)) as hcss_file:
            hcss_parser.feed(hcss_file.read())
        generated_css = hcss_parser.css()
        with open('examples/%s/%s.css' % (test_name, test_name)) as css_file:
            css_file = css_file.read()
        self.assertEquals(css_file, generated_css)
    return test_wrapper

class HCSSTestCase(unittest.TestCase):
    
    def test_unredundantize_selector(self):        
        selector_tests = [
            ['foo', 'foo'],
            ['.foo', '.foo'],
            ['div.foo', 'div.foo'],
            ['div#foo > div.bar', 'div#foo > div.bar'],
            ['div#foo > div#bar > div.xyz', 'div#bar > div.xyz']
        ]
        hcss_parser = hcss.HCSSParser()
        for test in selector_tests:
            self.assertEquals(
                test[1],
                hcss_parser.unredundantize_selector(test[0])
            )

    @hcss_test
    def test_element_based_simple_rules():
        pass

    @hcss_test
    def test_element_based_complex_rules():
        pass
    
    @hcss_test  
    def test_inheritance():
        pass
    
    @hcss_test
    def test_standalone_and_element_based_rules():
        pass

if __name__ == '__main__':
    unittest.main()