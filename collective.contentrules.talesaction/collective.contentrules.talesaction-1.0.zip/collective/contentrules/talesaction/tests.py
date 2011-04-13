import unittest

from zope.testing import doctestunit
from zope.component import testing, getUtility, getMultiAdapter
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

import collective.contentrules.talesaction

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.contentrules.talesaction)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

from zope.interface import implements

from zope.component.interfaces import IObjectEvent
from zope.component import getUtility, getMultiAdapter

from Products.PloneTestCase.setup import default_user
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.interfaces import IExecutable
from plone.app.contentrules.rule import Rule

from collective.contentrules.talesaction.action import (
    TalesExpressionAction, TalesExpressionEditForm)

class DummyEvent(object):
    implements(IObjectEvent)

    def __init__(self, object):
        self.object = object

class TestTalesExpressionAction(TestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Folder', 'target')
        self.login(default_user)
        self.folder.invokeFactory('Document', 'd1')

    def testRegistered(self):
        element = getUtility(IRuleAction, name='plone.actions.TalesExpression')
        self.assertEquals('plone.actions.TalesExpression', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(IObjectEvent, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction, name='plone.actions.TalesExpression')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)

        addview.createAndAdd(data={
                'tales_expression' : 'python:object.setContributors(object.Contributors() + (member.getId(),))'})

        e = rule.actions[0]
        self.failUnless(isinstance(e, TalesExpressionAction))
        self.assertEquals('python:object.setContributors(object.Contributors() + (member.getId(),))', e.tales_expression)

    def testInvokeEditView(self):
        element = getUtility(IRuleAction, name='plone.actions.TalesExpression')
        e = TalesExpressionAction()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.failUnless(isinstance(editview, TalesExpressionEditForm))

    def testExecute(self):
        e = TalesExpressionAction()
        e.target_folder = '/target'

        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEquals(True, ex())

        self.failUnless('d1' in self.folder.objectIds())
        self.failUnless('d1' in self.portal.target.objectIds())

    def testExecute(self):
        e = TalesExpressionAction()
        e.tales_expression = 'python:object.setContributors(object.Contributors() + (member.getId(),))'

        ex = getMultiAdapter((self.portal, e, DummyEvent(self.folder)), IExecutable)
        ex()
        self.assertEquals(self.folder.Contributors(), ('test_user_1_',))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTalesExpressionAction))
    return suite



if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
