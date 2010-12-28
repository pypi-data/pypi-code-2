import unittest

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from zope.interface import implements, Interface
from zope.component import getUtility, getMultiAdapter

from zope.component.interfaces import IObjectEvent

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleCondition
from plone.contentrules.rule.interfaces import IExecutable

from plone.app.contentrules.rule import Rule

import collective.contentrules.tagcondition

from collective.contentrules.tagcondition.tagcondition import HTMLTagCondition
from collective.contentrules.tagcondition.tagcondition import HTMLTagEditForm

ptc.setupPloneSite()

class DummyEvent(object):
    implements(IObjectEvent)
    
    def __init__(self, obj):
        self.object = obj

# Since we do not need to quick-install anything or register a Zope 2 style
# product, we can use a simple layer that's set up after the Plone site has 
# been created above

class TestHTMLTagCondition(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.contentrules.tagcondition)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

    def afterSetUp(self):
        self.setRoles(('Manager',))
        
    def testRegistered(self): 
        element = getUtility(IRuleCondition, name='collective.contentrules.tagcondition.Tag')
        self.assertEquals('collective.contentrules.tagcondition.Tag', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(IObjectEvent, element.event)
    
    def testInvokeAddView(self): 
        element = getUtility(IRuleCondition, name='collective.contentrules.tagcondition.Tag')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')
        
        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+condition')
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)
        
        addview.createAndAdd(data={'tags' : ['style', 'script']})
        
        e = rule.conditions[0]
        self.failUnless(isinstance(e, HTMLTagCondition))
        self.assertEquals(['style', 'script'], e.tags)
    
    def testInvokeEditView(self): 
        element = getUtility(IRuleCondition, name='collective.contentrules.tagcondition.Tag')
        e = HTMLTagCondition()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.failUnless(isinstance(editview, HTMLTagEditForm))

    def testExecute(self): 
        e = HTMLTagCondition()
        e.tags = ['div', 'span', 'style']
        
        self.folder.invokeFactory('Document', 'd1')
        self.folder.d1.setText('<div><span>hello</span> world!</div>')
        
        self.folder.invokeFactory('Document', 'd2')
        self.folder.d2.setText('<p>Hello World!</p>')
        
        ex = getMultiAdapter((self.portal, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEquals(True, ex())
        
        ex = getMultiAdapter((self.portal, e, DummyEvent(self.folder.d2)), IExecutable)
        self.assertEquals(False, ex())

def test_suite():
    return unittest.TestSuite([
            unittest.makeSuite(TestHTMLTagCondition)
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')