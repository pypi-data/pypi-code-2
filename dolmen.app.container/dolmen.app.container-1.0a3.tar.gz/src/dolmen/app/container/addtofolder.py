# -*- coding: utf-8 -*-

import grok
import dolmen.content

from dolmen.app import security, layout
from zope.component import getUtilitiesFor, queryMultiAdapter
from zope.container.constraints import checkFactory
from zope.container.interfaces import IContainer
from zope.security.checker import CheckerPublic
from zope.security.management import checkPermission

grok.templatedir("templates")


class AddMenu(grok.Viewlet):
    grok.order(60)
    grok.view(layout.IDisplayView)
    grok.context(IContainer)
    grok.require(security.CanAddContent)
    grok.viewletmanager(layout.AboveBody)

    def checkFactory(self, name, factory):
        """Verifies the factory and the right of the logged user against
        the container and the required permission of the content type.
        """
        if not checkFactory(self.context, name, factory):
            return False

        permission = dolmen.content.require.bind().get(factory.factory)
        if permission == 'zope.Public':
            permission = CheckerPublic
        return checkPermission(permission, self.context)

    def update(self):
        """Gathers the factories allowed for the context container
        in a list of factories information useable by the template.
        """
        self.factories = []
        self.contexturl = self.view.url(self.context)

        for name, factory in getUtilitiesFor(dolmen.content.IFactory):
            # We iterate and check the factories
            if self.checkFactory(name, factory):
                factory_class = factory.factory
                icon_view = queryMultiAdapter(
                    (factory_class, self.request), name="icon")
                self.factories.append(dict(
                    name=name,
                    icon= icon_view and icon_view() or None,
                    id=name.replace(".", "-"),
                    url='%s/++add++%s' % (self.contexturl, name),
                    title=factory_class.__content_type__,
                    description=(factory.description or
                                 factory_class.__doc__),
                    ))
