from euphorie.deployment.tests.functional import EuphorieTestCase


class SurveyGroupTests(EuphorieTestCase):
    def _create(self, container, *args, **kwargs):
        newid=container.invokeFactory(*args, **kwargs)
        return getattr(container, newid)

    def createSurveyGroup(self):
        country=self.portal.sectors.nl
        sector=self._create(country, "euphorie.sector", "sector")
        surveygroup=self._create(sector, "euphorie.surveygroup", "group")
        return surveygroup

    def testNoWorkflow(self):
        self.loginAsPortalOwner()
        surveygroup=self.createSurveyGroup()
        chain=self.folder.portal_workflow.getChainFor(surveygroup)
        self.assertEqual(chain, ())

    def testNotGloballyAllowed(self):
        self.loginAsPortalOwner()
        types=[fti.id for fti in self.portal.allowedContentTypes()]
        self.failUnless("euphorie.survey" not in types)

    def testAllowedContentTypes(self):
        self.loginAsPortalOwner()
        surveygroup=self.createSurveyGroup()
        types=[fti.id for fti in surveygroup.allowedContentTypes()]
        self.assertEqual(set(types), set(["euphorie.survey"]))

    def testCanNotBeCopied(self):
        self.loginAsPortalOwner()
        surveygroup=self.createSurveyGroup()
        self.assertFalse(surveygroup.cb_isCopyable())


class HandleSurveyPublishTests(EuphorieTestCase):
    def _create(self, container, *args, **kwargs):
        newid=container.invokeFactory(*args, **kwargs)
        return getattr(container, newid)

    def createSurveyGroup(self):
        country=self.portal.sectors.nl
        sector=self._create(country, "euphorie.sector", "sector")
        surveygroup=self._create(sector, "euphorie.surveygroup", "group")
        return surveygroup

    def testNothingPublished(self):
        self.loginAsPortalOwner()
        surveygroup=self.createSurveyGroup()
        self.assertEqual(surveygroup.published, None)

    def testUnknownWorkflowAction(self):
        from zope.event import notify
        from Products.CMFCore.WorkflowCore import ActionSucceededEvent
        self.loginAsPortalOwner()
        surveygroup=self.createSurveyGroup()
        survey=self._create(surveygroup, "euphorie.survey", "survey")
        notify(ActionSucceededEvent(survey, None, "bogus", None))
        self.assertEqual(surveygroup.published, None)

    def testPublishAction(self):
        from zope.event import notify
        from Products.CMFCore.WorkflowCore import ActionSucceededEvent
        self.loginAsPortalOwner()
        surveygroup=self.createSurveyGroup()
        survey=self._create(surveygroup, "euphorie.survey", "survey")
        notify(ActionSucceededEvent(survey, None, "publish", None))
        self.assertEqual(surveygroup.published, "survey")

    def testUpdateAction(self):
        from zope.event import notify
        from Products.CMFCore.WorkflowCore import ActionSucceededEvent
        self.loginAsPortalOwner()
        surveygroup=self.createSurveyGroup()
        survey=self._create(surveygroup, "euphorie.survey", "survey")
        notify(ActionSucceededEvent(survey, None, "update", None))
        self.assertEqual(surveygroup.published, "survey")


class AddFormTests(EuphorieTestCase):
    def _create(self, container, *args, **kwargs):
        newid=container.invokeFactory(*args, **kwargs)
        return getattr(container, newid)

    def createModule(self):
        country=self.portal.sectors.nl
        sector=self._create(country, "euphorie.sector", "sector")
        surveygroup=self._create(sector, "euphorie.surveygroup", "group")
        survey=self._create(surveygroup, "euphorie.survey", "survey")
        module=self._create(survey, "euphorie.module", "module")
        return module

    def testCopyPreservesOrder(self):
        from euphorie.content.surveygroup import AddForm
        original_order=[ u"one", u"two", u"three", u"four", u"five", u"six", u"seven", u"eight", u"nine", u"ten"]
        self.loginAsPortalOwner()
        module=self.createModule()
        for title in original_order:
            self._create(module, "euphorie.risk", title, title=title)
        self.assertEqual([r.title for r in module.values()], original_order)
        request=module.REQUEST
        container=module.aq_parent
        copy=self._create(container, "euphorie.module", "copy")
        copy=AddForm(container, request).copyTemplate(module, copy)
        self.assertEqual([r.title for r in copy.values()], original_order)

    def testReorderThenCopyTemplateKeepsOrder(self):
        from plone.folder.interfaces import IExplicitOrdering
        from euphorie.content.surveygroup import AddForm
        original_order=[ u"one", u"two", u"three", u"four", u"five", u"six", u"seven", u"eight", u"nine", u"ten"]
        sorted_order=list(sorted(original_order))
        self.loginAsPortalOwner()
        module=self.createModule()
        for title in original_order:
            self._create(module, "euphorie.risk", title, title=title)
        self.assertEqual([r.title for r in module.values()], original_order)
        ordering=IExplicitOrdering(module)
        ordering.orderObjects("title")
        self.assertEqual([r.title for r in module.values()], sorted_order)
        request=module.REQUEST
        container=module.aq_parent
        copy=self._create(container, "euphorie.module", "copy")
        copy=AddForm(container, request).copyTemplate(module, copy)
        self.assertEqual([r.title for r in copy.values()], sorted_order)

