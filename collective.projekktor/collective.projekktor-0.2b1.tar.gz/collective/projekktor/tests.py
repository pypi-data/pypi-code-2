"""Test setup for integration and functional tests."""
import unittest
import os.path, sys

from zope.component import getUtility, getMultiAdapter
from zope.app.component.hooks import setHooks, setSite
        
from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping, IPortletRenderer


DOC_TESTS = ('adapter_media','adapter_view_provider','adapter_portlet_provider','utility','browser_views','browser_portlets','browser_controls','exportimport')

@onsetup
def setup_product():
    """Set up the package and its dependencies."""
    
    fiveconfigure.debug_mode = True
    import collective.projekktor
    zcml.load_config('configure.zcml', collective.projekktor)
    fiveconfigure.debug_mode = False
    ztc.installProduct('collective.projekktor')

setup_product()
ptc.setupPloneSite(products=['collective.projekktor'],extension_profiles=['collective.projekktor.profiles:default'])


class ProjekktorFunctionalTestCase(ptc.FunctionalTestCase):

    def thisDir(self,file,name):
        if name == '__main__': filename = sys.argv[0]
        else: filename = file
        return os.path.abspath(os.path.dirname(filename))        

    def afterSetUp(self):
        filetypes = ['ogg','ogv','mp3','mp4']
        testDir = '%s/doctests' %self.thisDir(__file__,__name__)

        setHooks()
        setSite(self.portal)
        self.setRoles(['Manager'])

        sample_folder = self.portal.invokeFactory("Folder", "samples")        
        self.sample_folder = self.portal[sample_folder]

        self.samples = {}
        for filetype in filetypes:
            sample = self.sample_folder.invokeFactory("File","projekktor.%s"%filetype)
            self.samples[filetype] = self.sample_folder[sample]
            self.samples[filetype].setFile(open('%s/projekktor.%s'%(testDir,filetype),'r'))
            self.samples[filetype].setTitle('An example %s' %filetype)
            self.samples[filetype].setDescription('An %s file to use for testing purposes' %filetype)

        png_id = 'projekktor.png'
        self.sample_folder.invokeFactory('Image', id=png_id)
        self.sample_folder[png_id].setImage(open('%s/projekktor.png'%testDir,'r'))
       
        self.setRoles([])

    def portletRenderer(self, context, assignment):
        request = context.REQUEST
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)


def test_suite():
    """This sets up a test suite that actually runs the tests"""
    suite = unittest.TestSuite()

    suite.addTests(
        [ztc.ZopeDocFileSuite(
                'doctests/%s.txt' % f
                , package='collective.projekktor'
                , test_class=ProjekktorFunctionalTestCase )
         for f in DOC_TESTS],
        )
    return suite

