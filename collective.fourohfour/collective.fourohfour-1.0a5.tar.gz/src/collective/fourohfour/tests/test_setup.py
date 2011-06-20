import unittest

from Products.PloneTestCase.ptc import PloneTestCase
from collective.fourohfour.tests.layer import Layer

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from collective.fourohfour.interfaces import IFourOhFourSettings
from collective.fourohfour.interfaces import IBrowserLayer

class TestSetup(PloneTestCase):
    
    layer = Layer
    
    def test_registry_records_installed(self):
        reg = getUtility(IRegistry)
        records = reg.forInterface(IFourOhFourSettings)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)