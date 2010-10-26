from unittest import defaultTestLoader

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup

from OFS.interfaces import IObjectManager

from zope.interface import implements
from zope.component import getUtility, getMultiAdapter

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.interfaces import IExecutable

from collective.contentrules.template.action import CopyFromTemplateAction
from collective.contentrules.template.action import CopyFromTemplateEditForm

from plone.app.contentrules.rule import Rule

from zope.component.interfaces import IObjectEvent

from Products.PloneTestCase.setup import default_user, portal_owner

@onsetup
def setupPackage():
    fiveconfigure.debug_mode = True
    import collective.contentrules.template
    zcml.load_config('configure.zcml', collective.contentrules.template)
    fiveconfigure.debug_mode = False

setupPackage()
PloneTestCase.setupPloneSite()

class DummyEvent(object):
    implements(IObjectEvent)
    
    def __init__(self, object):
        self.object = object

class TestCopyFromTemplateRule(PloneTestCase.PloneTestCase):
    
    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Document', 'd1')
        self.portal.d1.setTitle("Source document")
        self.portal.invokeFactory('Folder', 'target2')

        self.login(default_user)
        self.folder.invokeFactory('Folder', 'target')

        self.folder.invokeFactory('Folder', 'sourcefolder')
        self.folder.sourcefolder.setTitle("Source Folder")
        self.folder.sourcefolder.invokeFactory('Document', 'd2')
        self.folder.sourcefolder.d2.setTitle("Source document too")


    def testRegistered(self): 
        element = getUtility(IRuleAction, name='collective.contentrules.template.CopyFromTemplate')
        self.assertEquals('collective.contentrules.template.CopyFromTemplate', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(IObjectManager, element.for_)
        self.assertEquals(IObjectEvent, element.event)
    
    def testInvokeAddView(self): 
        element = getUtility(IRuleAction, name='collective.contentrules.template.CopyFromTemplate')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')
        
        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)
        
        addview.createAndAdd(data={'source_object' : '/d1', 'change_ownership': False})
        
        e = rule.actions[0]
        self.failUnless(isinstance(e, CopyFromTemplateAction))
        self.assertEquals('/d1', e.source_object)
        self.assertEquals(False, e.change_ownership)
    
    def testInvokeEditView(self): 
        element = getUtility(IRuleAction, name='collective.contentrules.template.CopyFromTemplate')
        e = CopyFromTemplateAction()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.failUnless(isinstance(editview, CopyFromTemplateEditForm))

    def testExecuteWithRetainOwnership(self): 
        e = CopyFromTemplateAction()
        e.source_object = '/d1'
        e.change_ownership = False
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.target)), IExecutable)
        self.assertEquals(True, ex())
        
        self.failUnless('d1' in self.folder.target.objectIds())
        self.failUnless('d1' in self.portal.objectIds())
        self.assertEquals("Source document", self.folder.target.d1.Title())
        self.assertEquals(portal_owner, self.folder.target.d1.getOwnerTuple()[1])
    
    def testExecuteWithChangeOwnership(self):
        e = CopyFromTemplateAction()
        e.source_object = '/d1'
        e.change_ownership = True
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.target)), IExecutable)
        self.assertEquals(True, ex())
        
        self.failUnless('d1' in self.folder.target.objectIds())
        self.failUnless('d1' in self.portal.objectIds())
        self.assertEquals("Source document", self.folder.target.d1.Title())
        self.assertEquals(default_user, self.folder.target.d1.getOwnerTuple()[1])
    
    def testExecuteRetainsWorkflowState(self): 
        self.setRoles(('Manager',))
        self.portal.portal_workflow.doActionFor(self.portal.d1, 'publish')
        self.setRoles(('Member',))
        
        e = CopyFromTemplateAction()
        e.source_object = '/d1'
        e.change_ownership = True
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.target)), IExecutable)
        self.assertEquals(True, ex())
        
        self.failUnless('d1' in self.folder.target.objectIds())
        self.failUnless('d1' in self.portal.objectIds())
        self.assertEquals("Source document", self.folder.target.d1.Title())
        self.assertEquals(default_user, self.folder.target.d1.getOwnerTuple()[1])
        
        self.assertEquals('published', self.portal.portal_workflow.getInfoFor(self.portal.d1, 'review_state'))
        self.assertEquals('published', self.portal.portal_workflow.getInfoFor(self.folder.target.d1, 'review_state'))
    
    def testExecuteWithError(self): 
       e = CopyFromTemplateAction()
       e.source_object = '/dummy'
       e.change_ownership = False
       
       ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.target)), IExecutable)
       self.assertEquals(False, ex())
       
       self.failUnless('d1' in self.portal.objectIds())
       self.failIf('d1' in self.folder.target.objectIds())

    def testExecuteWithoutPermissionsOnTarget(self):
        self.setRoles(('Authenticated',))
        
        e = CopyFromTemplateAction()
        e.source_object = '/d1'
        e.change_ownership = True
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.portal.target2)), IExecutable)
        self.assertEquals(True, ex())
        
        self.failUnless('d1' in self.portal.target2.objectIds())
        self.failUnless('d1' in self.portal.objectIds())

    def testExecuteWithNamingConflict(self):
        self.folder.target.invokeFactory('Document', 'd1')
        
        e = CopyFromTemplateAction()
        e.source_object = '/d1'
        e.change_ownership = False
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.target)), IExecutable)
        self.assertEquals(True, ex())
        
        self.failUnless('d1' in self.folder.target.objectIds())
        self.failUnless('d1' in self.portal.objectIds())
        self.failUnless('d1.1' in self.folder.target.objectIds())
        
        self.assertEquals("Source document", self.folder.target['d1.1'].Title())

    def testExecuteWithCopyChildren(self):
        e = CopyFromTemplateAction()
        e.source_object = '/Members/%s/sourcefolder' % self.folder.id
        e.copy_children = True
        
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.target)), IExecutable)
        self.assertEquals([True], ex())
        
        self.failUnless('d2' in self.folder.target.objectIds())
        self.failUnless('d2' in self.folder.sourcefolder.objectIds())
        self.assertEquals("Source document too", self.folder.target.d2.Title())
    
    
def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)
