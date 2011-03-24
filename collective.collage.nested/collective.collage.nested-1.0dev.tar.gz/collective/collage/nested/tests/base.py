"""Test setup for integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of
Plone's products are loaded, and a Plone site will be created. This
happens at module level, which makes it faster to run each test, but
slows down test runner startup.
"""

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from Products.CMFCore.utils import getToolByName

from Products.Collage.interfaces import IDynamicViewManager


import os
from App import Common

# When ZopeTestCase configures Zope, it will *not* auto-load products
# in Products/. Instead, we have to use a statement such as:
#   ztc.installProduct('SimpleAttachment')
# This does *not* apply to products in eggs and Python packages (i.e.
# not in the Products.*) namespace. For that, see below.
# All of Plone's products are already set up by PloneTestCase.

@onsetup
def setup_product():
    """Set up the package and its dependencies.

    The @onsetup decorator causes the execution of this body to be
    deferred until the setup of the Plone site testing layer. We could
    have created our own layer, but this is the easiest way for Plone
    integration tests.
    """

    # Load the ZCML configuration for the example.tests package.
    # This can of course use <include /> to include other packages.

    fiveconfigure.debug_mode = True
    import collective.collage.nested
    zcml.load_config('configure.zcml', collective.collage.nested)
    fiveconfigure.debug_mode = False

    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML. Thus, we do it here. Note the use of installPackage()
    # instead of installProduct().
    # This is *only* necessary for packages outside the Products.*
    # namespace which are also declared as Zope 2 products, using
    # <five:registerPackage /> in ZCML.

    # We may also need to load dependencies, e.g.:
    #   ztc.installPackage('borg.localrole')

    ztc.installPackage('collective.collage.nested')

# The order here is important: We first call the (deferred) function
# which installs the products we need for this product. Then, we let
# PloneTestCase set up this product on installation.

setup_product()
ptc.setupPloneSite(products=['collective.collage.nested'])

class TestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If
    necessary, we can put common utility or setup code in here. This
    applies to unit test cases.
    """

from OFS.interfaces import IFolder
class ISpecialFolder(IFolder):
    pass

class FunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use
    doctest syntax. Again, we can put basic common utility or setup
    code in here.
    """

    def afterSetUp(self):
        roles = ('Member', 'Contributor')
        self.portal.portal_membership.addMember('contributor',
                                                'secret',
                                                roles, [])
                                                
class FunctionalTestCaseWithContent(FunctionalTestCase):

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        FunctionalTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()


    def afterSetUp(self):
        super(FunctionalTestCase, self).afterSetUp()
        self.loginAsPortalOwner()
        wtool = getToolByName(self.portal, 'portal_workflow')

        # News item without image
        _ = self.portal.invokeFactory('News Item', 'news-item')
        ob = getattr(self.portal, _)
        ob.setTitle('Test News item')
        ob.setExcludeFromNav(True)
        wtool.doActionFor(ob, 'publish')
        ni = ob
             
        # Page (Document)
        _ = self.portal.invokeFactory('Document', 'doc')
        ob = getattr(self.portal, _)
        ob.setTitle('Test Document')
        ob.setExcludeFromNav(True)
        wtool.doActionFor(ob, 'publish')
        doc = ob

        # Pre-build an inner (nested) Collage with 2 aliases for
        # each of the just created objects
        _ = self.portal.invokeFactory('Collage', 'inner-collage')
        collage = getattr(self.portal, _)
        collage.setTitle('Inner Collage')
        collage.setDescription('This is a nested Collage')
        collage.setExcludeFromNav(True)
        wtool.doActionFor(collage, 'publish')
        self.icollage = collage

        # Row
        _ = collage.invokeFactory('CollageRow', '1')
        row = getattr(collage, _)
        
        # Column and Alias for Page
        _ = row.invokeFactory('CollageColumn', '1')
        column = getattr(row, _)
        _ = column.invokeFactory('CollageAlias', 'alias-1')
        alias1 = getattr(column, _)
        alias1.set_target(doc.UID())
        manager = IDynamicViewManager(alias1)
        manager.setLayout('standard')

        # Column and Alias for News Item
        _ = row.invokeFactory('CollageColumn', '2')
        column = getattr(row, _)
        _ = column.invokeFactory('CollageAlias', 'alias-2')
        alias2 = getattr(column, _)
        alias2.set_target(ni.UID())
        manager = IDynamicViewManager(alias2)
        manager.setLayout('standard')  

        # Pre-build the outer Collage
        _ = self.portal.invokeFactory('Collage', 'outer-collage')
        collage = getattr(self.portal, _)
        collage.setTitle('Outer Collage')
        wtool.doActionFor(collage, 'publish')
        self.ocollage = collage

        # Row & Column
        _ = collage.invokeFactory('CollageRow', '1')
        row = getattr(collage, _)
        _ = row.invokeFactory('CollageColumn', '1')
#        column = getattr(row, _)

        # Alias for inner Collage
#       _ = column.invokeFactory('CollageAlias', 'alias')
#        alias = getattr(column, _)
#        alias.set_target(ni.UID())
