import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite(products=['collective.easyslider'])

import collective.easyslider

class TestCase(ptc.PloneTestCase):
    
    def click_with_data(self, link, data):
        labels = link.get_labels()
        if labels:
            label = labels[0].text
        else:
            label = None
        link.browser._start_timer()
        link.browser.mech_browser.open(form.click(
            id=control.id, name=control.name, label=label, coord=coord), data)
        link.browser._stop_timer()
        link.browser._changed()
    
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.easyslider)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='collective.easyslider',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='collective.easyslider.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='collective.easyslider',
        #    test_class=TestCase),

        ztc.FunctionalDocFileSuite(
            'browser.txt', package='collective.easyslider',
            test_class=TestCase),
        
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
