"""Defines a base test case class to help testing viewlets
configurations.
"""

from zope.component import getAdapters, getUtility
from zope.component import queryMultiAdapter
from zope.viewlet.interfaces import IViewletManager, IViewlet

from plone.app.viewletmanager.interfaces import IViewletSettingsStorage

from Products.Five.browser import BrowserView
from Products.PloneTestCase import PloneTestCase as ptc

class TestCase(ptc.PloneTestCase):
    """Base test case with helper methods to test viewlets
    configurations.
    """

    def get_viewlet_manager(self, name):
        """Get a viewlet manager by name"""

        view = BrowserView(self.portal, self.portal.REQUEST)
        manager = queryMultiAdapter(
            (self.portal, self.portal.REQUEST, view),
            IViewletManager,
            name=name
        )
        return manager

    def is_viewlet_in_viewlet_manager(self, vname, vmname):
        """Checks if a vname is the name of a viewlet managed by the
        viewlet manager with name vname.
        """

        manager = self.get_viewlet_manager(vmname)

        viewlets = getAdapters(
            (manager.context, manager.request, manager.__parent__, manager),
            IViewlet
        )

        r = vname in [name for (name, viewlet) in viewlets]
        return r

    def list_ordered_viewlets(self, vmname):
        """A list of viewlet names in the order they are inside a given
        viewlet manager.
        """

        manager = self.get_viewlet_manager(vmname)
        storage = getUtility(IViewletSettingsStorage)
        skinname = self.portal.portal_skins.getDefaultSkin()
        return storage.getOrder(vmname, skinname)

    def is_hidden_viewlet(self, vname, vmname):
        """Checks if a viewlet is hidden"""

        manager = self.get_viewlet_manager(vmname)
        storage = getUtility(IViewletSettingsStorage)
        skinname = self.portal.portal_skins.getDefaultSkin()
        hidden = storage.getHidden(manager, skinname)
        return vname in hidden
