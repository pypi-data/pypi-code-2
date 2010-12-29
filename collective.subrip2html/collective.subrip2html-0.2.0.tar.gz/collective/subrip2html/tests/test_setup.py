# -*- coding: utf-8 -*-

import os
import unittest

#from zope.testing import doctestunit
#from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite(products=['collective.subrip2html'])

import collective.subrip2html
from pysrt import SubRipFile, SubRipTime

class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            ztc.installPackage(collective.subrip2html)
            fiveconfigure.debug_mode = False
            p = '/'.join(os.path.realpath( __file__ ).split(os.path.sep )[:-2])
            p = '%s/tests/test.srt' % p
            cls.test_srt_file = p

        @classmethod
        def tearDown(cls):
            pass


class TestSrt(TestCase):
    
    def test_registered(self):
        pt = self.portal.portal_transforms
        self.assertTrue(bool(pt.srt_to_html))
    
    def test_pysrt(self):
        test_srt = SubRipFile.open(self.layer.test_srt_file)
        self.assertEquals(test_srt[0].text, u'Eagle, say again.\nRepeat, please, Eagle.\n')
        self.assertEquals(test_srt[0].start, SubRipTime(0, 0, 13, 800))

    def test_transform(self):
        pt = self.portal.portal_transforms
        text = open(self.layer.test_srt_file).read()
        data = pt.convert('srt_to_html', text)
        html = data.getData()
        self.assertEquals(html, """<dl class="subripSection">
<dt>00:00:13,800 &rarr; 00:00:16,700</dt>
<dd>Eagle, say again.\nRepeat, please, Eagle.\n</dd>
<dt>00:00:18,600 &rarr; 00:00:20,800</dt>
<dd>Zero One Zero, can you confirm deployment?\n</dd>
<dt>00:00:20,900 &rarr; 00:00:22,800</dt>
<dd>Roger that, Eagle. Stand by.\n</dd>
</dl>\n""")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSrt))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
