import unittest
import doctest
from Testing import ZopeTestCase as ztc
from Products.PFGVerkkomaksut.tests import base
from Products.CMFCore.utils import getToolByName

class TestSetup(base.PFGVerkkomaksutFunctionalTestCase):

    def afterSetUp( self ):
        """After SetUp"""
        self.setRoles(('Manager',))
        ## Set up sessioning objects
        ztc.utils.setupCoreSessions(self.app)
#        setup_tool = getToolByName(self.portal, 'portal_setup')
#        setup_tool.runAllImportStepsFromProfile(
#                    "profile-Products.PloneFormGen:default",
#                    purge_old=False)

        portal = self.portal
        ## Tools
        wftool = getToolByName(portal, 'portal_workflow')
        ## Create Form Folder
        portal.invokeFactory(
            'FormFolder',
            'form',
            title="Form Folder",
        )
        form = portal.form
        wftool.doActionFor(form, "publish")
        ## Add FormFixedPointField
        form.invokeFactory(
            'FormFixedPointField',
            'fixed_point_field',
            title = 'Fixed Point Price',
            required = True,
        )
#        fpf = form.fixed_point_field
#        fpf_uid = fpf.UID()
        form.invokeFactory(
            'FormSelectionField',
            'selection_field',
            title = 'Selection Price',
            required = False,
        )
#        sf = form.selection_field
#        form.invokeFactory(
#            'FormMultiSelectionField',
#            'multi_selection_field',
#            title = 'Multi Selection',
#            required = False,
#            fgVocabulary = 'aaa|AAA\nbbb|BBB\nccc|CCC',
#        )


def test_suite():
    return unittest.TestSuite([

        ztc.FunctionalDocFileSuite(
            'tests/functional/content_types_functional.txt',
            package='Products.PFGVerkkomaksut',
            test_class=TestSetup,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

            ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
