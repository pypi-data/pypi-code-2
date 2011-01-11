import os
from Testing.ZopeTestCase import app, close
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import setSite, setHooks
from transaction import commit
from collective.megaphone.tests.layer import MegaphoneLayer, zcml, metaconfigure


class MegaphoneCiceroLayer(MegaphoneLayer):
    
    @classmethod
    def setUp(cls):
        metaconfigure.debug_mode = True
        import collective.megaphonecicerolookup
        zcml.load_config('configure.zcml', collective.megaphonecicerolookup)
        metaconfigure.debug_mode = False

        root = app()
        portal = root.plone
        
        # import profile
        setHooks()
        setSite(portal)
        tool = getToolByName(portal, 'portal_setup')
        tool.runAllImportStepsFromProfile('profile-collective.megaphonecicerolookup:default', purge_old=False)

        # put in test mode
        os.environ['CICERO_TEST'] = '1'

        # and commit the changes
        setSite(None)
        commit()
        close(root)


    @classmethod
    def tearDown(cls):
        pass
