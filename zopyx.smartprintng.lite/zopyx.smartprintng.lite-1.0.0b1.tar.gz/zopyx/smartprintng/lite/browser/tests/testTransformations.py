import unittest
import BeautifulSoup

from zopyx.smartprintng.plone.browser.transformation import TRANSFORMATIONS

class TransformationTests(unittest.TestCase):

    def transform(self, html, transformation, params=None):
        soup = BeautifulSoup.BeautifulSoup(html)
        method = TRANSFORMATIONS[transformation]
        method(soup, params)
        return soup.renderContents()

    def testNeutral(self):
        html = '<h1>hello world</h1>'
        self.assertEqual(self.transform(html, 'convertFootnotes'), html)


    def testToFootnotesURLandText(self):
        html = '<a href="http://plone.org">plone.org</a>'
        self.assertEqual(self.transform(html, 'convertFootnotes'),
                        '<span class="generated-footnote-text">plone.org<span class="generated-footnote"><a href="http://plone.org">http://plone.org</a></span></span>')

    def testToFootnotesURLandURL(self):
        html = '<a href="http://plone.org">http://plone.org</a>'
        self.assertEqual(self.transform(html, 'convertFootnotes'), html),



def test_suite():

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TransformationTests))
    return suite
