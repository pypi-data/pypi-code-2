from Acquisition import aq_base
from Products.CMFPlone.utils import getToolByName
from Products.Five.component import LocalSiteHook, HOOK_NAME
from Products.SiteAccess.AccessRule import AccessRule
from ZPublisher.BeforeTraverse import registerBeforeTraverse
from zope.component import getUtility
from zope.publisher.browser import BrowserView

try:
    # Try import that works in Zope 2.13 or higher first
    from zope.browsermenu.interfaces import IBrowserMenu
except ImportError:
    # BBB for Zope 2.12 or lower
    from zope.app.publisher.interfaces.browser import IBrowserMenu

from collective.editskinswitcher import SwitcherMessageFactory as _
from collective.editskinswitcher.skin import set_selected_default_skin


class SelectSkin(BrowserView):

    def update(self):
        """Set selected skin as the default for the current folder."""
        # Check to see if the current object already has a
        # LocalSiteHook from Five registered. If not, then register
        # one ourselves, going around ``enableSite`` since we don't
        # want to make this object a full ``ISite``, but just get the
        # ``BeforeTraverseEvent`` fired.
        obj = aq_base(self.context)
        if not hasattr(obj, HOOK_NAME):
            hook = AccessRule(HOOK_NAME)
            registerBeforeTraverse(obj, hook, HOOK_NAME, 1)
            setattr(obj, HOOK_NAME, LocalSiteHook())

        set_selected_default_skin(
            self.context, self.request.form.get("skin_name", None))

        utils = getToolByName(self.context, "plone_utils")
        utils.addPortalMessage(_(u"Skin changed."))
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def menuItems(self):
        """Return the menu items for the skin switcher."""
        menu = getUtility(
            IBrowserMenu, name="collective-editskinswitcher-menu-skins",
            context=self.context)
        return menu.getMenuItems(self.context, self.request)
