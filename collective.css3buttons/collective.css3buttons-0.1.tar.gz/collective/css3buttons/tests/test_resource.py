from unittest import TestSuite, makeSuite
from zope.component import getAdapter
from zope.publisher.browser import TestRequest

from collective.css3buttons.tests import base


class ResourceTestCase(base.TestCase):

    def test_0010_resources(self):
        needed_resources = [
            'images/css3buttons_backgrounds.png',
            'images/css3buttons_icons.png',
            'stylesheets/css3buttons.css',
        ]
        request = TestRequest()
        res = getAdapter(request, name='collective.css3buttons.resources')
        for i in needed_resources:
            self.assertNotEqual(res.get(i, None), None, '`%s` is missing.' % i)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(ResourceTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
