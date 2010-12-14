from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from plone.memoize.instance import memoize
from zope.component import getMultiAdapter
from zope.interface import implements

try:
    # Try import that works in Zope 2.13 or higher first
    from zope.browsermenu.menu import BrowserMenu
    from zope.browsermenu.menu import BrowserSubMenuItem
except ImportError:
    # BBB for Zope 2.12 or lower
    from zope.app.publisher.browser.menu import BrowserMenu
    from zope.app.publisher.browser.menu import BrowserSubMenuItem

from collective.editskinswitcher import SwitcherMessageFactory as _
from collective.editskinswitcher.browser.interfaces import (
    ISkinsSubMenuItem, ISkinsMenu)
from collective.editskinswitcher.permissions import SetDefaultSkin
from collective.editskinswitcher.skin import get_selected_default_skin


class SkinsSubMenuItem(BrowserSubMenuItem):

    implements(ISkinsSubMenuItem)
    submenuId = "collective-editskinswitcher-menu-skins"
    title = _(u"Skins")
    description = _(u"Change skin for the current content item")
    extra = {'id': 'collective-editskinswitcher-menu-skins'}

    order = 11

    def __init__(self, context, request):
        BrowserSubMenuItem.__init__(self, context, request)
        self.tools = getMultiAdapter((context, request), name='plone_tools')
        self.context_state = getMultiAdapter((context, request),
                                             name='plone_context_state')

    @property
    def action(self):
        folder = self.context
        if not self.context_state.is_structural_folder():
            folder = utils.parent(self.context)
        return folder.absolute_url() + '/select_skin'

    @memoize
    def available(self):
        if not self._manageSkinSettings():
            return False

        # Only allow this menu on folders.
        if not (self.context_state.is_structural_folder()
                or self.context_state.is_default_page()):
            return False

        # Check if our property sheet is available.  When not, then
        # this might be a second Plone site in the same Zope instance.
        # If we are not installed in this Plone Site, we do not want
        # to offer this menu item.
        if not self.tools.properties().get('editskin_switcher'):
            return False

        skins_tool = getToolByName(self.context, 'portal_skins')
        if len(skins_tool.getSkinSelections()) < 2:
            # Nothing to choose.
            return False
        return True

    @memoize
    def _manageSkinSettings(self):
        return self.tools.membership().checkPermission(
            SetDefaultSkin, self.context)

    def selected(self):
        return False


class SkinsMenu(BrowserMenu):
    implements(ISkinsMenu)

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        results = []

        skins_tool = getToolByName(context, "portal_skins")
        context_state = getMultiAdapter((context, request),
                                        name='plone_context_state')
        folder = context
        if not context_state.is_structural_folder():
            folder = utils.parent(context)
        url = folder.absolute_url()
        current_skin = get_selected_default_skin(folder)
        for skin in skins_tool.getSkinSelections():
            skin_id = utils.normalizeString(skin, folder, "utf-8")
            selected = skin == current_skin
            cssClass = selected and "actionMenuSelected" or "actionMenu"
            results.append(
                {"title": skin,
                 "description": _(u"Use '${skin}' skin for this folder",
                                  mapping=dict(skin=skin)),
                 "action": "%s/@@switchDefaultSkin?skin_name=%s" % (url, skin),
                 "selected": selected,
                 "extra": {
                     "id": "collective.editskinswitcher-skin-%s" % skin_id,
                     "separator": False,
                     "class": cssClass},
                 "submenu": None,
                 "icon": None,
                 })
        return results
