from zope.interface import implements, Interface
from zope.component import getUtility, getMultiAdapter
from OFS.interfaces import IObjectManager
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.interfaces import IExecutable

from sc.contentrules.movebyattribute.interfaces import InvalidAttribute
from sc.contentrules.movebyattribute.action import MoveByAttributeAction
from sc.contentrules.movebyattribute.action import MoveByAttributeEditForm

from plone.app.contentrules.rule import Rule

from sc.contentrules.movebyattribute.tests.base import TestCase

from zope.component.interfaces import IObjectEvent

from Products.PloneTestCase.setup import default_user

from DateTime import DateTime

class DummyEvent(object):
    implements(IObjectEvent)
    
    def __init__(self, object):
        self.object = object

class TestMoveByAttributeAction(TestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Folder', 'target')
        self.portal.target.invokeFactory('Folder', default_user)
        self.login(default_user)
        self.folder.invokeFactory('Document', 'd1')
        self.folder.d1.getField('creators').set(self.folder.d1, (default_user,))

    def testRegistered(self): 
        element = getUtility(IRuleAction, name='sc.contentrules.movebyattribute.MoveByAttribute')
        self.assertEquals('sc.contentrules.movebyattribute.MoveByAttribute', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(IObjectManager, element.for_)
        self.assertEquals(IObjectEvent, element.event)
    
    def testInvokeAddView(self): 
        element = getUtility(IRuleAction, name='sc.contentrules.movebyattribute.MoveByAttribute')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')
        
        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)
        
        addview.createAndAdd(data={'base_folder' : '/target','attribute':'Creator'})
        
        e = rule.actions[0]
        self.failUnless(isinstance(e, MoveByAttributeAction))
        self.assertEquals('/target', e.base_folder)

    def testValidateAttributeName(self): 
        element = getUtility(IRuleAction, name='sc.contentrules.movebyattribute.MoveByAttribute')
        e=MoveByAttributeAction()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        field =  editview.form_fields.get('attribute').field
        
        self.assertRaises(InvalidAttribute,field.validate,u'__init__')
        self.assertRaises(InvalidAttribute,field.validate,u'__call__')
        self.assertRaises(InvalidAttribute,field.validate,u'foo.bar')
        self.assertRaises(InvalidAttribute,field.validate,u'.foobar')
        self.assertRaises(InvalidAttribute,field.validate,u'Creator()')
        self.assertEqual(field.validate(u'Creator'),None)
        
    
    def testInvokeEditView(self): 
        element = getUtility(IRuleAction, name='sc.contentrules.movebyattribute.MoveByAttribute')
        e = MoveByAttributeAction()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.failUnless(isinstance(editview, MoveByAttributeEditForm))

    def testExecute(self): 
        e = MoveByAttributeAction()
        e.base_folder = '/target'
        e.attribute = 'Creator'
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEquals(True, ex())
        
        self.failIf('d1' in self.folder.objectIds())
        target_folder = self.portal.unrestrictedTraverse('%s/%s' % (e.base_folder[1:],default_user))
        self.failUnless('d1' in target_folder.objectIds())
        
    def testExecuteWithError(self): 
        e = MoveByAttributeAction()
        e.base_folder = '/dummy'
        e.attribute = 'Creator'
                
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEquals(False, ex())
        
        self.failUnless('d1' in self.folder.objectIds())
        self.failIf('d1' in self.portal.target.objectIds())
        
    def testExecuteWithoutPermissionsOnTarget(self):
        self.setRoles(('Member',))
        
        e = MoveByAttributeAction()
        e.base_folder = '/target'
        e.attribute = 'Creator'
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEquals(True, ex())
        
        self.failIf('d1' in self.folder.objectIds())
        target_folder = self.portal.unrestrictedTraverse('%s/%s' % (e.base_folder[1:],default_user))
        self.failUnless('d1' in target_folder.objectIds())
        
    

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMoveByAttributeAction))
    return suite
