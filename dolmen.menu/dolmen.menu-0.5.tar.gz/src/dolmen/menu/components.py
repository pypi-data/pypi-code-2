# -*- coding: utf-8 -*-

import grokcore.view
import grokcore.viewlet

from dolmen.menu.interfaces import IMenu, IMenuEntry, IMenuEntryViewlet
from grokcore.component import baseclass
from megrok.pagetemplate import IPageTemplate, PageTemplate, view
from zope.component import getAdapters, getMultiAdapter
from zope.interface import implements, Interface
from zope.schema.fieldproperty import FieldProperty
from zope.security import checkPermission
from zope.security.checker import CheckerPublic
from zope.traversing.browser.absoluteurl import absoluteURL


class Menu(grokcore.viewlet.ViewletManager):
    """Viewlet Manager working as a menu.
    """
    baseclass()
    implements(IMenu)
    viewlets = []

    entries = FieldProperty(IMenu['entries'])
    menu_class = FieldProperty(IMenu['menu_class'])
    entry_class = FieldProperty(IMenu['entry_class'])
    context_url = FieldProperty(IMenu['context_url'])
    menu_context = FieldProperty(IMenu['menu_context'])

    @property
    def id(self):
        return self.__name__.replace('.', '-')

    def setMenuContext(self, item):
        self.menu_context = item

    def getMenuContext(self):
        return self.menu_context or self.context

    def _updateViewlets(self):
        """Doesn't fire events, like the original ViewletManager, on purpose.
        """
        for viewlet in self.viewlets:
            if IMenuEntryViewlet.providedBy(viewlet):
                viewlet.update()

    def filter(self, viewlets):
        for name, viewlet in viewlets:
            permission = viewlet.permission
            if permission == 'zope.Public':
                # Translate public permission to CheckerPublic
                permission = CheckerPublic
            if checkPermission(permission, self.context):
                yield name, viewlet

    def render(self):
        template = getattr(self, 'template', None)
        if template is None:
            template = getMultiAdapter((self, self.request), IPageTemplate)
        return template()

    def update(self):
        self.__updated = True
        self.title = grokcore.view.title.bind(default=self.__name__).get(self)

        # We get the real context
        menu_context = self.getMenuContext()

        # Get the MenuContext and calculate its url
        self.context_url = absoluteURL(menu_context, self.request)
        
        # Find all content providers for the region
        viewlets = getAdapters(
            (menu_context, self.request, self.__parent__, self),
            IMenuEntry)

        viewlets = self.filter(viewlets)
        self.viewlets = [viewlet for name, viewlet in self.sort(viewlets)]
        self._updateViewlets()


class Entry(object):
    """Viewlet
    """
    baseclass()
    implements(IMenuEntryViewlet)
    grokcore.viewlet.context(Interface)

    def __init__(self, context, request, view, manager):
        self.view = self.__parent__ = view
        self.context = context
        self.request = request
        self.manager = manager
        self.__name__ = self.__view_name__

    def __repr__(self):
        return  "<MenuEntry `%s` for menu `%s`>" % (
            self.__view_name__, self.manager.__name__)

    def default_namespace(self):
        namespace = {}
        namespace['context'] = self.context
        namespace['request'] = self.request
        namespace['view'] = self.view
        namespace['entry'] = self
        namespace['menu'] = self.manager
        return namespace

    def namespace(self):
        return {}

    def update(self):
        pass

    @property
    def selected(self):
        if self.__name__ == self.view.__name__:
            return True
        return False

    @property
    def url(self):
        return str("%s/%s" % (self.manager.context_url, self.__name__))

    @property
    def title(self):
        return grokcore.viewlet.title.bind(default=self.__name__).get(self)

    @property
    def permission(self):
        return grokcore.viewlet.require.bind().get(self)

    @property
    def description(self):
        return grokcore.viewlet.description.bind(default=None).get(self)

    def render(self):
        template = getattr(self, 'template', None)
        if template is None:
            template = getMultiAdapter((self, self.request), IPageTemplate)
        return template()


class MenuTemplate(PageTemplate):
    view(IMenu)
    template = grokcore.view.PageTemplateFile("templates/menu.pt")


class EntryTemplate(PageTemplate):
    view(IMenuEntry)
    template = grokcore.view.PageTemplateFile("templates/entry.pt")
