import sys

from io import StringIO
from os.path import (dirname, abspath)
from unittest import TestCase
from test import support

sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))
from tenpy import etree


class TenpyEtreeTest(TestCase):

    def setUp(self):
        self.xml = '<xml>'\
                     'before'\
                     '<div id="first"><inner id="inner_id">inner_content</inner></div>\n'\
                     '<div id="second">second_content</div>\n'\
                     '<span id="test">content1</span>'\
                     'after'\
                     '<!-- comment -->'\
                     '<span class="cls" id="test">content2</span>'\
                     '<tail></tail>'\
                   '</xml>\n'
        self.target = etree.XML(self.xml)

    def test_tostring(self):
        xml = etree.tostring(self.target)
        self.assertEqual(xml, self.xml)


def test_main():
    support.run_unittest(TenpyEtreeTest)

if __name__ == "__main__":
    test_main()
