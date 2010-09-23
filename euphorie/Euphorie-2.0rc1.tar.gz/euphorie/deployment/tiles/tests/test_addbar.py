from euphorie.deployment.tests.functional import EuphorieTestCase

class AddBarTileTests(EuphorieTestCase):
    def _create(self, container, *args, **kwargs):
        newid=container.invokeFactory(*args, **kwargs)
        return getattr(container, newid)

    def createSurvey(self):
        country=self.portal.sectors.nl
        sector=self._create(country, "euphorie.sector", "sector")
        surveygroup=self._create(sector, "euphorie.surveygroup", "group")
        survey=self._create(surveygroup, "euphorie.survey", "survey")
        return survey

    def tile(self, context):
        from euphorie.deployment.tiles.addbar import AddBarTile
        return AddBarTile(context, self.portal.REQUEST)

    def testModuleNameOutsideModule(self):
        self.loginAsPortalOwner()
        survey=self.createSurvey()
        tile=self.tile(survey)
        tile.update()
        action=filter(lambda fti: fti.id=="euphorie.module", tile.actions)[0]
        self.assertEqual(action.title, u"Module")

    def testModuleNameInsideModule(self):
        self.loginAsPortalOwner()
        survey=self.createSurvey()
        module=self._create(survey, "euphorie.module", "module")
        tile=self.tile(module)
        tile.update()
        action=filter(lambda fti: fti.id=="euphorie.module", tile.actions)[0]
        self.assertEqual(action.title, u"Submodule")

