"""
Automated tests.

This is mostly copy & paste from
http://plone.org/documentation/kb/creating-content-rule-conditions-and-actions/tutorial-all-pages

Daniel Holth <daniel.holth@exac.com>
"""

import unittest
import LinguaPlus

from zope.component import getUtility

from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.Five import fiveconfigure, zcml
from plone.contentrules.rule.interfaces import IRuleEventType
import Products.LinguaPlone
import plone.app.iterate
from zope.component.interfaces import IObjectEvent
from zope.interface import implements
from LinguaPlus.outdate import OutdateActionExecutor, OutdateAction,\
    Outdater
from plone.app.iterate.event import BeforeCheckoutEvent, CheckoutEvent,\
    CheckinEvent, AfterCheckinEvent

ptc.setupPloneSite()

class DummyEvent(object):
    implements(IObjectEvent)
    
    def __init__(self, obj):
        self.object = obj

class SisypheanTest(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             Products.LinguaPlone)
            zcml.load_config('configure.zcml',
                             plone.app.iterate)
            zcml.load_config('configure.zcml',
                             LinguaPlus)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

    def afterSetUp(self):
        self.setRoles(('Manager',))        
        self.portal.portal_setup.runAllImportStepsFromProfile(
            'profile-plone.app.iterate:plone.app.iterate')
        
    def testRegistered(self):
        # Why bother asserting the ZCML does what it says it does? 
        element = getUtility(IRuleEventType, name='A working copy will be checked in.')
        assert element
        
    def testExecute(self):
        """Assert OutdateAction marks translations as outdated."""
        self.folder.invokeFactory('Document', 'd1')
        self.folder.d1.setSubject(['Bar'])
        es = self.folder.d1.addTranslation('es')

        self.assertFalse(Outdater(self.folder.d1).outdated)
        self.assertFalse(Outdater(es).outdated)
        
        executor = OutdateActionExecutor(self.portal, OutdateAction(), DummyEvent(self.folder.d1))        
        self.assertTrue(executor())
                
        # canonical is not marked as outdated
        self.assertFalse(Outdater(self.folder.d1).outdated)
        # but the translation is marked as outdated
        self.assertTrue(Outdater(es).outdated)
        
    def testEvents(self):
        """Assert our new checkin/checkout listeners are listening."""
        events = []
        def appender(event):
            events.append(event)
        execute_rules = LinguaPlus.handlers.execute_rules
        try:
            LinguaPlus.handlers.execute_rules = appender     
            self.folder.invokeFactory('Document', 'd2')
            self.folder.d2.setSubject(['Bar'])
            working_copy = ICheckinCheckoutPolicy(self.folder.d2).checkout(self.folder)
            ICheckinCheckoutPolicy(working_copy).checkin("Automated Test")
            assert len(events) == 4, events
            b, co, ci, aci = events
            assert isinstance(b, BeforeCheckoutEvent)
            assert isinstance(co, CheckoutEvent)
            assert isinstance(ci, CheckinEvent)
            assert isinstance(aci, AfterCheckinEvent)
        finally:
            LinguaPlus.handlers.execute_rules = execute_rules
        

def test_suite():
    return unittest.TestSuite([
            unittest.makeSuite(SisypheanTest)
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

